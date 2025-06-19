from book.models import Book
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from . import models
from .models import Author
from .forms import CreateAuthorForm, EditAuthorForm, BookFormSet
from django.urls import reverse


@login_required
@permission_required('author.add_author', raise_exception=True)
def create_author(request):
    template_name = 'author/create_author.html'

    if request.method == 'POST':
        form = CreateAuthorForm(request.POST)
        if form.is_valid():
            author = form.save(commit=False)
            author.save()

            book_title = form.cleaned_data.get('book_title')
            if book_title:
                book, created = Book.objects.get_or_create(name=book_title)
                book.authors.add(author)

            return render(request, template_name, {'author': author, 'form': CreateAuthorForm()})
        else:
            return render(request, template_name, {'form': form})
    else:
        form = CreateAuthorForm()

    return render(request, template_name, {'form': form})


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
def remove_author(request):
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


@login_required
@permission_required('author.edit_author', raise_exception=True)
def edit_author(request, author_id):
    author = get_object_or_404(Author, pk=author_id)

    if request.method == 'POST':
        form = EditAuthorForm(request.POST, instance=author)
        formset = BookFormSet(request.POST, queryset=author.books.all())
        if form.is_valid() and formset.is_valid():
            print("Form data:", form.cleaned_data)
            author = form.save(commit=False)
            author.author_source_url = form.cleaned_data.get('author_source_url')
            author.save()
            formset.save()
            if request.user.is_superuser:
                return redirect(reverse('admin:author_author_change', args=[author.id]))

            return redirect('author:edit_author', author_id=author.id)
        else:
            print(form.errors)
            print(formset.errors)
    else:
        form = EditAuthorForm(instance=author)
        formset = BookFormSet(queryset=author.books.all())

    return render(request, 'author/edit_author.html', {
        'form': form,
        'formset': formset,
        'author': author,
        'readonly_fields': ['name', 'surname', 'patronymic'],
    })
