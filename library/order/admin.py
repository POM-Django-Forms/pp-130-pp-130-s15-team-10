from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .forms import OrderAdminForm
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

    @method_decorator(csrf_exempt, name='dispatch')
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        is_add_view = object_id is None

        if request.method == "POST":
            form = OrderAdminForm(request.POST, instance=None if is_add_view else Order.objects.get(pk=object_id))
            if form.is_valid():
                order = form.save()
                return redirect(reverse('admin:order_order_change', args=[order.pk]))
        else:
            form = OrderAdminForm(instance=None if is_add_view else Order.objects.get(pk=object_id))

        extra_context.update({
            'form': form,
            'original': None if is_add_view else Order.objects.get(pk=object_id),
            'title': "Add Order" if is_add_view else f"Change Order #{object_id}",
        })

        self.change_form_template = "order/update_order.html"

        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)
