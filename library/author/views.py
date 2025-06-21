from functools import wraps, reduce
from operator import and_
from book.models import Book
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from . import models
from .forms import CreateOrUpdateAuthorForm, AuthorSearchForm, DeleteAuthorForm
from .models import Author


def permissions_required(perms):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not all(request.user.has_perm(perm) for perm in perms):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


@login_required
@permissions_required(['author.add_author', 'author.change_author'])
def create_or_update_author(request, author_id=None):
    if author_id:
        author = get_object_or_404(Author, pk=author_id)
        form = CreateOrUpdateAuthorForm(request.POST or None, instance=author)
        action = 'Update Author'
        author_books = author.books.all()
    else:
        author = None
        form = CreateOrUpdateAuthorForm(request.POST or None)
        action = 'Create Author'
        author_books = None

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('author:show_authors')

    return render(request, 'author/create_or_update_author.html', {
        'form': form,
        'author': author,
        'author_books': author_books,
        'action': action,
    })


@login_required
@permission_required('author.view_author', raise_exception=True)
def show_authors(request):
    form = AuthorSearchForm(request.GET or None)
    query = ''
    authors = models.Author.objects.filter(is_deleted=False)

    if form.is_valid():
        query = form.cleaned_data.get('q', '').strip()
        if query:
            parts = query.split()

            combined_filters = [
                Q(name__icontains=part) | Q(surname__icontains=part) | Q(patronymic__icontains=part)
                for part in parts
            ]

            authors = authors.filter(reduce(and_, combined_filters)).distinct()

    authors = authors.order_by('surname', 'name')

    paginator = Paginator(authors, 30)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'author/show_authors.html', {
        'page_obj': page_obj,
        'page_number': page_number,
        'query': query,
        'filtered': bool(query),
        'form': form,
    })


@login_required
@permission_required('author.delete_author', raise_exception=True)
def delete_author(request):
    if request.method == 'POST':
        form = DeleteAuthorForm(request.POST)
        if form.is_valid():
            author = form.cleaned_data['author']
            if author.books.exists():
                messages.error(
                    request,
                    f"Cannot delete author {author.name} {author.surname} — they have associated books."
                )
            else:
                author.is_deleted = True
                author.save()
                messages.success(
                    request,
                    f"Successfully deleted author {author.name} {author.surname}!"
                )
                return redirect('author:delete_author')
    else:
        form = DeleteAuthorForm()

    return render(request, 'author/delete_author.html', {
        'form': form,
        'action': "Delete Author"
    })


@login_required
@permission_required('author.show_author', raise_exception=True)
def show_author(request, author_id):
    author = get_object_or_404(Author, pk=author_id, is_deleted=False)
    books = author.books.all()
    return render(request, 'author/show_author.html', {
        'author': author,
        'books': books,
        'action': "Show Author"
    })
