from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here

class User(AbstractUser):
    phone_number = models.CharField(max_length=100)
    address = models.CharField(max_length=200)


class Friend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name='friends')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False,
                               related_name='knowns')

    def __str__(self):
        return f"{self.user.username} -> {self.friend.username}"


class Bunch(models.Model):
    users = models.ManyToManyField(User, null=False, blank=False, related_name="%(class)s_members")
    name = models.CharField(max_length=150, unique=False, blank=False, null=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False,
                                related_name='%(class)s_creator')

    def __str__(self):
        return self.name


class Expense(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False,
                                related_name='%(class)s_creator')
    payers = models.ManyToManyField(User, blank=False, null=False, related_name="%(class)s_payers")
    subject = models.CharField(max_length=150, blank=True, null=True, verbose_name='subject')
    description = models.TextField(blank=True, unique=False, null=True, verbose_name='description')
    location = models.TextField(blank=True, unique=False, null=True, verbose_name='location')
    amount = models.FloatField(max_length=15, verbose_name="amount")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name='date')
    picture = models.ImageField(upload_to="sina", blank=True, null=True, verbose_name='picture')
