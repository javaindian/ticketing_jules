from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Book, Transaction, Fee

# Custom UserAdmin to display user_type and other fields
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'user_type')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'user_type', 'groups')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('user_type',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('user_type',)}),
    )

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'isbn', 'authors', 'category', 'status', 'publisher', 'published_date')
    search_fields = ('title', 'isbn', 'authors', 'category', 'publisher')
    list_filter = ('status', 'category', 'language')
    readonly_fields = ('created_at', 'updated_at', 'id')

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'book', 'transaction_type', 'transaction_date', 'due_date', 'return_date')
    search_fields = ('user__username', 'book__title', 'book__isbn')
    list_filter = ('transaction_type', 'transaction_date', 'due_date', 'return_date')
    autocomplete_fields = ['user', 'book'] # For easier selection in admin
    readonly_fields = ('id',)

class FeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'book', 'fee_type', 'amount', 'paid_status', 'payment_date', 'created_at')
    search_fields = ('user__username', 'book__title', 'transaction__id')
    list_filter = ('paid_status', 'fee_type', 'created_at', 'payment_date')
    autocomplete_fields = ['user', 'book', 'transaction']
    readonly_fields = ('id', 'created_at', 'updated_at')

admin.site.register(User, UserAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Fee, FeeAdmin)
