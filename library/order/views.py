import datetime
from datetime import datetime
from datetime import timedelta
from book.models import Book
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from .forms import OrderSearchForm, CloseOrdersForm, OrderCreateForm
from .models import Order


@login_required
@permission_required('order.view_order', raise_exception=True)
def all_orders(request):
    query = request.GET.get('q', '').strip()
    orders = Order.objects.select_related('user', 'book').prefetch_related('book__authors').all().order_by("-id")

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

    def is_valid_date(date_str):
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    if is_valid_date(query):
        q_filters |= Q(created_at__date=query)

    orders = orders.filter(q_filters).distinct('id')

    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    choices = [(str(order.id), str(order.id)) for order in page_obj.object_list]

    search_form = OrderSearchForm(request.GET or None)
    close_orders_form = CloseOrdersForm()
    close_orders_form.fields['selected_orders'].choices = choices  # Встановлюємо choices для форми

    context = {
        'orders': page_obj.object_list,
        'page_obj': page_obj,
        'search_form': search_form,
        'close_orders_form': close_orders_form,
        'query': query,
        'filtered': bool(query),
    }

    return render(request, 'order/all_orders.html', context)


@login_required
@permission_required('order.view_order', raise_exception=True)
def show_order(request, id):
    order = get_object_or_404(Order, id=id)
    context = {
        'order': order,
    }
    return render(request, 'order/show_order.html', context)


@login_required
def show_own_orders(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user).select_related('book')
        context = {'orders': orders}
        return render(request, 'order/user_orders.html', context)
    return render(request, 'order/user_orders.html', {})


def user_already_ordered_this_book(user, book_id):
    return Order.objects.filter(user=user, book_id=book_id, end_at__isnull=True).exists()


def get_books_not_ordered_by_user(user):
    active_ordered_books = Order.objects.filter(user=user, end_at__isnull=True).values_list('book_id', flat=True)
    return Book.objects.exclude(id__in=active_ordered_books)


@login_required
def create_order(request):
    if request.user.role == 1:
        return redirect('order:all_orders')

    books = get_books_not_ordered_by_user(request.user).filter(is_deleted=False)

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)

        if form.is_valid():
            form.instance.user = request.user

            if user_already_ordered_this_book(request.user, form.cleaned_data['book']):
                messages.error(request, "You cannot order the same book twice.")
                return render(request, 'order/create_order.html', {'form': form, 'books': books})

            try:
                order = form.save(commit=False)
                order.created_at = timezone.now()

                order.plated_end_at = order.created_at + timedelta(days=form.cleaned_data['term'])
                order.save()

                books = get_books_not_ordered_by_user(request.user)

                form = OrderCreateForm()
                return render(request, 'order/create_order.html', {'form': form, 'books': books})
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                return render(request, 'order/create_order.html', {'form': form, 'books': books})

    else:
        form = OrderCreateForm()

    if not books.exists():
        messages.warning(request, "You have already ordered all available books.")

    return render(request, 'order/create_order.html', {'form': form, 'books': books})


@login_required
def close_orders(request):
    if not (request.user.is_superuser or request.user.role == 1):
        return redirect('order:all_orders')

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


@login_required
def close_order(request, id):
    if not (request.user.is_superuser or request.user.role == 1):
        return redirect('order:show_order')
    order = get_object_or_404(Order, id=id)
    if request.method == 'POST':
        form = CloseOrdersForm(request.POST)

        if form.is_valid():
            if order.end_at:
                return redirect('order:show_order', id=order.id)

            order.update(end_at=timezone.now())
            return redirect('order:show_order', id=order.id)

        return redirect('order:show_order', id=order.id)

    return redirect('order:all_orders')
