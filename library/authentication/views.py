from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from order.models import Order
from .models import CustomUser
from .forms import LoginForm, RegisterForm, StyledPasswordResetForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('authentication:main')

    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            return redirect('authentication:main')

    return render(request, 'authentication/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('authentication:main')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                user = CustomUser.objects.create_user(
                    email=cd['login'],
                    password=cd['password'],
                    first_name=cd['firstname'],
                    last_name=cd['lastname'],
                    middle_name=cd['middle_name'],
                    role=int(cd['role']),
                    is_active=False
                )
            except IntegrityError:
                form.add_error(None, "Some error occurred.")
                return render(request, 'authentication/register.html', {'form': form})

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
    else:
        form = RegisterForm()

    return render(request, 'authentication/register.html', {'form': form})


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
        form = StyledPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if not CustomUser.objects.filter(email__iexact=email, is_active=True).exists():
                form.add_error('email', "No active account found with that email address.")
            else:
                form.save(
                    request=request,
                    use_https=request.is_secure(),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    email_template_name='authentication/password_reset_email.html',
                    subject_template_name='authentication/password_reset_subject.txt',
                )
                return redirect('authentication:password_reset_done')
    else:
        form = StyledPasswordResetForm()

    return render(request, 'authentication/forgot_password.html', {'form': form})


def activation_sent(request):
    return render(request, 'authentication/activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
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
