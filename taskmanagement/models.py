from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    task_link = models.URLField()
    due_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.title
    
    
STATUS_CHOICES = [
    ('pending', 'Start Task'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
]
 
class UserTask(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    submitted_proof = CloudinaryField('image', null=True, blank=True)
    gitlink = models.URLField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.task.title} - "