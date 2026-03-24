from django.db import models
from django.conf import settings


COVER_COLORS = [
    ('#4A5568', 'Slate'),
    ('#744210', 'Amber'),
    ('#276749', 'Forest'),
    ('#2C5282', 'Navy'),
    ('#702459', 'Plum'),
    ('#234E52', 'Teal'),
    ('#63171B', 'Burgundy'),
    ('#1A365D', 'Midnight'),
]

GENRE_CHOICES = [
    ('fiction', 'Fiction'),
    ('non-fiction', 'Non-Fiction'),
    ('science', 'Science & Technology'),
    ('history', 'History'),
    ('biography', 'Biography'),
    ('mathematics', 'Mathematics'),
    ('engineering', 'Engineering'),
    ('arts', 'Arts & Humanities'),
    ('reference', 'Reference'),
    ('other', 'Other'),
]


class Book(models.Model):
    isbn = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    year = models.IntegerField()
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default='other')
    description = models.TextField(blank=True)
    copies_total = models.PositiveIntegerField(default=1)
    copies_available = models.PositiveIntegerField(default=1)
    cover_color = models.CharField(max_length=10, choices=COVER_COLORS, default='#4A5568')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='books_added'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

    def is_available(self):
        return self.copies_available > 0

    class Meta:
        ordering = ['title']


class BorrowRequest(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('returned', 'Returned'),
    ]
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_requests')
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='borrow_requests'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='processed_requests'
    )
    rejection_reason = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.borrower.username} -> {self.book.title} [{self.status}]"

    def is_active(self):
        return self.status == 'approved'

    class Meta:
        ordering = ['-requested_at']


class BorrowRecord(models.Model):
    ACTION_CHOICES = [('borrow', 'Borrow'), ('return', 'Return')]
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='borrows'
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    request = models.ForeignKey(
        BorrowRequest, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='records'
    )

    def __str__(self):
        return f"{self.action} - {self.book.title} - {self.borrower.username}"

    class Meta:
        ordering = ['-timestamp']
