from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Library Admin'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    student_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    department = models.CharField(max_length=100, blank=True)

    def is_admin(self):
        return self.role == 'admin'

    def is_student(self):
        return self.role == 'student'

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"
