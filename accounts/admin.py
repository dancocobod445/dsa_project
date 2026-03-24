from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'role', 'student_id', 'department']
    list_filter = ['role']
    fieldsets = UserAdmin.fieldsets + (
        ('Library Info', {'fields': ('role', 'student_id', 'department')}),
    )
