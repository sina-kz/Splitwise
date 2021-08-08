import datetime
import random
import string

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse
import threading
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.urls import reverse
from .models import User, Friend, Bunch, Expense
from django.core.mail import send_mail
import re


def main_page(request):
    if request.user.is_authenticated:
        if not request.user.is_staff:
            return redirect('/dashboard/')
        else:
            return redirect('/administrator/')
    else:
        return redirect('/login/')


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/dashboard/")
    if request.method == 'POST':
        form_data = request.POST
        user_name = form_data["user_name"]
        password = form_data["password"]
        user = authenticate(username=user_name, password=password)

        data = {}
        error = {}
        if user is None:

            error["username"] = "نام‌کاربری یا رمز عبور اشتباه است"
            data["error"] = error
            data["username"] = user_name
            return render(request, "auth-sign-in.html", context=data)
        else:

            login(request, user)
            print(user.is_staff)
            return redirect('/dashboard')
            # TODO write pannel
            # return HttpResponse("successful login")

    return render(request, "auth-sign-in.html")


def register_view(request):
    if request.method == "POST":
        form_data = request.POST
        username = form_data.get('username')
        firstname = form_data.get('firstname')
        lastname = form_data.get('lastname')
        phone_number = form_data.get('phone_number')
        email = form_data.get('email')
        password = form_data.get('password')
        password2 = form_data.get('password2')

        users = User.objects.all()

        data = {}
        error = {}

        if password != password2:
            error["password"] = "رمز های عبور یکسان نمی باشند!"

        try:
            user = User.objects.get(username=username)
            error["username"] = "نام کاربری وارد شده تکراری می باشد!"
        except User.DoesNotExist:
            pass

        try:
            user = User.objects.get(phone_number=phone_number)
            error["phone_number"] = "شماره تلفن وارد شده تکراری می باشد!"
        except User.DoesNotExist:
            pass

        if not re.match("^09\d{9}", phone_number):
            error["invalid_phone_number"] = "شماره تلفن وارد شده صحیح نمی باشد!"

        if len(error) == 0:
            user = User.objects.create_user(first_name=firstname, last_name=lastname, phone_number=phone_number,
                                            email=email,
                                            password=password2,
                                            username=username)
            user.save()
            return redirect("/login")
        else:
            data["error"] = error
            return render(request, "auth-sign-up.html", context=data)

    return render(request, "auth-sign-up.html")


def logout_view(request):
    logout(request)
    return redirect('/login/')


def dashboard(request):
    if request.user.is_authenticated:
        if not request.user.is_staff:
            return render(request, "dashboard.html")
        else:
            return render(request, "admin_dashboard.html")
    else:
        return redirect('/login/')


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


def invite_view(request):
    print(6666)
    if request.method == "POST":
        print(5555)
        data = request.POST
        email_url = data['email']
        email_subject = 'Invitation mail from Dongland'
        email_body = render_to_string('invite.html', {
            'user': request.user,
            'url': 'http://localhost/register'
        })
        email_from = settings.EMAIL_HOST_USER
        recievers = [email_url, ]
        send_mail(subject=email_subject, message=email_body, from_email=email_from, recipient_list=recievers)
        return redirect('/dashboard/')
    return render(request, "invite_user.html")


def add_group(request):
    error = {}
    if request.method == "POST":
        form_data = request.POST
        group_name = form_data.get('groupname')
        if group_name == "":
            error["group_name"] = "نام گروه نباید خالی باشد."
        print(error)
        if len(error) == 0:
            group = Bunch.objects.create(name=group_name, creator=request.user, token_str=''.join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(10)))
            group_name = group.token_str
            print(group_name)
            group.users.add(request.user)
            group.save()
            return redirect(reverse("add_users", args=(group_name,)))
    data = {}
    data["error"] = error
    return render(request, "create_group.html", data)


def add_users(request, group_name):
    error = {}
    if request.method == "POST":
        form_data = request.POST
        group = Bunch.objects.get(token_str=group_name, creator=request.user)
        user = None
        user_exist = True
        group_user = form_data.get('groupusers')
        if group_user == "":
            error["group_user"] = "نام کاربر نباید خالی باشد."
        else:
            try:
                user = User.objects.get(username=group_user)
            except User.DoesNotExist:
                error["no_user"] = "کاربر " + group_user + " در سامانه وجود ندارد."
                user_exist = False
            user_friends = Friend.objects.filter(user=request.user)
            list_of_friends = [friend.friend for friend in user_friends]
            if user_exist:
                if user == request.user:
                    error["same_user"] = "شما قبلا به گروه اضافه شده‌اید."
                elif user not in list_of_friends:
                    error["friendship"] = "کاربر " + group_user + " از دوستان شما نیست."
                elif user in list(group.users.all()):
                    error["existed"] = "کاربر " + group_user + " قبلا به گروه اضافه شده است."
        data = {"error": error}
        if len(error) == 0:
            group.users.add(user)
            group.save()
            return redirect(reverse("add_users", args=(group_name,)))
        else:
            return render(request, "add_users_to_group.html", data)
    return render(request, "add_users_to_group.html", {})


def add_friend(request):
    error = {}
    if request.method == "POST":
        form_data = request.POST
        username = form_data.get('friend')
        user = None
        if username == "":
            error["username"] = "نام کاربر نباید خالی باشد."
        else:
            previous_friends = list(Friend.objects.filter(user=request.user))
            list_of_friends = [friend.friend for friend in previous_friends]
            user_exist = True
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                error["no_user"] = "کاربر " + username + " در سامانه وجود ندارد."
                user_exist = False
            if user_exist:
                if user == request.user:
                    error["same_user"] = "نمی‌توانید خود را به دوستان اضافه کنید."
                elif user in list_of_friends:
                    error["friendship"] = "کاربر " + username + " قبلا به دوستان شما اضافه شده است."
        data = {"error": error}
        if len(error) == 0:
            Friend.objects.create(user=request.user, friend=user)
            Friend.objects.create(user=user, friend=request.user)
            return redirect('/add-friend/')
        else:
            return render(request, "add_friend.html", data)
    return render(request, "add_friend.html", {})


def friends_list(request):
    current_user = request.user
    user_friends = Friend.objects.filter(user=current_user)
    list_of_friends = list(user_friends)
    friends = []
    for friend in list_of_friends:
        friends.append(friend.friend.username)
    context = {"friends": friends}
    return render(request, "list_of_friends.html", context)


def groups_list(request):
    current_user = request.user
    user_groups = Bunch.objects.filter(users=current_user)
    list_of_groups = list(user_groups)
    groups = []
    for group in list_of_groups:
        groups.append(group.name)
    print(list_of_groups)
    context = {"groups": list_of_groups}
    return render(request, "list_of_groups.html", context)


def delete_groups(request):
    current_user = request.user
    user_groups = Bunch.objects.filter(creator=current_user)
    list_of_groups = list(user_groups)
    groups = []
    for group in list_of_groups:
        groups.append(group.name)
    context = {"groups": groups}
    return render(request, "delete_groups_list.html", context)


def group_details(request, group_name):
    group = Bunch.objects.get(token_str=group_name)
    group_users = list(group.users.all())
    context = {"group_users": group_users,
               "group": group}
    return render(request, "group_details.html", context)


def add_expense(request):
    if request.method == "GET":
        return render(request, "add_expense.html")
    elif request.method == "POST":
        form_data = request.POST
        print(form_data)