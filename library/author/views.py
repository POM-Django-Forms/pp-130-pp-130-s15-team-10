from book.models import Book
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from . import models
from .models import Author
from .forms import CreateOrUpdateAuthorForm, AuthorBookFormSet
from book.forms import BookFormSet
from functools import wraps


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
    else:
        author = None
        form = CreateOrUpdateAuthorForm(request.POST or None)
        action = 'Add Author'

    book_formset = AuthorBookFormSet(request.POST or None)

    if request.method == 'POST':
        if form.is_valid() and book_formset.is_valid():
            author = form.save()
            for book_form in book_formset:
                if book_form.cleaned_data and not book_form.cleaned_data.get('DELETE', False):
                    title = book_form.cleaned_data.get('title')
                    source_url = book_form.cleaned_data.get('source_url')
                    if title:
                        book, created = Book.objects.get_or_create(name=title)
                        if source_url:
                            book.source_url = source_url
                            book.save()
                        book.authors.add(author)

            return redirect('author:detail', author_id=author.id)

    return render(request, 'author/create_or_update_author.html', {
        'form': form,
        'book_formset': book_formset,
        'author': author,
        'action': action,
    })


@login_required
@permission_required('author.view_author', raise_exception=True)
def show_authors(request):
    query = request.GET.get('q', '').strip()
    authors = models.Author.objects.all()

    if query:
        q_filters = (
                Q(name__icontains=query) |
                Q(surname__icontains=query) |
                Q(patronymic__icontains=query)
        )

        if ' ' in query:
            parts = query.split()
            if len(parts) == 2:
                first, last = parts
                q_filters |= (Q(name__icontains=first) & Q(surname__icontains=last))
                q_filters |= (Q(surname__icontains=first) & Q(name__icontains=last))

        authors = authors.filter(q_filters).distinct()
    authors = authors.order_by('surname', 'name')

    paginator = Paginator(authors, 30)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'author/show_authors.html', {
        'page_obj': page_obj,
        'page_number': page_number,
        'query': query,
        'filtered': bool(query),
    })


@login_required
@permission_required('author.delete_author', raise_exception=True)
def delete_author(request):
    authors = models.Author.objects.all()
    deleted_author = None

    if request.method == 'POST':
        author_id = request.POST.get('authors')
        if author_id:
            try:
                author = models.Author.objects.get(id=author_id)

                if author.books.exists():
                    messages.error(request,
                                   f"Cannot delete author {author.name} {author.surname} — they have associated books.")
                else:
                    author.delete()
                    deleted_author = author
            except models.Author.DoesNotExist:
                messages.error(request, "Author not found.")

    return render(request, 'author/remove_author.html', {
        'authors': authors,
        'deleted_author': deleted_author,
    })
