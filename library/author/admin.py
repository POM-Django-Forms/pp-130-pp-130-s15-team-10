from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.template.response import TemplateResponse
import plotly.graph_objs as go
from django.utils.html import mark_safe
from .models import Author
from book.models import Book
from django.contrib.admin import SimpleListFilter


class BookInline(admin.TabularInline):
    model = Book.authors.through
    extra = 0
    verbose_name = "Book"
    verbose_name_plural = "Books"
    show_change_link = True


class BookCountFilter(SimpleListFilter):
    title = 'Book count'
    parameter_name = 'book_count'

    def lookups(self, request, model_admin):
        return [
            ('0', 'No books'),
            ('1-3', '1–3 books'),
            ('4+', '4 or more'),
        ]

    def queryset(self, request, queryset):
        queryset = queryset.annotate(n=Count('books'))
        if self.value() == '0':
            return queryset.filter(n=0)
        elif self.value() == '1-3':
            return queryset.filter(n__gte=1, n__lte=3)
        elif self.value() == '4+':
            return queryset.filter(n__gte=4)
        return queryset


@admin.register(Author)
class AdminAuthor(admin.ModelAdmin):
    change_form_template = "author/author_change_form_custom.html"

    list_display = ["full_name_colored", "book_count", "book_list_truncated", "easter_egg"]
    list_display_links = ["full_name_colored"]
    list_filter = ['surname', 'patronymic', 'books__name', 'books__publication_year', BookCountFilter]
    search_fields = ['name', 'surname', 'patronymic', 'books__name']
    ordering = ['surname', 'name']

    readonly_fields = ['display_static_info', 'display_dynamic_info']
    inlines = [BookInline]
    autocomplete_fields = ['books']

    fieldsets = (
        ("Author Identity", {
            'fields': ('name', 'patronymic', 'surname')
        }),
        ("📖 Books", {
            'classes': ('collapse',),
            'fields': ('books',)
        }),
        ("🧠 Structured Info View", {
            'classes': ('wide',),
            'fields': ('display_static_info', 'display_dynamic_info')
        }),
    )

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if object_id:
            obj = self.get_object(request, object_id)
            if obj:
                extra_context['static_info'] = mark_safe(self.display_static_info(obj))
                extra_context['dynamic_info'] = mark_safe(self.display_dynamic_info(obj))
        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)

    @admin.display(description="Full Name", ordering='surname')
    def full_name_colored(self, obj):
        return format_html(
            f"<b style='color:#1a237e'>{obj.name} {obj.surname}</b><br><small>{obj.patronymic or ''}</small>"
        )

    @admin.display(description="Book Count")
    def book_count(self, obj):
        return obj.books.count()

    @admin.display(description="Books (truncated)")
    def book_list_truncated(self, obj):
        names = [b.name for b in obj.books.all()[:3]]
        return ", ".join(names) + ("..." if obj.books.count() > 3 else "")

    def display_static_info(self, obj):
        info = [
            f"<b>Author:</b> {obj.name} {obj.surname}",
            f"<b>Patronymic:</b> {obj.patronymic or '—'}",
            f"<b>ID:</b> {obj.pk}"
        ]
        return format_html("<ul>{}</ul>".format("".join(f"<li>{i}</li>" for i in info)))
    display_static_info.short_description = "Static Data"

    def display_dynamic_info(self, obj):
        book_data = [
            f"<b>{b.name}</b> ({b.publication_year if b.publication_year else 'Unknown'})"
            for b in obj.books.all()
        ]
        if not book_data:
            return "No books attached"
        return format_html("<ul>{}</ul>".format("".join(f"<li>{b}</li>" for b in book_data)))
    display_dynamic_info.short_description = "Dynamic Book Info"

    @admin.display(description='Easter Egg 💎')
    def easter_egg(self, obj):
        return "💎 You found it!"

    change_list_template = "author/author_change_list_with_chart.html"

    def changelist_view(self, request, extra_context=None):
        qs = Author.objects.annotate(book_count=Count('books')).order_by('surname')
        x = [author.surname for author in qs]
        y = [author.book_count for author in qs]

        fig = go.Figure(data=[go.Bar(x=x, y=y)])
        chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

        extra_context = extra_context or {}
        extra_context['chart'] = chart_html

        return super().changelist_view(request, extra_context=extra_context)

    def chart_view(self, request):
        qs = Author.objects.annotate(n=Count('books')).values('surname', 'n')
        x = [a['surname'] for a in qs]
        y = [a['n'] for a in qs]
        fig = go.Figure([go.Bar(x=x, y=y)])
        chart = fig.to_html(full_html=False, include_plotlyjs='cdn')
        context = dict(self.admin_site.each_context(request), chart=chart)
        return TemplateResponse(request, "author/author_chart.html", context)
