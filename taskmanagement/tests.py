from django.test import TestCase

# Create your tests here.
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())