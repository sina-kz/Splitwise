import datetime
import random
import string

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
import threading
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.urls import reverse
from .models import User, Friend, Bunch, Expense, Pay
from django.core.mail import send_mail
from Utils.Algorithms.split_algorithm import minCashFlow
import re


def main_page(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    else:
        print("yes")
        return redirect("/login/")


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


@login_required(login_url='login_page')
def dashboard(request):
    if not request.user.is_staff:
        return render(request, "dashboard.html", {"username": request.user.username})
    else:
        return render(request, "admin_dashboard.html", {"username": request.user.username})


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


@login_required(login_url='login_page')
def invite_view(request):
    if request.method == "POST":
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


@login_required(login_url='login_page')
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


@login_required(login_url='login_page')
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


@login_required(login_url='login_page')
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


@login_required(login_url='login_page')
def friends_list(request):
    current_user = request.user
    user_friends = Friend.objects.filter(user=current_user)
    list_of_friends = list(user_friends)
    friends = []
    for friend in list_of_friends:
        friends.append(friend.friend)
    context = {"friends": friends}
    return render(request, "list_of_friends.html", context)


@login_required(login_url='login_page')
def groups_list(request):
    current_user = request.user
    user_groups = Bunch.objects.filter(users=current_user)
    list_of_groups = list(user_groups)
    groups = []
    for group in list_of_groups:
        group_users = list(group.users.all())

        num_of_users = len(list(group.users.all()))
        graph = [[0 for i in range(num_of_users)] for j in range(num_of_users)]

        expenses = list(Expense.objects.filter(bunch=group))
        for i in range(len(group_users)):
            print(group_users[i].username)
        for expense in expenses:
            for i in range(len(group_users)):
                pay = list(Pay.objects.filter(expense=expense, payer=group_users[i]))
                main_payer = expense.main_payer
                index_of_main_payer = None

                if main_payer.username == group_users[i].username:
                    continue

                for j in range(len(group_users)):
                    if main_payer.username == group_users[j].username:
                        index_of_main_payer = j
                        break
                if len(pay) != 0:
                    amount = pay[0].amount
                    graph[i][index_of_main_payer] += amount
        final_graph = minCashFlow(graph)
        user_index = None
        for i in range(len(group_users)):
            if group_users[i].username == current_user.username:
                user_index = i
                break
        debt = int(sum(final_graph[user_index]))
        groups.append((group, debt))
    context = {"groups": groups}
    return render(request, "list_of_groups.html", context)


@login_required(login_url='login_page')
def group_details(request, group_name):
    group = Bunch.objects.get(token_str=group_name)
    group_users = list(group.users.all())
    expenses = list(Expense.objects.filter(bunch=group))
    context = {"group_users": group_users,
               "group": group,
               "token": group_name,
               "expenses": expenses}

    num_of_users = len(list(group.users.all()))
    graph = [[0 for i in range(num_of_users)] for j in range(num_of_users)]

    expenses = list(Expense.objects.filter(bunch=group))
    for i in range(len(group_users)):
        print(group_users[i].username)
    for expense in expenses:
        for i in range(len(group_users)):
            pay = list(Pay.objects.filter(expense=expense, payer=group_users[i]))
            main_payer = expense.main_payer
            index_of_main_payer = None

            if main_payer.username == group_users[i].username:
                continue

            for j in range(len(group_users)):
                if main_payer.username == group_users[j].username:
                    index_of_main_payer = j
                    break
            if len(pay) != 0:
                amount = pay[0].amount
                graph[i][index_of_main_payer] += amount
    print(graph)
    print(minCashFlow(graph))
    return render(request, "group_details.html", context)


@login_required(login_url='login_page')
def select_pay_method(request, token):
    if request.method == "GET":
        return render(request, "select_pay_method.html", {"token": token})
    # elif request.method == "POST":
    #     form_data = request.POST
    #     print(form_data)


@login_required(login_url='login_page')
def add_expense(request, token, type_of_calculate):
    if request.method == "GET":
        bunch_of_user = list(Bunch.objects.filter(token_str=token))
        users = list(bunch_of_user[0].users.all())
        return render(request, "add_expense.html", {"users": users, "type_of_calculate": type_of_calculate})
    elif request.method == "POST":
        form_data = request.POST
        form_data_files = request.FILES
        bunch = list(Bunch.objects.filter(token_str=token))[0]
        total_amount = int(form_data.get('totalAmount'))
        subject = form_data.get('subject')
        description = form_data.get('description')
        main_payer = form_data.get('payer')
        main_payer_user = list(User.objects.filter(username=main_payer))[0]
        image = form_data_files.get('expenseImage')

        expense = Expense.objects.create(main_payer=main_payer_user, bunch=bunch, amount=total_amount, subject=subject,
                                         description=description, picture=image,
                                         token_str=''.join(
                                             random.choice(string.ascii_uppercase + string.digits) for _ in range(10)))
        expense.save()

        if type_of_calculate == "1":
            print(list(bunch.users.all()))
            num_of_users = len(list(bunch.users.all()))
            share_of_each_user = total_amount / num_of_users
            for user in list(bunch.users.all()):
                pay = Pay.objects.create(expense=expense, payer=user, amount=share_of_each_user)
                pay.save()
        elif type_of_calculate == "2":
            for user in list(bunch.users.all()):
                if form_data.get(user.username) == "":
                    share_of_user = 0
                else:
                    share_of_user = float(form_data.get(user.username))
                pay = Pay.objects.create(expense=expense, payer=user, amount=share_of_user)
                pay.save()
        elif type_of_calculate == "3":
            for user in list(bunch.users.all()):
                if form_data.get(user.username) == "":
                    percent_of_user = 0
                else:
                    percent_of_user = float(form_data.get(user.username))
                share_of_user = percent_of_user * total_amount / 100
                pay = Pay.objects.create(expense=expense, payer=user, amount=share_of_user)
                pay.save()

        return redirect(reverse("group_details", args=(token,)))


@login_required(login_url='login_page')
def remove_group(request, token):
    current_user = request.user
    bunch_of_user = list(Bunch.objects.filter(token_str=token))
    bunch_of_user[0].users.remove(current_user)

    if len(bunch_of_user[0].users.all()) == 0:
        Bunch.objects.filter(token_str=token).delete()

    return redirect("/groups-list/")


@login_required(login_url='login_page')
def financial_report(request):
    current_user = request.user
    user_pays = list(Pay.objects.filter(payer=current_user))
    expenses = []
    for pay in user_pays:
        expense = pay.expense
        share = int(pay.amount)
        expenses += [(expense, share)]
    context = {"expenses": expenses}
    return render(request, 'expense_report.html', context)


def expense_detail(request, group_token, expense_token):
    expense = list(Expense.objects.filter(token_str=expense_token))[0]
    bunch = list(Bunch.objects.filter(token_str=group_token))[0]
    context = {"expense": expense, "bunch": bunch}
    return render(request, "expense_detail.html", context)
