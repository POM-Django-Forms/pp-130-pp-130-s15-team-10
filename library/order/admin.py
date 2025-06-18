from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from .models import Order


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


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user_email', 'get_book_name', 'created_at', 'plated_end_at', 'display_returned')
    list_filter = ('book', 'user', 'created_at', IsReturnedFilter)
    search_fields = ('user__email', 'book__name')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('book', 'user', 'created_at')
        }),
        ('Return Dates', {
            'classes': ('collapse',),
            'fields': (('end_at', 'plated_end_at'),)
        }),
    )

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
