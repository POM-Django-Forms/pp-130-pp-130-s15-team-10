from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from author.models import Author
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .forms import BookLimitedUpdateForm, AddBookForm
from .models import Book


class AuthorInlineAdmin(admin.TabularInline):
    model = Book.authors.through
    extra = 1
    verbose_name = "Author"
    verbose_name_plural = "Authors"


class AuthorsFilter(SimpleListFilter):
    title = "Authors"
    parameter_name = "author"

    def lookups(self, request, model_admin):
        authors = Author.objects.all()
        return [(str(author.id), f"{author.name} {author.surname}") for author in authors]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(authors__id=self.value()).distinct()
        return queryset


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    add_form_template = 'book/add_form_custom.html'

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}

        if request.method == 'POST':
            form = AddBookForm(request.POST)
            if form.is_valid():
                book = form.save()
                form.save_m2m()
                return redirect(reverse('admin:book_book_changelist'))
        else:
            form = AddBookForm()

        authors = Author.objects.all()

        extra_context.update({
            'form': form,
            'authors': authors,
        })

        return super().add_view(request, form_url, extra_context=extra_context)

    list_display = ["id", 'name', "get_authors", "publication_year", 'count']

    def get_authors(self, obj):
        return ", ".join([f"{author.name} {author.surname}" for author in obj.authors.all()])

    get_authors.short_description = "Authors"

    list_display_links = ['name']

    list_filter = ("id", AuthorsFilter, "publication_year")

    search_fields = ['id', 'name', 'authors__name', 'authors__surname']
    list_editable = ['count']
    filter_vertical = ['authors']
    ordering = ['id']

    inlines = [AuthorInlineAdmin]

    change_form_template = "book/change_form_limited.html"

    @csrf_exempt
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        book = get_object_or_404(Book, pk=object_id) if object_id else None

        if request.method == "POST":
            form = BookLimitedUpdateForm(request.POST, instance=book)
            if form.is_valid():
                form.save()
                return redirect(reverse('admin:book_book_change', args=[book.pk]))
        else:
            form = BookLimitedUpdateForm(instance=book)

        extra_context.update({
            'form': form,
            'book': book,
        })

        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)
