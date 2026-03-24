# LibraryDSA — KNU Central Library System
### COE 363: Data Structures & Algorithms Project

---

## Quick Start

```bash
# 1. Create + activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install Django
pip install django

# 3. Run migrations
python manage.py makemigrations accounts
python manage.py makemigrations books
python manage.py migrate

# 4. Seed sample data (books + demo users)
python manage.py seed

# 5. Start server
python manage.py runserver
```

Visit **http://127.0.0.1:8000**

---

## Demo Accounts

| Username | Password | Role |
|---|---|---|
| librarian | admin1234 | Library Admin |
| kwame | student1234 | Student |
| abena | student1234 | Student |
| kofi | student1234 | Student |

---

## Project Structure

```
libraryDSA/
├── manage.py
├── setup.sh
├── library_project/
│   ├── settings.py
│   └── urls.py
├── accounts/                  ← Auth app
│   ├── models.py              ← Custom User (role: admin/student)
│   ├── views.py               ← login, register, logout
│   └── templates/accounts/
│       ├── login.html
│       └── register.html
└── books/                     ← Main app
    ├── dsa.py                 ← ALL DSA (from scratch)
    ├── models.py              ← Book, BorrowRecord
    ├── views.py               ← role-based views
    ├── static/books/main.css
    └── templates/books/
        ├── base.html          ← sidebar layout
        ├── book_list.html     ← main grid
        ├── add_book.html
        ├── search.html
        ├── history.html
        ├── book_detail.html
        ├── admin_dashboard.html
        ├── borrow.html
        ├── confirm_return.html
        └── confirm_remove.html
```

---

## DSA Implementation (books/dsa.py)

| Structure / Algorithm | Class / Function | Complexity |
|---|---|---|
| Hash Table (chaining) | `HashTable` | O(1) avg insert/get |
| Linked List (buckets) | `LinkedList`, `Node` | — |
| Stack (history) | `Stack`, `StackNode` | O(1) push/pop |
| Merge Sort | `merge_sort()` | O(n log n) |
| Bubble Sort | `bubble_sort()` | O(n²) |
| Linear Search | `linear_search()` | O(n) |
| Binary Search | `binary_search()` | O(log n) |

---

## Role Permissions

| Feature | Admin | Student |
|---|---|---|
| View all books | ✓ | ✓ |
| Search books | ✓ | ✓ |
| View history | All records | Own records only |
| Add book | ✓ | ✗ |
| Remove book | ✓ | ✗ |
| Borrow book | ✗ | ✓ |
| Return book | ✗ | ✓ |
| Admin dashboard | ✓ | ✗ |
