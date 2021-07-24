from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

UserAdmin.fieldsets += (
    ("Added Field", {'fields': ('phone_number', 'address')}),
)

# Register your models here.
admin.site.register(User, UserAdmin)
