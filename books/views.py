from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from .models import Book, BorrowRequest, BorrowRecord
from .forms import AddBookForm, BorrowRequestForm, RejectRequestForm, SearchForm
from .dsa import HashTable, Stack, merge_sort, linear_search, binary_search


# ── decorators ────────────────────────────────────────────────

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_admin():
            messages.error(request, 'Access restricted to library administrators.')
            return redirect('book_list')
        return view_func(request, *args, **kwargs)
    return wrapper


def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_student():
            messages.error(request, 'This action is for students only.')
            return redirect('book_list')
        return view_func(request, *args, **kwargs)
    return wrapper


# ── helpers ───────────────────────────────────────────────────

def _build_ht():
    ht = HashTable(capacity=64)
    ht.load_from_queryset(Book.objects.all())
    return ht


def _build_stack():
    stack = Stack()
    stack.load_from_queryset(BorrowRecord.objects.select_related('book', 'borrower'))
    return stack


def _my_active_request_ids(user):
    return set(
        BorrowRequest.objects.filter(borrower=user, status='approved')
        .values_list('book_id', flat=True)
    )


def _my_pending_request_ids(user):
    return set(
        BorrowRequest.objects.filter(borrower=user, status='pending')
        .values_list('book_id', flat=True)
    )


# ── book list ─────────────────────────────────────────────────

@login_required
def book_list(request):
    sort_by      = request.GET.get('sort', 'title')
    genre_filter = request.GET.get('genre', '')

    ht = _build_ht()
    all_books = ht.all_books()

    if genre_filter:
        all_books = [b for b in all_books if b['genre'] == genre_filter]

    # always use merge sort internally
    sorted_books = merge_sort(all_books, key=sort_by)

    available = [b for b in sorted_books if b['is_available']]
    borrowed  = [b for b in sorted_books if not b['is_available']]

    my_active_ids  = _my_active_request_ids(request.user)  if request.user.is_student() else set()
    my_pending_ids = _my_pending_request_ids(request.user) if request.user.is_student() else set()
    pending_count  = BorrowRequest.objects.filter(status='pending').count()

    stats = {
        'total':     ht.size,
        'available': sum(1 for b in all_books if b['is_available']),
        'borrowed':  sum(1 for b in all_books if not b['is_available']),
        'pending':   pending_count,
    }

    from .models import GENRE_CHOICES
    return render(request, 'books/book_list.html', {
        'books': sorted_books,
        'available': available,
        'borrowed': borrowed,
        'sort_by': sort_by,
        'genre_filter': genre_filter,
        'genre_choices': GENRE_CHOICES,
        'stats': stats,
        'my_active_ids': my_active_ids,
        'my_pending_ids': my_pending_ids,
    })


# ── my books (student) ────────────────────────────────────────

@student_required
def my_books(request):
    active   = BorrowRequest.objects.filter(borrower=request.user, status='approved').select_related('book')
    pending  = BorrowRequest.objects.filter(borrower=request.user, status='pending').select_related('book')
    returned = BorrowRequest.objects.filter(borrower=request.user, status='returned').select_related('book')
    rejected = BorrowRequest.objects.filter(borrower=request.user, status='rejected').select_related('book')
    return render(request, 'books/my_books.html', {
        'active': active, 'pending': pending,
        'returned': returned, 'rejected': rejected,
    })


# ── add book (admin) ──────────────────────────────────────────

@admin_required
def add_book(request):
    if request.method == 'POST':
        form = AddBookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.copies_available = book.copies_total
            book.added_by = request.user
            book.save()
            messages.success(request, f'"{book.title}" added to the library.')
            return redirect('book_list')
    else:
        form = AddBookForm()
    return render(request, 'books/add_book.html', {'form': form})


# ── remove book (admin) ───────────────────────────────────────

@admin_required
def remove_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if request.method == 'POST':
        ht = _build_ht()
        ht.delete(book.isbn)
        title = book.title
        book.delete()
        messages.success(request, f'"{title}" removed from the library.')
        return redirect('book_list')
    return render(request, 'books/confirm_remove.html', {'book': book})


# ── request to borrow (student) ───────────────────────────────

@student_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if book.copies_available <= 0:
        messages.error(request, f'No copies of "{book.title}" are currently available.')
        return redirect('book_list')

    existing = BorrowRequest.objects.filter(
        borrower=request.user, book=book, status__in=['pending', 'approved']
    ).first()
    if existing:
        messages.warning(request, f'You already have a {existing.status} request for this book.')
        return redirect('my_books')

    if request.method == 'POST':
        form = BorrowRequestForm(request.POST)
        if form.is_valid():
            BorrowRequest.objects.create(
                book=book,
                borrower=request.user,
                due_date=form.cleaned_data['due_date'],
                status='pending',
            )
            messages.success(request, f'Borrow request for "{book.title}" submitted. Awaiting admin approval.')
            return redirect('my_books')
    else:
        form = BorrowRequestForm()

    return render(request, 'books/borrow.html', {'book': book, 'form': form})


# ── admin: approve request ────────────────────────────────────

@admin_required
def approve_request(request, req_id):
    req = get_object_or_404(BorrowRequest, id=req_id, status='pending')
    if request.method == 'POST':
        if req.book.copies_available <= 0:
            messages.error(request, 'No copies available to approve this request.')
            return redirect('admin_dashboard')
        req.status = 'approved'
        req.approved_at = timezone.now()
        req.processed_by = request.user
        req.save()
        req.book.copies_available -= 1
        req.book.save()
        BorrowRecord.objects.create(
            book=req.book, borrower=req.borrower,
            action='borrow', due_date=req.due_date, request=req,
        )
        messages.success(request, f'Approved: {req.borrower.get_full_name()} — "{req.book.title}".')
        return redirect('admin_dashboard')
    return render(request, 'books/confirm_approve.html', {'req': req})


# ── admin: reject request ─────────────────────────────────────

@admin_required
def reject_request(request, req_id):
    req = get_object_or_404(BorrowRequest, id=req_id, status='pending')
    if request.method == 'POST':
        form = RejectRequestForm(request.POST)
        if form.is_valid():
            req.status = 'rejected'
            req.processed_by = request.user
            req.rejection_reason = form.cleaned_data.get('reason', '')
            req.save()
            messages.success(request, f'Request by {req.borrower.get_full_name()} rejected.')
            return redirect('admin_dashboard')
    else:
        form = RejectRequestForm()
    return render(request, 'books/confirm_reject.html', {'req': req, 'form': form})


# ── admin: process return ─────────────────────────────────────

@admin_required
def return_book(request, req_id):
    req = get_object_or_404(BorrowRequest, id=req_id, status='approved')
    if request.method == 'POST':
        req.status = 'returned'
        req.returned_at = timezone.now()
        req.processed_by = request.user
        req.save()
        req.book.copies_available = min(req.book.copies_available + 1, req.book.copies_total)
        req.book.save()
        BorrowRecord.objects.create(
            book=req.book, borrower=req.borrower,
            action='return', request=req,
        )
        messages.success(request, f'"{req.book.title}" marked as returned for {req.borrower.get_full_name()}.')
        return redirect('admin_dashboard')
    return render(request, 'books/confirm_return.html', {'req': req})


# ── search ────────────────────────────────────────────────────

@login_required
def search_books(request):
    form = SearchForm(request.GET or None)
    results, searched = [], False

    if form.is_valid():
        query = form.cleaned_data.get('query', '').strip()
        field = form.cleaned_data['field']

        if query:
            searched = True
            ht = _build_ht()
            all_books = ht.all_books()
            # always use linear search — best for partial matching
            results = linear_search(all_books, query, field=field)

    my_active_ids  = _my_active_request_ids(request.user)  if request.user.is_student() else set()
    my_pending_ids = _my_pending_request_ids(request.user) if request.user.is_student() else set()

    return render(request, 'books/search.html', {
        'form': form, 'results': results, 'searched': searched,
        'my_active_ids': my_active_ids, 'my_pending_ids': my_pending_ids,
    })


# ── history ───────────────────────────────────────────────────

@login_required
def history(request):
    if request.user.is_admin():
        qs = BorrowRecord.objects.select_related('book', 'borrower')
    else:
        qs = BorrowRecord.objects.select_related('book', 'borrower').filter(borrower=request.user)

    stack = Stack()
    stack.load_from_queryset(qs)
    records = stack.to_list()
    return render(request, 'books/history.html', {'records': records, 'stack_size': stack.size})


# ── book detail ───────────────────────────────────────────────

@login_required
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    ht = _build_ht()
    book_data = ht.get(book.isbn)

    active_requests = None
    if request.user.is_admin():
        active_requests = BorrowRequest.objects.filter(
            book=book, status__in=['approved', 'pending']
        ).select_related('borrower').order_by('-requested_at')

    my_request = None
    if request.user.is_student():
        my_request = BorrowRequest.objects.filter(
            borrower=request.user, book=book, status__in=['pending', 'approved']
        ).first()

    return render(request, 'books/book_detail.html', {
        'book': book, 'book_data': book_data,
        'active_requests': active_requests, 'my_request': my_request,
    })


# ── admin dashboard ───────────────────────────────────────────

@admin_required
def admin_dashboard(request):
    from accounts.models import User

    ht = _build_ht()
    all_books = ht.all_books()

    pending_requests  = BorrowRequest.objects.filter(status='pending').select_related('book', 'borrower')
    approved_requests = BorrowRequest.objects.filter(status='approved').select_related('book', 'borrower')
    total_students    = User.objects.filter(role='student').count()
    total_borrows     = BorrowRecord.objects.filter(action='borrow').count()
    total_returns     = BorrowRecord.objects.filter(action='return').count()

    context = {
        'total_books':       ht.size,
        'total_copies':      sum(b['copies_total'] for b in all_books),
        'available_copies':  sum(b['copies_available'] for b in all_books),
        'total_students':    total_students,
        'total_borrows':     total_borrows,
        'currently_out':     total_borrows - total_returns,
        'pending_requests':  pending_requests,
        'approved_requests': approved_requests,
        'pending_count':     pending_requests.count(),
        'recent_records':    BorrowRecord.objects.select_related('book', 'borrower')[:10],
    }
    return render(request, 'books/admin_dashboard.html', context)


# ── stat detail views ─────────────────────────────────────────

@admin_required
def stat_detail(request, stat):
    from accounts.models import User

    if stat == 'books':
        ht = _build_ht()
        items = merge_sort(ht.all_books(), key='title')
        return render(request, 'books/stat_books.html', {
            'items': items,
            'title': 'All Book Titles',
            'subtitle': f'{len(items)} titles in the library',
        })

    elif stat == 'copies':
        books = Book.objects.all().order_by('title')
        return render(request, 'books/stat_copies.html', {
            'books': books,
            'title': 'All Copies',
            'subtitle': 'Total physical copies across all titles',
        })

    elif stat == 'available':
        books = Book.objects.filter(copies_available__gt=0).order_by('title')
        return render(request, 'books/stat_copies.html', {
            'books': books,
            'title': 'Available Books',
            'subtitle': 'Books with at least one copy on the shelf',
        })

    elif stat == 'students':
        students = User.objects.filter(role='student').order_by('first_name')
        return render(request, 'books/stat_students.html', {'students': students})

    elif stat == 'borrows':
        records = BorrowRecord.objects.filter(action='borrow').select_related('book', 'borrower')
        return render(request, 'books/stat_records.html', {
            'records': records,
            'title': 'All Borrow Transactions',
            'subtitle': f'{records.count()} total borrows',
        })

    elif stat == 'out':
        reqs = BorrowRequest.objects.filter(status='approved').select_related('book', 'borrower')
        return render(request, 'books/stat_out.html', {'reqs': reqs})

    return redirect('admin_dashboard')
