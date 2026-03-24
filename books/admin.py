from django.contrib import admin
from .models import Book, BorrowRequest, BorrowRecord


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'year', 'genre', 'copies_total', 'copies_available']
    list_filter = ['genre']
    search_fields = ['title', 'author', 'isbn']


@admin.register(BorrowRequest)
class BorrowRequestAdmin(admin.ModelAdmin):
    list_display = ['book', 'borrower', 'status', 'requested_at', 'due_date']
    list_filter = ['status']


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ['book', 'borrower', 'action', 'timestamp', 'due_date']
    list_filter = ['action']
