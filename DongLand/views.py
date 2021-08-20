import datetime
import random
import string

import numpy as np
from django.contrib import messages
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
from django import template


def main_page(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    else:
        return redirect("/login/")


def login_view(request):
    list(messages.get_messages(request))
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
            try:
                remember_me = form_data["rememberMe"]
            except:
                remember_me = False
            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)
            login(request, user)
            messages.success(request, "message")
            return redirect('/dashboard/')
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
            messages.success(request, "ثبت نام با موفقیت انجام شد")
            return redirect("/login/")
        else:
            data["error"] = error
            return render(request, "auth-sign-up.html", context=data)

    return render(request, "auth-sign-up.html")


def logout_view(request):
    logout(request)
    return redirect('/login/')


@login_required(login_url='login_page')
def dashboard(request):
    list(messages.get_messages(request))
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
        error = {}
        users_list = list(User.objects.all())
        for user in users_list:
            if user.email == email_url:
                error['email'] = f'ایمیل {email_url} قبلا در سامانه ثبت شده است'
        if len(error) == 0:
            recievers = [email_url, ]
            send_mail(subject=email_subject, message=email_body, from_email=email_from, recipient_list=recievers)
            return render(request, "invite_user.html", {"message": "message"})
        else:
            return render(request, "invite_user.html", {"error": error})
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
            messages.success(request, "message")
            return redirect(reverse("add_users", args=(group_name,)))
    data = {}
    data["error"] = error
    return render(request, "create_group.html", data)


@login_required(login_url='login_page')
def add_users(request, group_name):
    current_user = request.user
    group = Bunch.objects.get(token_str=group_name)
    group_users = list(group.users.all())

    has_access = False
    for user in group_users:
        if current_user.username == user.username:
            has_access = True
            break
    if not has_access:
        return render(request, "bad_access.html")

    list(messages.get_messages(request))
    error = {}
    if request.method == "POST":
        form_data = request.POST
        group = Bunch.objects.get(token_str=group_name)
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
            return render(request, "add_users_to_group.html", {"message": "message"})
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
            return render(request, "add_friend.html", {"message": "message"})
        else:
            return render(request, "add_friend.html", data)
    return render(request, "add_friend.html", {})


@login_required(login_url='login_page')
def friends_list(request):
    list(messages.get_messages(request))
    current_user = request.user
    user_friends = Friend.objects.filter(user=current_user)
    list_of_friends = list(user_friends)
    friends = []
    for friend in list_of_friends:
        friends.append(friend.friend)
    context = {"friends": friends}
    return render(request, "list_of_friends.html", context)

@login_required(login_url='login_page')
def show_users_admin(request):
    list(messages.get_messages(request))
    current_user = request.user
    users = User.objects.all()
    list_of_users = list(users)
    
    context = {"friends": list_of_users}
    return render(request, "admin_show_users.html", context)

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
                    graph[i][index_of_main_payer] += int(amount)
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
def groups_list_admin(request):
    current_user = request.user
    if not current_user.is_staff:
        return HttpResponse("you don't have access")

    user_groups = Bunch.objects.all()
    list_of_groups = list(user_groups)
    groups = []
    for group in list_of_groups:
        group_users = list(group.users.all())

        num_of_users = len(list(group.users.all()))
        print(num_of_users)
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
                    graph[i][index_of_main_payer] += int(amount)
        final_graph = minCashFlow(graph)
       
        groups.append(group)
    context = {"groups": groups}
    return render(request, "admin_list_of_groups.html", context)

@login_required(login_url='login_page')
def group_details(request, group_name):
    list(messages.get_messages(request))
    current_user = request.user
    group = Bunch.objects.get(token_str=group_name)
    group_users = list(group.users.all())
    expenses = list(Expense.objects.filter(bunch=group))
    amounts = []

    has_access = False
    for user in group_users:
        if current_user.username == user.username:
            has_access = True
            break
    if not has_access:
        return render(request, "bad_access.html")

    for expense in expenses:
        pay = list(Pay.objects.filter(expense=expense, payer=current_user))
        if len(pay) != 0:
            amounts.append(int(pay[0].amount))

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
                graph[i][index_of_main_payer] += int(amount)
    print(graph)
    result = (minCashFlow(graph))
    result = np.array(result)
    rows, cols = np.where(result != 0)
    print(result)

    debtors = []
    creditors = []
    amount_of_debt = []

    for i in range(len(rows)):
        debtors.append(group_users[rows[i]])
        creditors.append(group_users[cols[i]])
        amount_of_debt.append(int(result[rows[i]][cols[i]]))

    is_admin = False
    if group.creator.username == current_user.username:
        is_admin = True
    else:
        is_admin = False

    context = {"group_users": group_users,
               "group": group,
               "token": group_name,
               "amounts_and_expenses": list(zip(expenses, amounts)),
               "debtor_and_creditor": list(zip(debtors, creditors, amount_of_debt)),
               "is_admin": is_admin,
               "admin": group.creator}

    return render(request, "group_details.html", context)


@login_required(login_url='login_page')
def group_details_admin(request, group_name):
    list(messages.get_messages(request))
    current_user = request.user
    if not current_user.is_staff:
        return HttpResponse("no access")
    group = Bunch.objects.get(token_str=group_name)
    group_users = list(group.users.all())
    expenses = list(Expense.objects.filter(bunch=group))
    amounts = []

    has_access = True
    if not has_access:
        return render(request, "bad_access.html")

    for expense in expenses:
        pay = list(Pay.objects.filter(expense=expense, payer=current_user))
        if len(pay) != 0:
            amounts.append(int(pay[0].amount))

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
                graph[i][index_of_main_payer] += int(amount)
    print(graph)
    result = (minCashFlow(graph))
    result = np.array(result)
    rows, cols = np.where(result != 0)
    print(result)

    debtors = []
    creditors = []
    amount_of_debt = []

    for i in range(len(rows)):
        debtors.append(group_users[rows[i]])
        creditors.append(group_users[cols[i]])
        amount_of_debt.append(int(result[rows[i]][cols[i]]))

    is_admin = False
    if group.creator.username == current_user.username:
        is_admin = True
    else:
        is_admin = False

    context = {"group_users": group_users,
               "group": group,
               "token": group_name,
               "amounts_and_expenses": list(zip(expenses, amounts)),
               "debtor_and_creditor": list(zip(debtors, creditors, amount_of_debt)),
               "is_admin": is_admin,
               "admin": group.creator}

    return render(request, "group_details_admin.html", context)

@login_required(login_url='login_page')
def select_pay_method(request, token):
    current_user = request.user
    group = Bunch.objects.get(token_str=token)
    group_users = list(group.users.all())

    has_access = False
    for user in group_users:
        if current_user.username == user.username:
            has_access = True
            break
    if not has_access:
        return render(request, "bad_access.html")
    if request.method == "GET":
        return render(request, "select_pay_method.html", {"token": token})
    # elif request.method == "POST":
    #     form_data = request.POST
    #     print(form_data)


@login_required(login_url='login_page')
def add_expense(request, token, type_of_calculate):
    current_user = request.user
    group = Bunch.objects.get(token_str=token)
    group_users = list(group.users.all())

    has_access = False
    for user in group_users:
        if current_user.username == user.username:
            has_access = True
            break
    if not has_access:
        return render(request, "bad_access.html")

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
        date = form_data.get('date')
        location = form_data.get('location')

        main_payer_user = list(User.objects.filter(username=main_payer))[0]
        image = form_data_files.get('expenseImage')

        if subject and total_amount and main_payer_user:
            expense = Expense.objects.create(main_payer=main_payer_user, bunch=bunch, amount=total_amount,
                                             subject=subject,
                                             description=description, location=location, date=date,
                                             type_of_calculation=int(type_of_calculate),
                                             token_str=''.join(
                                                 random.choice(string.ascii_uppercase + string.digits) for _ in
                                                 range(10)))
            if image:
                expense.picture = image
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
            messages.info(request, "هزینه با موفقیت ثبت شد")
            return redirect(reverse("group_details", args=(token,)))


@login_required(login_url='login_page')
def remove_group(request, token):
    current_user = request.user
    group = Bunch.objects.get(token_str=token)
    group_users = list(group.users.all())

    has_access = False
    for user in group_users:
        if current_user.username == user.username:
            has_access = True
            break
    if not has_access:
        return render(request, "bad_access.html")

    bunch_of_user = list(Bunch.objects.filter(token_str=token))
    bunch_of_user[0].users.remove(current_user)

    if len(bunch_of_user[0].users.all()) == 0:
        Bunch.objects.filter(token_str=token).delete()

    Expense.objects.filter(bunch=group, main_payer=current_user).delete()
    for expense in list(Expense.objects.filter(bunch=group)):
        Pay.objects.filter(expense=expense, payer=current_user).delete()

    return redirect("/groups-list/")


@login_required(login_url='login_page')
def remove_group_admin(request, token):
    print("remove group")
    current_user = request.user
    if not current_user.is_staff:
        return HttpResponse("no access")
    group = Bunch.objects.get(token_str=token)
    group_users = list(group.users.all())

    has_access = True
    
    if not has_access:
        return render(request, "bad_access.html")

    bunch_of_user = list(Bunch.objects.filter(token_str=token))
    bunch_of_user[0].users.remove(current_user)

    if len(bunch_of_user[0].users.all()) == 0:
        Bunch.objects.filter(token_str=token).delete()

    Expense.objects.filter(bunch=group, main_payer=current_user).delete()
    for expense in list(Expense.objects.filter(bunch=group)):
        Pay.objects.filter(expense=expense, payer=current_user).delete()
    
    Bunch.delete(group)

    return redirect("/admin-groups-list/")


@login_required(login_url='login_page')
def financial_report(request):
    current_user = request.user
    if not current_user.is_staff:
        user_pays = list(Pay.objects.filter(payer=current_user))
        expenses = []
        for pay in user_pays:
            expense = pay.expense
            share = int(pay.amount)
            expenses += [(expense, share, expense.main_payer)]
        context = {"expenses": expenses}
        return render(request, 'expense_report.html', context)
    else:
        all_expenses = list(Expense.objects.all())
        expenses = []
        for expense in all_expenses:
            expenses += [(expense, int(expense.amount), expense.main_payer)]
        context = {"expenses": expenses}
        return render(request, 'expense_report_admin.html', context)


def expense_detail(request, group_token, expense_token):
    current_user = request.user
    group = Bunch.objects.get(token_str=group_token)
    group_users = list(group.users.all())

    has_access = False
    for user in group_users:
        if current_user.username == user.username:
            has_access = True
            break
    if not has_access:
        return render(request, "bad_access.html")

    expense = list(Expense.objects.filter(token_str=expense_token))[0]
    bunch = list(Bunch.objects.filter(token_str=group_token))[0]
    context = {"expense": expense, "bunch": bunch}
    if not current_user.is_staff:
        return render(request, "expense_detail.html", context)
    else:
        return render(request, "expense_detail_admin.html", context)


def remove_user(request, token, username):
    current_user = request.user
    group = Bunch.objects.get(token_str=token)

    has_access = False
    if current_user.username == group.creator.username:
        has_access = True
    if not has_access:
        return render(request, "bad_access.html")

    bunch = list(Bunch.objects.filter(token_str=token))[0]
    user = User.objects.get(username=username)
    bunch.users.remove(user)

    Expense.objects.filter(bunch=group, main_payer=user).delete()
    for expense in list(Expense.objects.filter(bunch=group)):
        Pay.objects.filter(expense=expense, payer=user).delete()

    messages.success(request, f"کاربر {username} با موفقیت حذف گردید")
    return redirect(reverse("group_details", args=(token,)))


def remove_friend(request, username):
    current_user = request.user
    try:
        user = User.objects.get(username=username)
        Friend.objects.get(user=current_user, friend=user).delete()
        Friend.objects.get(user=user, friend=current_user).delete()
        messages.success(request, f'کاربر {username} با موفقیت از دوستان شما حذف شد')
        return redirect("/friends-list/")
    except Friend.DoesNotExist:
        return render(request, "bad_access.html")

def remove_user_admin(request, username):
    current_user = request.user
    try:
        if username == current_user.username:
            return render(request, "bad_access.html")
        User.objects.get(username=username).delete()
        
        messages.success(request, f'کاربر {username} با موفقیت از لیست کاربران حذف شد')
        return redirect(reverse('show_users_admin'))
    except user.DoesNotExist:
        return render(request, "bad_access.html")

def page_not_found(request):
    return render(request, "page_not_found.html")


def edit_expense(request, group_token, expense_token, type_of_calculate):
    if request.method == "GET":
        expense = list(Expense.objects.filter(token_str=expense_token))[0]
        bunch_of_user = list(Bunch.objects.filter(token_str=group_token))
        users = list(bunch_of_user[0].users.all())
        pays = list(Pay.objects.filter(expense=expense))
        user_and_amounts = []
        for user in users:
            for pay in pays:
                if user.username == pay.payer.username:
                    user_and_amounts.append((user, pay.amount, int(pay.amount) / int(expense.amount)))

        context = {"totalAmount": int(expense.amount),
                   "subject": expense.subject,
                   "description": expense.description,
                   "location": expense.location,
                   "date": expense.date,
                   "main_payer": expense.main_payer,
                   "users": users,
                   "type_of_calculate": type_of_calculate,
                   "image": expense.picture,
                   "user_and_amounts": user_and_amounts}
        return render(request, "edit_expense.html", context=context)
    elif request.method == "POST":
        expense = list(Expense.objects.filter(token_str=expense_token))[0]
        bunch = list(Bunch.objects.filter(token_str=group_token))[0]
        Pay.objects.filter(expense=expense).delete()

        form_data = request.POST
        form_data_files = request.FILES
        total_amount = int(form_data.get('totalAmount'))
        subject = form_data.get('subject')
        description = form_data.get('description')
        main_payer = form_data.get('payer')
        date = form_data.get('date')
        location = form_data.get('location')

        main_payer_user = list(User.objects.filter(username=main_payer))[0]
        image = form_data_files.get('editExpenseImage')
        expense.subject = subject
        expense.description = description
        expense.amount = total_amount
        expense.date = date
        expense.location = location
        expense.main_payer = main_payer_user
        if image:
            expense.picture = image
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
        messages.info(request, "هزینه با موفقیت ویرایش شد")

        return redirect(f"/groups/{group_token}/")


def user_profile(request):
    list(messages.get_messages(request))
    return render(request, "user_profile.html", {"user": request.user})

def user_profile_admin(request, username):
    list(messages.get_messages(request))
    user = User.objects.get(username=username)
    return render(request, "user_profile_admin.html", {"user": user})

def delete_user(request):
    if request.method == "POST":
        form_data = request.POST
        current_user = request.user
        user_name = form_data["username"]
        password = form_data["pass"]
        user = authenticate(username=user_name, password=password)
        data = {}
        error = {}
        if user is None or user_name != request.user.username:
            error["username"] = "نام‌کاربری یا رمز عبور اشتباه است"
            data["error"] = error
            return render(request, "delete_user.html", context=data)
        else:
            User.objects.filter(username=user_name).delete()
            return redirect('/logout/')
    return render(request, "delete_user.html")


def delete_expense(request, group_token, expense_token):
    Expense.objects.filter(token_str=expense_token).delete()
    return redirect(f"/groups/{group_token}/")


def change_password(request):
    if request.method == "POST":
        form_data = request.POST
        current_user = request.user
        old_password = form_data["old_pass"]
        new_password = form_data["new_pass"]
        new_password2 = form_data["new_pass2"]
        user = authenticate(username=request.user.username, password=old_password)
        data = {}
        error = {}
        if old_password == "" or new_password == "" or new_password2 == "":
            error["empty_field"] = "تمامی فیلدها باید پر شوند"
        elif user is None:
            error["password"] = "رمز عبور فعلی صحیح نیست"
        elif new_password != new_password2:
            error["new_pass"] = "رمز عبور جدید و تکرار آن مطابقت ندارند"
        if len(error) != 0:
            data["error"] = error
            return render(request, "change_password.html", data)
        else:
            user = User.objects.get(username=request.user.username)
            user.set_password(new_password)
            user.save()
            login(request, user)
            messages.success(request, "رمز عبور با موفقیت تغییر کرد")
            return redirect('/view-profile/')
    return render(request, "change_password.html")
