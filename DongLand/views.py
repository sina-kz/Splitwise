import datetime
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.http import HttpResponse

from .models import User
import re


def main_page(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
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
        return render(request, "dashboard.html")
    else:
        return redirect('/login/')