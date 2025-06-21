from author.models import Author
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.views.main import ChangeList
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .forms import CreateOrUpdateBookForm
from .models import Book
import plotly.graph_objs as go


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
    add_form_template = 'book/create_or_update_book.html'

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}

        if request.method == 'POST':
            form = CreateOrUpdateBookForm(request.POST)
            if form.is_valid():
                form.save()
                form.save_m2m()
                return redirect(reverse('admin:book_book_changelist'))
        else:
            form = CreateOrUpdateBookForm()

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
    ordering = ['id']

    inlines = [AuthorInlineAdmin]

    change_form_template = "book/change_form_limited.html"

    @csrf_exempt
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        response = super().changelist_view(request, extra_context=extra_context)

        if hasattr(response, 'context_data') and response.context_data is not None:
            try:
                cl = ChangeList(
                    request, self.model, self.list_display,
                    self.list_display_links, self.list_filter,
                    self.date_hierarchy, self.search_fields,
                    self.list_select_related, self.list_per_page,
                    self.list_max_show_all, self.list_editable,
                    self,
                )
                queryset = cl.get_queryset(request)

                qs = queryset.annotate(book_count=Count('books')).order_by('-book_count')
                x = [author.surname for author in qs]
                y = [author.book_count for author in qs]

                fig = go.Figure(data=[go.Bar(x=x, y=y)])
                chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

                response.context_data['chart'] = chart_html
            except Exception as e:
                self.message_user(request, f"Error building chart: {e}", level='error')

        return response
