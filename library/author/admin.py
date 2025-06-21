from django.contrib import admin
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.db.models import Count
import plotly.graph_objs as go
from django.views.decorators.csrf import csrf_exempt
from .models import Author
from book.models import Book
from django.contrib.admin import SimpleListFilter
from django.db.models import Q, Value
from django.db.models.functions import Concat
from .forms import CreateOrUpdateAuthorForm


class BookInline(admin.TabularInline):
    model = Book.authors.through
    extra = 0
    verbose_name = "Book"
    verbose_name_plural = "Books"
    show_change_link = True


class SurnameFilter(SimpleListFilter):
    title = 'Surname'
    parameter_name = 'surname'

    def lookups(self, request, model_admin):
        surnames = model_admin.model.objects.values_list('surname', flat=True).distinct()
        return [(s, s) for s in surnames if s]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(surname=self.value())
        return queryset


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


class BookNameFilter(admin.SimpleListFilter):
    title = 'Book'
    parameter_name = 'books__name'

    def lookups(self, request, model_admin):
        book_names = set(model_admin.model.objects.values_list('books__name', flat=True).distinct())
        return [(name, name) for name in book_names if name]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(books__name=self.value())
        return queryset


class PatronymicFilter(SimpleListFilter):
    title = 'Patronymic'
    parameter_name = 'patronymic'

    def lookups(self, request, model_admin):
        values = model_admin.model.objects.exclude(patronymic__isnull=True).exclude(patronymic='') \
            .values_list('patronymic', flat=True).distinct()
        return [(v, v) for v in values]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(patronymic=self.value())
        return queryset


class PublicationYearFilter(SimpleListFilter):
    title = 'Year of publication'
    parameter_name = 'books__publication_year'

    def lookups(self, request, model_admin):
        years = model_admin.model.objects.values_list('books__publication_year', flat=True) \
            .exclude(books__publication_year__isnull=True).distinct()
        return [(year, str(year)) for year in sorted(years) if year is not None]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(books__publication_year=self.value())
        return queryset


@admin.register(Author)
class AdminAuthor(admin.ModelAdmin):
    actions = None
    change_form_template = "author/create_or_update_author.html"

    @csrf_exempt
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['readonly_fields'] = ['name', 'surname', 'patronymic']
        author = None
        if object_id:
            author = get_object_or_404(Author, pk=object_id)

        if request.method == 'POST':
            form = CreateOrUpdateAuthorForm(request.POST, instance=author)

            if form.is_valid():
                author = form.save(commit=False)
                author.source_url = form.cleaned_data['source_url']
                author.save()
                return HttpResponseRedirect(reverse('admin:author_author_change', args=[author.pk]))
        else:
            form = CreateOrUpdateAuthorForm(instance=author)

        author_books = author.books.all() if author else []

        extra_context.update({
            'form': form,
            'author': author,
            'author_books': author_books,
            'action': 'Update Author'
        })

        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)

    list_display = ["full_name_colored", "book_count", "book_list", "easter_egg"]
    list_display_links = ["full_name_colored"]
    list_filter = [SurnameFilter, PatronymicFilter, BookNameFilter, PublicationYearFilter, BookCountFilter]
    search_fields = ['name', 'surname', 'patronymic', 'books__name']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        if not search_term:
            return queryset, use_distinct

        combined_filter = Q()

        combined_filter |= Q(
            pk__in=Author.objects.annotate(
                full_name=Concat('name', Value(' '), 'surname')
            ).filter(full_name__icontains=search_term).values_list('pk', flat=True)
        )

        combined_filter |= Q(
            pk__in=Author.objects.annotate(
                full_name=Concat('patronymic', Value(' '), 'surname')
            ).filter(full_name__icontains=search_term).values_list('pk', flat=True)
        )

        parts = search_term.lower().split()
        if len(parts) >= 2:
            candidates = Author.objects.all()

            def matches_all_parts(author):
                fields = [author.name, author.surname, author.patronymic or ""]
                full_text = " ".join(fields).lower()
                return all(part in full_text for part in parts)

            matched_ids = [a.pk for a in candidates if matches_all_parts(a)]
            combined_filter |= Q(pk__in=matched_ids)

        queryset = queryset.filter(combined_filter)

        return queryset, use_distinct

    ordering = ['surname', 'name']

    inlines = [BookInline]
    autocomplete_fields = ['books']

    @admin.display(description="Full Name", ordering='surname')
    def full_name_colored(self, obj):
        return format_html(
            f"<b style='color:#1a237e'>{obj.name} {obj.surname}</b><br><small>{obj.patronymic or ''}</small>"
        )

    @admin.display(description="Book count")
    def book_count(self, obj):
        return obj.books.count()

    @admin.display(description="Books")
    def book_list(self, obj):
        books = obj.books.all()
        if not books:
            return "-"
        return format_html(
            "<ul style='margin:0; padding-left:20px;'>"
            "{}"
            "</ul>",
            format_html_join(
                "",
                "<li>{}</li>",
                ((book.name,) for book in books)
            )
        )

    @admin.display(description='Think about this 💎')
    def easter_egg(self, obj):
        books = obj.books.all()
        count = books.count()

        if count == 0:
            return "🕳 This author has no books yet — maybe a hidden genius?"
        elif count == 1:
            title = books[0].name
            return f"📘 Only one book: “{title}” — quality over quantity!"
        elif count <= 3:
            titles = ", ".join([f"“{b.name}”" for b in books])
            return f"📚 Just starting: {titles}"
        else:
            longest_title = max(books, key=lambda b: len(b.name)).name
            return format_html(
                "🔥 Prolific writer with {} books. Longest title: <b>“{}”</b>.",
                count,
                longest_title
            )

    change_list_template = "author/author_change_list_with_chart.html"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        response = super().changelist_view(request, extra_context=extra_context)

        try:

            cl = self.get_changelist_instance(request)
            queryset = cl.queryset

            qs = queryset.annotate(book_count=Count('books')).order_by('-book_count')
            x = [author.surname for author in qs]
            y = [author.book_count for author in qs]

            fig = go.Figure(data=[go.Bar(x=x, y=y)])
            chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

            response.context_data['chart'] = chart_html
            response.context_data["can_add"] = request.user.has_perm("author.add_author")
            response.context_data["can_delete"] = request.user.has_perm("author.delete_author")

        except Exception as e:
            self.message_user(request, f"Error building chart: {e}", level='error')

        return response
