from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from books.models import Book

User = get_user_model()

BOOKS = [
    {"isbn": "978-0-13-468599-1", "title": "The Pragmatic Programmer", "author": "David Thomas", "year": 2019, "genre": "engineering", "copies_total": 3, "cover_color": "#2C5282"},
    {"isbn": "978-0-13-235088-4", "title": "Clean Code", "author": "Robert C. Martin", "year": 2008, "genre": "engineering", "copies_total": 2, "cover_color": "#276749"},
    {"isbn": "978-0-201-63361-0", "title": "Design Patterns", "author": "Gang of Four", "year": 1994, "genre": "engineering", "copies_total": 2, "cover_color": "#744210"},
    {"isbn": "978-0-13-110362-7", "title": "The C Programming Language", "author": "Brian Kernighan", "year": 1988, "genre": "science", "copies_total": 4, "cover_color": "#63171B"},
    {"isbn": "978-0-262-03384-8", "title": "Introduction to Algorithms", "author": "Thomas Cormen", "year": 2022, "genre": "mathematics", "copies_total": 5, "cover_color": "#1A365D"},
    {"isbn": "978-0-19-953556-9", "title": "A Brief History of Time", "author": "Stephen Hawking", "year": 1988, "genre": "science", "copies_total": 3, "cover_color": "#234E52"},
    {"isbn": "978-0-7432-7356-5", "title": "Sapiens", "author": "Yuval Noah Harari", "year": 2011, "genre": "history", "copies_total": 4, "cover_color": "#702459"},
    {"isbn": "978-0-14-028329-7", "title": "1984", "author": "George Orwell", "year": 1949, "genre": "fiction", "copies_total": 3, "cover_color": "#4A5568"},
    {"isbn": "978-0-14-303943-3", "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "year": 1925, "genre": "fiction", "copies_total": 2, "cover_color": "#744210"},
    {"isbn": "978-0-7432-7357-2", "title": "Atomic Habits", "author": "James Clear", "year": 2018, "genre": "non-fiction", "copies_total": 4, "cover_color": "#276749"},
]


class Command(BaseCommand):
    help = 'Seed the database with sample books and users'

    def handle(self, *args, **kwargs):
        # create admin user
        if not User.objects.filter(username='librarian').exists():
            admin = User.objects.create_superuser(
                username='librarian',
                password='admin1234',
                first_name='Library',
                last_name='Admin',
                role='admin',
            )
            self.stdout.write(self.style.SUCCESS('Admin created: librarian / admin1234'))
        else:
            admin = User.objects.get(username='librarian')

        # create sample students
        students = [
            ('kwame', 'Kwame', 'Mensah', 'UG/0012/22', 'Computer Engineering'),
            ('abena', 'Abena', 'Asante', 'UG/0045/22', 'Electrical Engineering'),
            ('kofi',  'Kofi',  'Adu',    'UG/0078/23', 'Mathematics'),
        ]
        for uname, fn, ln, sid, dept in students:
            if not User.objects.filter(username=uname).exists():
                User.objects.create_user(
                    username=uname, password='student1234',
                    first_name=fn, last_name=ln,
                    student_id=sid, department=dept,
                    role='student',
                )
                self.stdout.write(self.style.SUCCESS(f'Student created: {uname} / student1234'))

        # create books
        for bdata in BOOKS:
            if not Book.objects.filter(isbn=bdata['isbn']).exists():
                Book.objects.create(added_by=admin, **bdata,
                    copies_available=bdata['copies_total'])
                self.stdout.write(self.style.SUCCESS(f'Book added: {bdata["title"]}'))

        self.stdout.write(self.style.SUCCESS('\nSeed complete!'))
