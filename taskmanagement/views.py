from arrow import now
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from taskmanagement.models import Task, UserTask
from .forms import AdminLoginForm, ForgotPasswordForm, LoginForm, RegistrationForm, ResetPasswordForm, TaskForm
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login , logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator  # --> for token generator
from django.utils.http import urlsafe_base64_encode ,urlsafe_base64_decode# --> for generate a 
from django.utils.encoding import force_bytes # --> for encode a string
from django.contrib.sites.shortcuts import get_current_site # --> for get current site
from django.template.loader import render_to_string # --> for render a template to str
from django.core.mail import send_mail # --> for send a mail
from django.contrib.auth.decorators import login_required 

def register(request):
    
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Set username to email
            user.username = form.cleaned_data['email']
            
            #password Hashing
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request,'Registered Successfully! Now you can login')
            return redirect('login')
        
        
    return render(request,'register.html',{'form':form})

def login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            user = authenticate(request,username=email,password=password)
            if user is not None:
                print("user:",user.last_name) #--> gives the username eg:karthi39
            
            if user is not None:
                auth_login(request,user)
                print('Successfully Login!')
                messages.success(request,'Login Successfully!')
                return redirect('user')
            else:
                messages.error(request,'Invalid credentials. Please try again.')
                
    return render(request,'login.html',{'form':form})


def adminlogin(request):
    form = AdminLoginForm()
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        
        if form.is_valid():
            
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            user = authenticate(request,username=email,password=password)
            if user is not None and user.is_staff:
                auth_login(request,user)
                print('Successfully Login!')
                messages.success(request,'Login Successfully!')
                return redirect('admin')
            else:
        
                messages.error(request,'Invalid credentials or you are not an admin.')
                
    return render(request,'adminlogin.html',{'form':form})

@login_required(login_url='login')
def logout(request):
    print(f'Successfully Logout!:{request.user}')
    auth_logout(request)
    messages.success(request,'Logged out successfully!')
    return redirect(reverse('login'))

@login_required(login_url='adminlogin')
def adminlogout(request):   
    print(f'Successfully Logout!:{request.user}')
    auth_logout(request)
    messages.success(request,'Logged out successfully!')
    return redirect(reverse('adminlogin'))

def forgot_password(request):
    form = ForgotPasswordForm()
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            user = User.objects.get(email=email)
            
            token = default_token_generator.make_token(user) # --> create a token for user to reset password (one time use)
            uid = urlsafe_base64_encode(force_bytes(user.id)) # --> encode the user id to base64 gives eg: b'cGFzc3dvcmQx' in short gives the base64 str
            current_site =  get_current_site(request) 
            domain = current_site.domain #--> get the domain name eg: 127.0.0.1:8000
            
            #mail summary :
            subject = "Reset Password Requested"
            message  = render_to_string('reset_password_email.html',{
                'domain':domain,
                'uid':uid,
                'token':token
            }) 
            
            send_mail(subject,message,from_email=None,recipient_list=[email])
            messages.success(request,'Email has been sent!')
            
            return redirect('login')
            
            
    return render(request,'forgot_password.html', {'form': form})


def reset_password(request, uidb64, token):
    form = ResetPasswordForm()
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            
            try:
                uid = urlsafe_base64_decode(uidb64).decode() # --> decode the base64 string to get the user id
                user = User.objects.get(id=uid) # --> get the user object using the decoded user id
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None
            
            if user is not None and default_token_generator.check_token(user, token):
                user.set_password(new_password) # --> set the new password for the user
                user.save()
                messages.success(request,'Password reset successfully! Now you can login with new password')
                return redirect('login')
            else:
                messages.error(request,'The reset password link is invalid or has expired.')
                
    return render(request,'reset_password.html',{'form':form})


@login_required(login_url='login')
def user(request):
    user_tasks = UserTask.objects.filter(user_id=request.user).select_related('task').order_by('id')
    
    # Filter out soft-deleted tasks and calculate statistics
    active_user_tasks = user_tasks.filter(task__deleted_at__isnull=True)
    
    total_tasks = active_user_tasks.count()
    pending_count = active_user_tasks.filter(status='pending').count()
    in_progress_count = active_user_tasks.filter(status='in_progress').count()
    completed_count = active_user_tasks.filter(status='completed').count()
    
    # Calculate completion percentage
    completion_percentage = round((completed_count / total_tasks * 100), 1) if total_tasks > 0 else 0
    
    stats = {
        'total_tasks': total_tasks,
        'pending': pending_count,
        'in_progress': in_progress_count,
        'completed': completed_count,
        'completion_percentage': completion_percentage,
    }
    
    return render(request,'user.html',{'usertasks':user_tasks, 'stats':stats})
    
@login_required(login_url='adminlogin')
def admin(request):
    
    form = TaskForm()
    
    # Handle task creation form submission
    if request.method == 'POST':
        print("Received POST request for task creation")
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            
            for user in User.objects.all():
                if user != request.user:
                    try:
                        UserTask.objects.create(user=user, task=task)
                    except Exception as e:
                        print(f"Error creating UserTask for user {user.id} and task {task.id}: {e}")
            
            return redirect('admin')
        
    
    # --------------------ADMIN DASHBOARD STATS CALCULATION--------------------
    # For admin dashboard stats and user stats calculation (excluding soft-deleted tasks)
    
    # Get active (non-deleted) tasks
    active_tasks = Task.objects.filter(deleted_at__isnull=True).order_by('id')
    
    total_tasks = active_tasks.count()
    
    # Get all UserTasks for these active tasks
    all_user_tasks = UserTask.objects.filter(task__deleted_at__isnull=True)
    completed_count = all_user_tasks.filter(status='completed').count()
    
    # Calculate overall completion percentage
    total_user_tasks = all_user_tasks.count()
    completion_percentage = round((completed_count / total_user_tasks * 100), 1) if total_user_tasks > 0 else 0
    
    stats = {
        'total_tasks': total_tasks,
        'completion_percentage': completion_percentage,
    }
    
    
    # --------------------USER SHOWING AND STATS CALCULATION--------------------
    # Show user stats for all users (excluding the admin and soft-deleted tasks)
    
    # Always calculate user stats (will be populated by JavaScript, always default to hidden)
    if request.method == 'GET':
        print("Calculating user stats...")
        users_with_stats = []
        all_users = User.objects.exclude(id=request.user.id).order_by('first_name')
        
        for user in all_users:
            user_tasks = UserTask.objects.filter(user=user, task__deleted_at__isnull=True)
            users_with_stats.append({
                'user': user,
                'total_tasks': user_tasks.count(),
                'pending': user_tasks.filter(status='pending').count(),
                'in_progress': user_tasks.filter(status='in_progress').count(),
                'completed': user_tasks.filter(status='completed').count(),
            })
    
    return render(request,'admin.html',{
        'form':form,
        'tasks':active_tasks,
        'stats':stats,
        'show_users': False,
        'users_with_stats': users_with_stats
    })

@login_required(login_url='adminlogin')
@require_POST
def edittask(request,task_id):

    task = get_object_or_404(Task, id=task_id)
    task.title = request.POST.get('title')
    task.description = request.POST.get('description')
    task.task_link = request.POST.get('task_link')
    task.updated_at = now().datetime
    task.save()
    messages.success(request,'Task updated Successfully!')
    
    return redirect('admin')

@login_required(login_url='adminlogin')
@require_POST
def deletetask(request,task_id):
    taskdelete = get_object_or_404(Task, id=task_id)
    taskdelete.deleted_at = now().datetime
    taskdelete.save()
    messages.success(request,'Task deleted Successfully!')
    
    return redirect('admin')

@login_required(login_url='login')
@require_POST
def completetask(request,task_id):
    usertask = get_object_or_404(UserTask, user=request.user, task_id=task_id)
    usertask.is_completed = True
    usertask.completed_at = now().datetime
    usertask.save()
    messages.success(request,'Task marked as completed!')
    
    return redirect('user')


@login_required(login_url='login')
@require_POST
def updatetaskstatus(request, task_id):
    user_task = UserTask.objects.get(id=task_id, user=request.user)

    new_status = request.POST.get("status")

    if new_status in ['pending', 'in_progress', 'completed']:
        user_task.status = new_status
        user_task.updated_at = now().datetime
        user_task.save()
    
    if new_status == 'completed':
        user_task.completed_at = now().datetime
        user_task.save()

    return redirect('user')