from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string


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
    token_str = models.CharField(max_length=10, default=''.join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(10)))

    def __str__(self):
        return self.name


class Expense(models.Model):
    main_payer = models.ForeignKey(User, on_delete=models.CASCADE, null=True,
                                   related_name='%(class)s_main_payer')
    bunch = models.ForeignKey(Bunch, on_delete=models.CASCADE, null=True,
                              related_name='%(class)s_bunch')
    subject = models.CharField(max_length=150, blank=True, null=True, verbose_name='subject')
    description = models.TextField(blank=True, unique=False, null=True, verbose_name='description')
    location = models.TextField(blank=True, unique=False, null=True, verbose_name='location')
    amount = models.FloatField(max_length=15, verbose_name="amount")
    date = models.CharField(max_length=20, blank=True, null=True, verbose_name='date')
    picture = models.ImageField(upload_to="images", blank=True, null=True, verbose_name='picture',
                                default="images/no_image.png")
    token_str = models.CharField(max_length=10, default=''.join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(10)))

    def __str__(self):
        return f"{self.main_payer.username} -> {self.bunch.name}"


class Pay(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, null=True)
    payer = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    amount = models.FloatField(max_length=15, verbose_name="amount")

    def __str__(self):
        return f"{self.payer.username} -> {self.amount}"
