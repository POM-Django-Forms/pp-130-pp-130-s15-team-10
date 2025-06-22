from functools import reduce
from operator import and_
from authentication.models import CustomUser
from author.models import Author
from book.forms import CreateOrUpdateBookForm, AuthorFormSet
from book.models import Book
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import get_messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms.utils import ErrorList
from django.shortcuts import get_object_or_404, redirect, render
from order.models import Order
from django.contrib.auth.decorators import permission_required
from utils.permissions import required_permissions
from . import models
from .forms import BookSearchForm, CreateOrUpdateBookForm, DeleteBookForm, AuthorFormSet
from .models import Book


@login_required
def show_books(request):
    form = BookSearchForm(request.GET or None)
    books = models.Book.objects.filter(is_deleted=False).prefetch_related('authors')
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

    paginator = Paginator(books, 9)
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
@required_permissions(['book.add_book', 'book.change_book'])
def create_or_update_book(request, book_id=None):
    book_instance = get_object_or_404(Book, pk=book_id) if book_id else None

    if request.method == 'POST':
        form = CreateOrUpdateBookForm(request.POST, instance=book_instance)
        author_formset = AuthorFormSet(request.POST, prefix='authors')

        if form.is_valid() and author_formset.is_valid():
            book = form.save(commit=False)

            authors = set()
            for af in author_formset:
                if af.cleaned_data.get('DELETE'):
                    continue
                author = af.cleaned_data.get('author')
                if author:
                    authors.add(author)

            if not authors:
                author_formset._non_form_errors = ErrorList(["You must select at least one author."])

                return render(request, 'book/create_or_update_book.html', {
                    'form': form,
                    'author_formset': author_formset,
                    'action': 'Update Book' if book_id else 'Create Book',
                })

            existing_books = Book.objects.filter(
                name__iexact=book.name.strip(),
                publication_year=book.publication_year
            )
            if book_instance:
                existing_books = existing_books.exclude(pk=book_instance.pk)

            submitted_authors = set(a.id for a in authors)

            for existing in existing_books:
                existing_authors = set(existing.authors.values_list('id', flat=True))
                if existing_authors == submitted_authors:
                    form.add_error(None, "A book with this title, authors, and publication year already exists")
                    break

            if not form.errors:
                book.save()
                book.authors.set(authors)
                return redirect('book:show_books')

    else:
        form = CreateOrUpdateBookForm(instance=book_instance)
        initial_data = [{'author': author.pk} for author in book_instance.authors.all()] if book_instance else []
        author_formset = AuthorFormSet(initial=initial_data, prefix='authors')

    return render(request, 'book/create_or_update_book.html', {
        'form': form,
        'author_formset': author_formset,
        'action': 'Update Book' if book_id else 'Create Book',
    })


@login_required
@permission_required('book.delete_book', raise_exception=True)
def delete_book(request):
    if request.method == 'POST':
        form = DeleteBookForm(request.POST)
        if form.is_valid():
            book = form.cleaned_data['book']
            book.is_deleted = True
            book.save()
            messages.success(request, f"The book '{book.name}' was successfully marked as deleted.")
            return redirect('book:show_books')  # заміни на свій url
    else:
        form = DeleteBookForm()

    return render(request, 'book/delete_book.html', {
        'form': form,
        'title': 'Delete Book'
    })
