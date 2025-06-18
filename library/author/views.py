from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect
from . import models
from django.contrib.auth.decorators import login_required


@login_required
def create_author(request):
    if request.method == 'POST':
        data = request.POST
        models.Author.create(data['name'],
                                      data['surname'],
                                      data['patronymic'])
        return redirect('author:create_author')
    return render(request, 'author/create_author.html')


@login_required
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
def remove_author(request):
    authors = models.Author.objects.all()
    deleted_author = None

    if request.method == 'POST':
        author_id = request.POST.get('authors')
        if author_id:
            try:
                author = models.Author.objects.get(id=author_id)

                if author.books.exists():
                    messages.error(request, f"Cannot delete author {author.name} {author.surname} — they have associated books.")
                else:
                    author.delete()
                    deleted_author = author
            except models.Author.DoesNotExist:
                messages.error(request, "Author not found.")

    return render(request, 'author/remove_author.html', {
        'authors': authors,
        'deleted_author': deleted_author,
    })
