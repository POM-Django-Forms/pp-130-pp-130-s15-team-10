from django.contrib.messages import get_messages
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.urls import reverse
from . import models
from authentication.models import CustomUser
from order.models import Order
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from .forms import AddBookForm, BookSearchForm
from author.models import Author
from functools import wraps, reduce
from operator import and_


@login_required
@permission_required('author.view_book', raise_exception=True)
def show_books(request):
    form = BookSearchForm(request.GET or None)
    books = models.Book.objects.all().prefetch_related('authors')
    query = ''

    if form.is_valid():
        query = form.cleaned_data.get('q', '').strip()

        if query:
            if query.isdigit():
                books = books.filter(count=int(query))
            else:
                parts = query.split()

                combined_filters = [
                    Q(name__icontains=part) |
                    Q(authors__name__icontains=part) |
                    Q(authors__surname__icontains=part) |
                    Q(authors__patronymic__icontains=part)
                    for part in parts
                ]

                books = books.filter(reduce(and_, combined_filters)).distinct()

            if not books.exists():
                messages.error(
                    request,
                    f"No books found for your search: '{query}'",
                    extra_tags='books'
                )

    storage = get_messages(request)
    book_messages = [m for m in storage if 'books' in m.tags]

    paginator = Paginator(books, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'book/show_books.html', {
        'books': books,
        'page_obj': page_obj,
        'query': query,
        'filtered': bool(query),
        'form': form,
        'messages': book_messages,
    })


@login_required
def book_detail(request, book_id):
    book = models.Book.get_by_id(book_id=book_id)
    return render(request, 'book/book_detail.html', {'book': book})


@login_required
def user_detail_book(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    books = []
    for i in Order.objects.all():
        if i.user.id == user_id:
            books.append(i.book)

    return render(request, 'book/user_detail_books.html', {'books': books,
                                                           'user': user})


@login_required
def create_book(request, form_url='', extra_context=None):
    extra_context = extra_context or {}

    if request.method == 'POST':
        form = AddBookForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                form.save_m2m()
                return redirect(reverse('admin:book_book_changelist'))
            except IntegrityError as e:
                form.add_error(None, "Book with this name already exists.")
    else:
        form = AddBookForm()

    authors = Author.objects.all()

    extra_context.update({
        'form': form,
        'authors': authors,
    })

    return super().add_view(request, form_url, extra_context=extra_context)


def update_book():
    return None


def delete_book():
    return None