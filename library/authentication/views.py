import re
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from order.models import Order
from .models import CustomUser


def login_view(request):
    if request.user.is_authenticated:
        return redirect('authentication:main')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not email or not password:
            return render(request, 'authentication/login.html', {'message_err': 'Email and password required'})
        user = authenticate(request, username=email, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect('authentication:main')
            return render(request, 'authentication/login.html', {'message_err': 'Account disabled'})
        return render(request, 'authentication/login.html', {'message_err': 'Invalid credentials'})

    return render(request, 'authentication/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('authentication:main')

    errors = []
    data = {
        'login': '',
        'firstname': '',
        'middle_name': '',
        'lastname': '',
        'role': '',
    }

    if request.method == 'POST':
        cd = request.POST
        data.update({
            'login': cd.get('login','').strip(),
            'firstname': cd.get('firstname','').strip(),
            'middle_name': cd.get('middle_name','').strip(),
            'lastname': cd.get('lastname','').strip(),
            'role': cd.get('role',''),
        })
        pwd = cd.get('password','')
        pwd2 = cd.get('confirm_password','')

        if not data['login']:
            errors.append("Email is required.")
        else:
            try:
                validate_email(data['login'])
            except ValidationError:
                errors.append("Enter a valid email address.")
            else:
                if CustomUser.objects.filter(email=data['login']).exists():
                    errors.append("This email is already registered.")

        if not pwd or not pwd2:
            errors.append("Both password fields are required.")
        elif pwd != pwd2:
            errors.append("Passwords do not match.")
        else:
            if len(pwd) < 8:
                errors.append("Password must be at least 8 characters long.")
            if not re.search(r"\d", pwd):
                errors.append("Password must contain at least one digit.")
            if not re.search(r"[A-Z]", pwd):
                errors.append("Password must contain at least one uppercase letter.")
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', pwd):
                errors.append("Password must contain at least one special character (e.g. ! @ # $ %).")

        name_pattern = re.compile(r'^([A-Za-z]{2,}|[A-Za-z]\.)$')
        for field, label in (
            ('firstname',   'First name'),
            ('middle_name', 'Middle name'),
            ('lastname',    'Last name'),
        ):
            val = data[field]
            if not val:
                errors.append(f"{label} is required.")
            elif not name_pattern.match(val):
                errors.append(
                    f"{label} must be at least 2 letters, "
                    "or a single letter followed by a dot (e.g. 'A.')."
                )

        if data['role'] not in ('0','1'):
            errors.append("Please select a valid role.")

        if errors:
            return render(request, 'authentication/register.html', {
                'errors': errors,
                'data': data
            })

        try:
            user = CustomUser.objects.create_user(
                email=data['login'],
                password=pwd,
                first_name=data['firstname'],
                last_name=data['lastname'],
                middle_name=data['middle_name'],
                role=int(data['role']),
                is_active=False
            )
        except IntegrityError:
            error = "An error occurred while creating the account. This email may already exist."
            return render(request, 'authentication/register.html', {
                'error': error,
                'data': data
            })

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = request.build_absolute_uri(
            reverse('authentication:activate', args=[uid, token])
        )

        send_mail(
            subject="Activate your BookNest account",
            message=(
                f"Hi {user.first_name},\n\n"
                f"Please click the link below to activate your account:\n\n"
                f"{activation_link}\n\n"
                "If you didn't register, just ignore this email."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return redirect('authentication:activation_sent')

    return render(request, 'authentication/register.html', {
        'data': data
    })


def logout_view(request):
    logout(request)
    return redirect('authentication:login')


@login_required
def main(request):
    return render(request, 'main/main.html')


@login_required
def show_all_users(request):
    if not request.user.is_authenticated or request.user.role != 1:
        return redirect('authentication:login')

    query = request.GET.get('q', '').strip()
    users = CustomUser.objects.all()
    filtered = False

    if query:
        filtered = True
        filters = (
            Q(id__iexact=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

        parts = query.split()
        if len(parts) >= 2:
            first, last = parts[0], parts[1]
            filters |= Q(first_name__icontains=first, last_name__icontains=last)
            filters |= Q(first_name__icontains=last, last_name__icontains=first)

        try:
            filters |= Q(id=int(query))
        except ValueError:
            pass

        users = users.filter(filters).distinct()

        if not users.exists():
            messages.error(request, f"No users found for your search: '{query}'")

    paginator = Paginator(users, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'users/users.html', {
        'page_obj': page_obj,
        'query': query,
        'filtered': filtered
    })


@login_required
def user_detail(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)
    orders = Order.objects.filter(user=user).select_related('book')
    for order in orders:
        order.penalty = order.calculate_penalty()
    return render(request, 'users/user.html', {
        'user': user,
        'orders': orders,
    })


def forgot_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if not CustomUser.objects.filter(email__iexact=email, is_active=True).exists():
                form.add_error('email', "No active account found with that email address.")
                return render(request, 'authentication/forgot_password.html', {
                    'form': form,
                })

            form.save(
                request=request,
                use_https=request.is_secure(),
                from_email=settings.DEFAULT_FROM_EMAIL,
                email_template_name='authentication/password_reset_email.html',
                subject_template_name='authentication/password_reset_subject.txt',
            )
            return redirect(reverse('authentication:password_reset_done'))
        return render(request, 'authentication/forgot_password.html', {
            'form': form,
            'error': "Please enter a valid email address."
        })
    else:
        form = PasswordResetForm()

    return render(request, 'authentication/forgot_password.html', {
        'form': form
    })


def activation_sent(request):
    return render(request, 'authentication/activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid  = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except Exception:
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('authentication:activation_complete')
    else:
        return render(request, 'authentication/activation_invalid.html')


def activation_complete(request):
    return render(request, 'authentication/activation_complete.html')
