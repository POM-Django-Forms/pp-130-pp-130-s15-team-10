from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import Order
from book.models import Book
from django.utils import timezone
from django.contrib import messages


class IsReturnedFilter(SimpleListFilter):
    title = 'Returned Status'
    parameter_name = 'is_returned'

    def lookups(self, request, model_admin):
        return (
            ('returned', 'Returned'),
            ('not_returned', 'Not Returned'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'returned':
            return queryset.exclude(end_at__isnull=True)
        elif self.value() == 'not_returned':
            return queryset.filter(end_at__isnull=True)
        return queryset


class BookFilter(SimpleListFilter):
    title = 'Book'
    parameter_name = 'book'

    def lookups(self, request, model_admin):
        return [(book.id, book.name) for book in Book.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(book_id=self.value())
        return queryset


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'get_user_email', 'get_book_name',
        'created_at', 'plated_end_at', 'display_returned'
    )

    list_filter = (BookFilter, 'user', 'created_at', IsReturnedFilter)
    search_fields = ('user__email', 'book__name')
    ordering = ('-created_at',)
    actions = ['close_orders']

    readonly_fields = ('created_at',)
    date_hierarchy = 'plated_end_at'
    empty_value_display = '-empty-'

    def get_user_email(self, obj):
        return obj.user.email

    get_user_email.short_description = 'User Email'

    def get_book_name(self, obj):
        return obj.book.name

    get_book_name.short_description = 'Book Name'

    def display_returned(self, obj):
        return obj.end_at is not None

    display_returned.boolean = True
    display_returned.short_description = 'Returned'

    @admin.action(description="Close selected orders")
    def close_orders(self, request, queryset):
        open_orders = queryset.filter(end_at__isnull=True)
        count = open_orders.update(end_at=timezone.now())
        if count:
            self.message_user(request, f"{count} order(s) successfully closed.", messages.SUCCESS)
        else:
            self.message_user(request, "No open orders were selected.", messages.WARNING)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @csrf_exempt
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        order = get_object_or_404(Order, pk=object_id)

        if request.method == 'POST' and 'close_order' in request.POST:
            if order.end_at is None:
                order.end_at = timezone.now()
                order.save()
                messages.success(request, "Order closed successfully.")
            else:
                messages.warning(request, "This order is already closed.")

        extra_context = extra_context or {}
        extra_context.update({
            'order': order,
            'title': f"Change Order #{object_id}",
        })

        self.change_form_template = "order/show_order.html"

        return render(request, self.change_form_template, extra_context)
