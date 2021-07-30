from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .models import Friend
from .models import Bunch
from .models import Expense

UserAdmin.fieldsets += (
    ("Added Field", {'fields': ('phone_number', 'address')}),
)

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Friend)
admin.site.register(Bunch)
admin.site.register(Expense)

