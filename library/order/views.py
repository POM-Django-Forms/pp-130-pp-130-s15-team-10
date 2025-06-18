import datetime
from datetime import timedelta
from book.models import Book
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from .models import Order
from datetime import datetime
from django.db.models import Q
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required


@login_required
def all_orders(request):
    query = request.GET.get('q', '').strip()
    orders = Order.objects.select_related('user', 'book').prefetch_related('book__authors').all()

    def is_valid_date(date_str):
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    q_filters = Q(id__iexact=query) | \
                Q(book__name__icontains=query) | \
                Q(book__authors__name__icontains=query) | \
                Q(book__authors__surname__icontains=query) | \
                Q(user__email__icontains=query) | \
                Q(user__first_name__icontains=query) | \
                Q(user__last_name__icontains=query)

    if ' ' in query:
        first, last = query.split(' ', 1)
        q_filters |= Q(user__first_name__icontains=first) & Q(user__last_name__icontains=last)

    if ' ' in query:
        first, last = query.split(' ', 1)
        q_filters |= Q(book__authors__name__icontains=first) & Q(book__authors__surname__icontains=last)

    if is_valid_date(query):
        q_filters |= Q(created_at__date=query)

    orders = orders.filter(q_filters).distinct('id')

    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,
        'filtered': bool(query),
    }
    return render(request, 'order/all_orders.html', context)


@login_required
def show_own_orders(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user).select_related('book')
        context = {'orders': orders}
        return render(request, 'order/user_orders.html', context)
    return render(request, 'order/user_orders.html', {})


def user_already_ordered_this_book(user, book_id):
    return Order.objects.filter(user=user, book_id=book_id).exists()


def get_books_not_ordered_by_user(user):
    ordered_books = Order.objects.filter(user=user).values_list('book_id', flat=True)
    return Book.objects.exclude(id__in=ordered_books)


@login_required
def create_order(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to create an order.")
        return redirect('login')

    if request.user.role:
        messages.error(request, "Only users without librarian role can create orders.")
        return redirect('some_page')

    books = get_books_not_ordered_by_user(request.user)

    if request.method == 'POST':
        book_id = request.POST.get('book')
        term_days = request.POST.get('term')

        if not book_id or not term_days:
            messages.error(request, "Please select a book and enter the term.")
            return render(request, 'order/create_order.html', {'books': books})

        if user_already_ordered_this_book(request.user, book_id):
            messages.error(request, "You cannot order the same book twice.")
            return render(request, 'order/create_order.html', {'books': books})

        try:
            book = Book.objects.get(pk=book_id)
            term_days = int(term_days)
            if term_days <= 0:
                raise ValueError("Term must be greater than 0.")

            created_at = timezone.now()
            plated_end_at = created_at + timedelta(days=term_days)

            order = Order.objects.create(
                user=request.user,
                book=book,
                created_at=created_at,
                plated_end_at=plated_end_at
            )

            messages.success(request, f"Order #{order.id} created successfully!")

            books = get_books_not_ordered_by_user(request.user)
            return render(request, 'order/create_order.html', {'books': books})

        except IntegrityError:
            messages.error(request, "You have already ordered this book.")
        except ValueError:
            messages.error(request, "Invalid term value.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

        return render(request, 'order/create_order.html', {'books': books})

    if not books.exists():
        messages.warning(request, "You have already ordered all available books.")

    return render(request, 'order/create_order.html', {'books': books})


@login_required
def close_order(request):
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_orders')
        page = request.POST.get('page', '1')
        q = request.POST.get('q', '')

        if selected_ids:
            orders = Order.objects.filter(id__in=selected_ids, end_at__isnull=True)
            count = orders.update(end_at=timezone.now())
            messages.success(request, f"{count} order(s) successfully closed.")
        else:
            messages.warning(request, "No orders were selected.")

        base_url = reverse('order:all_orders')
        query_params = f"?page={page}"
        if q:
            query_params += f"&q={q}"

        return redirect(f"{base_url}{query_params}")

    return redirect('order:all_orders')
