# =============================================================
#  dsa.py — Data Structures & Algorithms (all from scratch)
#  COE 363 — Library Book Management System
# =============================================================


# ─────────────────────────────────────────────────────────────
#  LINKED LIST  (backbone of the HashTable's chaining)
# ─────────────────────────────────────────────────────────────

class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.length = 0

    def insert(self, key, value):
        current = self.head
        while current:
            if current.key == key:
                current.value = value
                return
            current = current.next
        new_node = Node(key, value)
        new_node.next = self.head
        self.head = new_node
        self.length += 1

    def get(self, key):
        current = self.head
        while current:
            if current.key == key:
                return current.value
            current = current.next
        return None

    def delete(self, key):
        if self.head is None:
            return False
        if self.head.key == key:
            self.head = self.head.next
            self.length -= 1
            return True
        current = self.head
        while current.next:
            if current.next.key == key:
                current.next = current.next.next
                self.length -= 1
                return True
            current = current.next
        return False

    def all_values(self):
        result = []
        current = self.head
        while current:
            result.append(current.value)
            current = current.next
        return result


# ─────────────────────────────────────────────────────────────
#  HASH TABLE  (chaining via LinkedList)
# ─────────────────────────────────────────────────────────────

class HashTable:
    def __init__(self, capacity=64):
        self.capacity = capacity
        self.size = 0
        self.buckets = [LinkedList() for _ in range(self.capacity)]

    def _hash(self, key):
        """Polynomial rolling hash — h = Σ(ord(c) × 31^i) mod capacity"""
        hash_value = 0
        prime = 31
        for i, char in enumerate(str(key)):
            hash_value = (hash_value + ord(char) * (prime ** i)) % self.capacity
        return hash_value

    def insert(self, key, value):
        index = self._hash(key)
        if self.buckets[index].get(key) is None:
            self.size += 1
        self.buckets[index].insert(key, value)

    def get(self, key):
        return self.buckets[self._hash(key)].get(key)

    def delete(self, key):
        removed = self.buckets[self._hash(key)].delete(key)
        if removed:
            self.size -= 1
        return removed

    def all_books(self):
        result = []
        for bucket in self.buckets:
            result.extend(bucket.all_values())
        return result

    def load_from_queryset(self, queryset):
        for book in queryset:
            self.insert(book.isbn, {
                'id': book.id,
                'isbn': book.isbn,
                'title': book.title,
                'author': book.author,
                'year': book.year,
                'genre': book.genre,
                'copies_total': book.copies_total,
                'copies_available': book.copies_available,
                'is_available': book.copies_available > 0,
                'cover_color': book.cover_color,
            })


# ─────────────────────────────────────────────────────────────
#  STACK  (LIFO — borrow / return history)
# ─────────────────────────────────────────────────────────────

class StackNode:
    def __init__(self, data):
        self.data = data
        self.next = None


class Stack:
    def __init__(self):
        self.top = None
        self.size = 0

    def push(self, data):
        node = StackNode(data)
        node.next = self.top
        self.top = node
        self.size += 1

    def pop(self):
        if self.is_empty():
            return None
        data = self.top.data
        self.top = self.top.next
        self.size -= 1
        return data

    def peek(self):
        return self.top.data if self.top else None

    def is_empty(self):
        return self.top is None

    def to_list(self):
        result = []
        current = self.top
        while current:
            result.append(current.data)
            current = current.next
        return result

    def load_from_queryset(self, queryset):
        for record in list(queryset.order_by('timestamp')):
            self.push({
                'id': record.id,
                'book_title': record.book.title,
                'book_isbn': record.book.isbn,
                'borrower_name': record.borrower.get_full_name() or record.borrower.username,
                'student_id': record.borrower.student_id or '—',
                'action': record.action,
                'timestamp': record.timestamp,
                'due_date': record.due_date,
            })


# ─────────────────────────────────────────────────────────────
#  SORTING ALGORITHMS
# ─────────────────────────────────────────────────────────────

def merge_sort(books, key='title'):
    """Recursive merge sort — O(n log n)"""
    if len(books) <= 1:
        return books
    mid = len(books) // 2
    left = merge_sort(books[:mid], key)
    right = merge_sort(books[mid:], key)
    return _merge(left, right, key)


def _merge(left, right, key):
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        lv = left[i][key]
        rv = right[j][key]
        if isinstance(lv, str):
            lv, rv = lv.lower(), rv.lower()
        if lv <= rv:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def bubble_sort(books, key='year'):
    """In-place bubble sort — O(n²)"""
    books = books[:]
    n = len(books)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            a, b = books[j][key], books[j + 1][key]
            if isinstance(a, str):
                a, b = a.lower(), b.lower()
            if a > b:
                books[j], books[j + 1] = books[j + 1], books[j]
                swapped = True
        if not swapped:
            break
    return books


# ─────────────────────────────────────────────────────────────
#  SEARCH ALGORITHMS
# ─────────────────────────────────────────────────────────────

def linear_search(books, query, field='title'):
    """Linear search — O(n). Partial, case-insensitive match."""
    query = query.lower().strip()
    return [b for b in books if query in str(b[field]).lower()]


def binary_search(books, query, field='title'):
    """
    Binary search — O(log n).
    List must be pre-sorted by the same field.
    Returns all prefix-matching entries.
    """
    query = query.lower().strip()
    low, high, match_index = 0, len(books) - 1, -1
    while low <= high:
        mid = (low + high) // 2
        val = str(books[mid][field]).lower()
        if val.startswith(query):
            match_index = mid
            break
        elif val < query:
            low = mid + 1
        else:
            high = mid - 1
    if match_index == -1:
        return []
    results = [books[match_index]]
    i = match_index - 1
    while i >= 0 and str(books[i][field]).lower().startswith(query):
        results.append(books[i]); i -= 1
    i = match_index + 1
    while i < len(books) and str(books[i][field]).lower().startswith(query):
        results.append(books[i]); i += 1
    return results
