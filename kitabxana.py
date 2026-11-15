"""
Mini Kitabxana İdarəetmə Sistemi (konsol tətbiqi)
Əhatə olunan mövzular:
 1. Array / Dynamic Array  -> benchmark (ölçmə və müqayisə)
 2. Singly / Doubly Linked List -> benchmark + DLL ilə "oxu siyahısı" naviqasiyası
 3. Stack / Queue / Deque  -> Undo (Stack), Borc sorğuları (Queue), Son baxılanlar (Deque)
 4. Hash Table (chaining)  -> ISBN ilə O(1) axtarış
 5. Binary Search Tree     -> Ada görə sıralı siyahı / axtarış / silmə
İşə salmaq: python kitabxana.py
"""
import sys
import os
import json
import time
import random
from collections import deque

sys.setrecursionlimit(20000)


# ====================== 1. ARRAY və DYNAMIC ARRAY ======================
class StaticArray:
    """Sabit ölçülü massiv: tutum dəyişmir, dolduqda xəta verir."""
    def __init__(self, capacity):
        self.data = [None] * capacity
        self.size = 0

    def append(self, v):
        if self.size == len(self.data):
            raise OverflowError("Massiv doludur")
        self.data[self.size] = v
        self.size += 1

    def insert_front(self, v):
        if self.size == len(self.data):
            raise OverflowError("Massiv doludur")
        for i in range(self.size, 0, -1):      # O(n) sürüşdürmə
            self.data[i] = self.data[i - 1]
        self.data[0] = v
        self.size += 1

    def delete_front(self):
        for i in range(1, self.size):          # O(n) sürüşdürmə
            self.data[i - 1] = self.data[i]
        self.size -= 1

    def delete_last(self):
        self.size -= 1

    def search(self, v):
        for i in range(self.size):             # O(n)
            if self.data[i] == v:
                return i
        return -1


class DynamicArray(StaticArray):
    """Tutum dolduqda 2 dəfə böyüyən massiv (amortized O(1) append)."""
    def __init__(self):
        super().__init__(4)

    def _grow(self):
        new = [None] * (len(self.data) * 2)
        for i in range(self.size):
            new[i] = self.data[i]
        self.data = new

    def append(self, v):
        if self.size == len(self.data):
            self._grow()
        super().append(v)

    def insert_front(self, v):
        if self.size == len(self.data):
            self._grow()
        super().insert_front(v)


# ====================== 2. LINKED LIST-lər ======================
class SNode:
    def __init__(self, v):
        self.v, self.next = v, None


class SinglyLinkedList:
    def __init__(self):
        self.head = self.tail = None
        self.size = 0

    def append(self, v):                       # tail var -> O(1)
        n = SNode(v)
        if self.tail:
            self.tail.next = n
        else:
            self.head = n
        self.tail = n
        self.size += 1

    def insert_front(self, v):                 # O(1)
        n = SNode(v)
        n.next = self.head
        self.head = n
        if not self.tail:
            self.tail = n
        self.size += 1

    def delete_front(self):                    # O(1)
        if self.head:
            self.head = self.head.next
            if not self.head:
                self.tail = None
            self.size -= 1

    def delete_last(self):                     # O(n): əvvəlki düyünü tapmaq lazımdır
        if not self.head:
            return
        if self.head is self.tail:
            self.head = self.tail = None
        else:
            cur = self.head
            while cur.next is not self.tail:
                cur = cur.next
            cur.next = None
            self.tail = cur
        self.size -= 1

    def search(self, v):                       # O(n)
        cur, i = self.head, 0
        while cur:
            if cur.v == v:
                return i
            cur, i = cur.next, i + 1
        return -1


class DNode:
    def __init__(self, v):
        self.v, self.next, self.prev = v, None, None


class DoublyLinkedList:
    def __init__(self):
        self.head = self.tail = None
        self.size = 0

    def append(self, v):
        n = DNode(v)
        if self.tail:
            self.tail.next, n.prev = n, self.tail
        else:
            self.head = n
        self.tail = n
        self.size += 1

    def insert_front(self, v):
        n = DNode(v)
        if self.head:
            n.next, self.head.prev = self.head, n
        else:
            self.tail = n
        self.head = n
        self.size += 1

    def delete_front(self):
        if self.head:
            self.head = self.head.next
            if self.head:
                self.head.prev = None
            else:
                self.tail = None
            self.size -= 1

    def delete_last(self):                     # O(1): prev göstəricisi var
        if self.tail:
            self.tail = self.tail.prev
            if self.tail:
                self.tail.next = None
            else:
                self.head = None
            self.size -= 1

    def search(self, v):
        cur, i = self.head, 0
        while cur:
            if cur.v == v:
                return i
            cur, i = cur.next, i + 1
        return -1


# ====================== 3. STACK / QUEUE / DEQUE ======================
class Stack:
    """Undo əməliyyatları üçün (LIFO)."""
    def __init__(self):
        self.items = []

    def push(self, x): self.items.append(x)
    def pop(self): return self.items.pop() if self.items else None
    def __len__(self): return len(self.items)


class Queue:
    """Borc sorğuları üçün (FIFO) - Singly Linked List üzərində."""
    def __init__(self):
        self.l = SinglyLinkedList()

    def enqueue(self, x): self.l.append(x)

    def dequeue(self):
        if not self.l.head:
            return None
        v = self.l.head.v
        self.l.delete_front()
        return v

    def __len__(self): return self.l.size


# Deque: "Son baxılan kitablar" üçün collections.deque(maxlen=5) istifadə olunur.


# ====================== 4. HASH TABLE (chaining) ======================
class HNode:
    def __init__(self, k, v):
        self.k, self.v, self.next = k, v, None


class HashTable:
    def __init__(self, capacity=8):
        self.cap = capacity
        self.buckets = [None] * capacity
        self.size = 0
        self.collisions = 0

    def _hash(self, key):
        h = 0
        for c in str(key):
            h = (h * 31 + ord(c)) & 0xFFFFFFFF
        return h % self.cap

    def put(self, key, value):
        i = self._hash(key)
        cur = self.buckets[i]
        while cur:                              # mövcuddursa yenilə
            if cur.k == key:
                cur.v = value
                return
            cur = cur.next
        if self.buckets[i] is not None:
            self.collisions += 1                # chaining: eyni bucket-ə düşdü
        n = HNode(key, value)
        n.next = self.buckets[i]
        self.buckets[i] = n
        self.size += 1
        if self.size / self.cap > 0.75:
            self._resize()

    def get(self, key):
        cur = self.buckets[self._hash(key)]
        while cur:
            if cur.k == key:
                return cur.v
            cur = cur.next
        return None

    def remove(self, key):
        i = self._hash(key)
        cur, prev = self.buckets[i], None
        while cur:
            if cur.k == key:
                if prev:
                    prev.next = cur.next
                else:
                    self.buckets[i] = cur.next
                self.size -= 1
                return True
            prev, cur = cur, cur.next
        return False

    def _resize(self):
        old = self.buckets
        self.cap *= 2
        self.buckets = [None] * self.cap
        self.size = 0
        for head in old:
            while head:
                self.put(head.k, head.v)
                head = head.next

    def stats(self):
        used = sum(1 for b in self.buckets if b)
        longest = 0
        for b in self.buckets:
            n = 0
            while b:
                n, b = n + 1, b.next
            longest = max(longest, n)
        return (f"elementlər={self.size}, bucket={self.cap}, dolu bucket={used}, "
                f"collision={self.collisions}, ən uzun zəncir={longest}, "
                f"load factor={self.size / self.cap:.2f}")


# ====================== 5. BINARY SEARCH TREE ======================
class TNode:
    def __init__(self, k, v):
        self.k, self.v, self.left, self.right = k, v, None, None


class BST:
    def __init__(self):
        self.root = None
        self.size = 0

    def insert(self, k, v):                     # iterativ (dərin ağacda stack overflow olmasın)
        n = TNode(k, v)
        if not self.root:
            self.root = n
            self.size += 1
            return
        cur = self.root
        while True:
            if k == cur.k:
                cur.v = v
                return
            side = "left" if k < cur.k else "right"
            nxt = getattr(cur, side)
            if nxt is None:
                setattr(cur, side, n)
                self.size += 1
                return
            cur = nxt

    def search(self, k):
        """(dəyər, müqayisə sayı) qaytarır."""
        cur, steps = self.root, 0
        while cur:
            steps += 1
            if k == cur.k:
                return cur.v, steps
            cur = cur.left if k < cur.k else cur.right
        return None, steps

    def delete(self, k):
        self.root, deleted = self._delete(self.root, k)
        if deleted:
            self.size -= 1
        return deleted

    def _delete(self, node, k):
        if not node:
            return None, False
        if k < node.k:
            node.left, d = self._delete(node.left, k)
            return node, d
        if k > node.k:
            node.right, d = self._delete(node.right, k)
            return node, d
        if not node.left:                       # 0 və ya 1 uşaq
            return node.right, True
        if not node.right:
            return node.left, True
        succ = node.right                       # 2 uşaq: inorder successor
        while succ.left:
            succ = succ.left
        node.k, node.v = succ.k, succ.v
        node.right, _ = self._delete(node.right, succ.k)
        return node, True

    def inorder(self):
        res, st, cur = [], [], self.root
        while st or cur:
            while cur:
                st.append(cur)
                cur = cur.left
            cur = st.pop()
            res.append((cur.k, cur.v))
            cur = cur.right
        return res

    def height(self):
        if not self.root:
            return 0
        h, level = 0, [self.root]
        while level:
            h += 1
            level = [c for n in level for c in (n.left, n.right) if c]
        return h


# ====================== TƏTBİQ: KİTABXANA ======================
class Book:
    def __init__(self, isbn, title, author, year="-", genre="-"):
        self.isbn, self.title, self.author = isbn, title, author
        self.year, self.genre = year, genre

    def __str__(self):
        return f"[{self.isbn}] {self.title} - {self.author} ({self.year}, {self.genre})"


class Library:
    def __init__(self):
        self.by_isbn = HashTable()              # ISBN -> Book (sürətli axtarış)
        self.by_title = BST()                   # ad -> Book (sıralı siyahı)
        self.undo = Stack()                     # Undo
        self.requests = Queue()                 # Borc sorğuları
        self.recent = deque(maxlen=5)           # Son baxılanlar
        self.reading_list = DoublyLinkedList()  # Oxu siyahısı (irəli/geri)
        self.cursor = None
        # Məlumatlar skriptlə eyni qovluqda kitabxana.json faylında saxlanır
        self.file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kitabxana.json")
        self.load()

    def save(self):
        books = [{"isbn": b.isbn, "title": b.title, "author": b.author,
                  "year": b.year, "genre": b.genre} for _, b in self.by_title.inorder()]
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump({"seeded": self.seeded, "books": books}, f, ensure_ascii=False, indent=2)

    def load(self):
        self.seeded = False
        if os.path.exists(self.file):
            try:
                with open(self.file, encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self.seeded = data.get("seeded", False)
                    data = data.get("books", [])
                books = [Book(d["isbn"], d["title"], d["author"], d.get("year", "-"), d.get("genre", "-"))
                         for d in data]
                for b in books:
                    self.by_isbn.put(b.isbn, b)
                # Fayl əlifba sırası ilə saxlanıldığı üçün kitabları sıra ilə əlavə etmək ağacı
                # "degenerate" edərdi. Ona görə ortadakı element birinci əlavə olunur (balanslı ağac).
                books.sort(key=lambda b: b.title.lower())
                stack = [(0, len(books) - 1)]
                while stack:
                    lo, hi = stack.pop()
                    if lo > hi:
                        continue
                    mid = (lo + hi) // 2
                    self.by_title.insert(books[mid].title.lower(), books[mid])
                    stack.append((lo, mid - 1))
                    stack.append((mid + 1, hi))
                print(f"  {len(data)} kitab fayldan yükləndi.")
            except (json.JSONDecodeError, OSError, KeyError):
                print("  Xəbərdarlıq: kitabxana.json oxunmadı.")
        if not self.seeded:                      # ilk işə salınma: hazır kataloq yüklənir
            self.seeded = True
            seed(self, quiet=True)
            print(f"  Hazır kataloq yükləndi ({self.by_title.size} kitab).")

    def add(self, book, record=True):
        if self.by_isbn.get(book.isbn):
            print("  Bu ISBN artıq mövcuddur.")
            return
        self.by_isbn.put(book.isbn, book)
        self.by_title.insert(book.title.lower(), book)
        if record:
            self.undo.push(("add", book))
        self.save()

    def remove(self, isbn, record=True):
        b = self.by_isbn.get(isbn)
        if not b:
            print("  Kitab tapılmadı.")
            return
        self.by_isbn.remove(isbn)
        self.by_title.delete(b.title.lower())
        if record:
            self.undo.push(("remove", b))
        self.save()
        print(f"  Silindi: {b}")

    def undo_last(self):
        op = self.undo.pop()
        if not op:
            print("  Geri qaytarılacaq əməliyyat yoxdur.")
            return
        kind, b = op
        if kind == "add":
            self.remove(b.isbn, record=False)
        else:
            self.add(b, record=False)
        print(f"  Undo: '{kind}' əməliyyatı geri qaytarıldı ({b.title}).")

    def view(self, isbn):
        b = self.by_isbn.get(isbn)
        if not b:
            print("  Kitab tapılmadı.")
            return
        print(" ", b)
        if b.isbn in [x.isbn for x in self.recent]:
            self.recent = deque((x for x in self.recent if x.isbn != b.isbn), maxlen=5)
        self.recent.appendleft(b)

    def borrow_request(self, isbn, user):
        if not self.by_isbn.get(isbn):
            print("  Kitab tapılmadı.")
            return
        self.requests.enqueue((isbn, user))
        print(f"  Sorğu növbəyə əlavə edildi. Növbədə: {len(self.requests)}")

    def process_request(self):
        r = self.requests.dequeue()
        if not r:
            print("  Növbə boşdur.")
            return
        b = self.by_isbn.get(r[0])
        print(f"  Təsdiqləndi: {r[1]} -> {b.title if b else r[0]}")


CATALOG = [
    ("BK-001", "Introduction to Algorithms", "Cormen, Leiserson, Rivest, Stein", 1990, "Proqramlaşdırma"),
    ("BK-002", "Clean Code", "Robert C. Martin", 2008, "Proqramlaşdırma"),
    ("BK-003", "The Pragmatic Programmer", "Hunt, Thomas", 1999, "Proqramlaşdırma"),
    ("BK-004", "Design Patterns", "Gamma, Helm, Johnson, Vlissides", 1994, "Proqramlaşdırma"),
    ("BK-005", "Data Structures and Algorithm Analysis", "Mark Allen Weiss", 1992, "Proqramlaşdırma"),
    ("BK-006", "Algorithms", "Sedgewick, Wayne", 2011, "Proqramlaşdırma"),
    ("BK-007", "The C Programming Language", "Kernighan, Ritchie", 1978, "Proqramlaşdırma"),
    ("BK-008", "Code Complete", "Steve McConnell", 1993, "Proqramlaşdırma"),
    ("BK-009", "Refactoring", "Martin Fowler", 1999, "Proqramlaşdırma"),
    ("BK-010", "Structure and Interpretation of Computer Programs", "Abelson, Sussman", 1985, "Proqramlaşdırma"),
    ("BK-011", "The Art of Computer Programming", "Donald Knuth", 1968, "Proqramlaşdırma"),
    ("BK-012", "Python Crash Course", "Eric Matthes", 2015, "Proqramlaşdırma"),
    ("BK-013", "Fluent Python", "Luciano Ramalho", 2015, "Proqramlaşdırma"),
    ("BK-014", "Eloquent JavaScript", "Marijn Haverbeke", 2011, "Proqramlaşdırma"),
    ("BK-015", "Grokking Algorithms", "Aditya Bhargava", 2016, "Proqramlaşdırma"),
    ("BK-016", "Cracking the Coding Interview", "Gayle McDowell", 2008, "Proqramlaşdırma"),
    ("BK-017", "Designing Data-Intensive Applications", "Martin Kleppmann", 2017, "Proqramlaşdırma"),
    ("BK-018", "Computer Networking: A Top-Down Approach", "Kurose, Ross", 2000, "Kompüter elmləri"),
    ("BK-019", "Operating System Concepts", "Silberschatz, Galvin", 1983, "Kompüter elmləri"),
    ("BK-020", "Database System Concepts", "Silberschatz, Korth", 1986, "Kompüter elmləri"),
    ("BK-021", "Artificial Intelligence: A Modern Approach", "Russell, Norvig", 1995, "Kompüter elmləri"),
    ("BK-022", "Dune", "Frank Herbert", 1965, "Elmi-fantastika"),
    ("BK-023", "Foundation", "Isaac Asimov", 1951, "Elmi-fantastika"),
    ("BK-024", "Fahrenheit 451", "Ray Bradbury", 1953, "Elmi-fantastika"),
    ("BK-025", "Brave New World", "Aldous Huxley", 1932, "Elmi-fantastika"),
    ("BK-026", "1984", "George Orwell", 1949, "Elmi-fantastika"),
    ("BK-027", "Animal Farm", "George Orwell", 1945, "Roman"),
    ("BK-028", "The Hobbit", "J.R.R. Tolkien", 1937, "Fantaziya"),
    ("BK-029", "Frankenstein", "Mary Shelley", 1818, "Roman"),
    ("BK-030", "Crime and Punishment", "Fyodor Dostoevsky", 1866, "Roman"),
    ("BK-031", "War and Peace", "Leo Tolstoy", 1869, "Roman"),
    ("BK-032", "Don Quixote", "Miguel de Cervantes", 1605, "Roman"),
    ("BK-033", "Pride and Prejudice", "Jane Austen", 1813, "Roman"),
    ("BK-034", "The Great Gatsby", "F. Scott Fitzgerald", 1925, "Roman"),
    ("BK-035", "To Kill a Mockingbird", "Harper Lee", 1960, "Roman"),
    ("BK-036", "The Stranger", "Albert Camus", 1942, "Roman"),
    ("BK-037", "One Hundred Years of Solitude", "Gabriel Garcia Marquez", 1967, "Roman"),
    ("BK-038", "The Old Man and the Sea", "Ernest Hemingway", 1952, "Roman"),
    ("BK-039", "The Little Prince", "Antoine de Saint-Exupery", 1943, "Roman"),
    ("BK-040", "The Alchemist", "Paulo Coelho", 1988, "Roman"),
    ("BK-041", "Ali and Nino", "Kurban Said", 1937, "Roman"),
    ("BK-042", "A Brief History of Time", "Stephen Hawking", 1988, "Elm"),
    ("BK-043", "Cosmos", "Carl Sagan", 1980, "Elm"),
    ("BK-044", "The Selfish Gene", "Richard Dawkins", 1976, "Elm"),
    ("BK-045", "On the Origin of Species", "Charles Darwin", 1859, "Elm"),
    ("BK-046", "Sapiens", "Yuval Noah Harari", 2011, "Tarix"),
    ("BK-047", "Thinking, Fast and Slow", "Daniel Kahneman", 2011, "Psixologiya"),
    ("BK-048", "Atomic Habits", "James Clear", 2018, "Psixologiya"),
    ("BK-049", "The Prince", "Niccolo Machiavelli", 1532, "Fəlsəfə"),
    ("BK-050", "Meditations", "Marcus Aurelius", 180, "Fəlsəfə"),
]


def seed(lib, quiet=False):
    """Hazır kataloqu yükləyir (mövcud ID-ləri keçir)."""
    added = 0
    for t in CATALOG:
        if not lib.by_isbn.get(t[0]):
            lib.add(Book(*t), record=False)
            added += 1
    if not quiet:
        print(f"  Kataloqdan {added} kitab əlavə edildi.")


def print_table(books):
    line = "  " + "-" * 92
    print(line)
    print(f"  {'ID':<8}{'Ad':<44}{'Müəllif':<24}{'İl':<6}{'Janr'}")
    print(line)
    for b in books:
        print(f"  {b.isbn:<8}{b.title[:42]:<44}{b.author[:22]:<24}{str(b.year):<6}{b.genre}")
    print(line)
    print(f"  Cəmi: {len(books)} kitab")


# ====================== BENCHMARK-lar ======================
def timed(fn, k):
    t = time.perf_counter()
    for _ in range(k):
        fn()
    return (time.perf_counter() - t) / k * 1e6   # mikrosaniyə / əməliyyat


def make(kind, n, extra):
    s = StaticArray(n + extra) if kind == "static" else {
        "dynamic": DynamicArray, "sll": SinglyLinkedList, "dll": DoublyLinkedList}[kind]()
    for i in range(n):
        s.append(i)
    return s


def benchmark_lists():
    names = {"static": "Static Array", "dynamic": "Dynamic Array",
             "sll": "Singly LL", "dll": "Doubly LL"}
    sizes = [1000, 5000, 20000]
    k = 50
    ops = [("append (sona)", lambda s: s.append(1)),
           ("insert front", lambda s: s.insert_front(1)),
           ("delete front", lambda s: s.delete_front()),
           ("delete last", lambda s: s.delete_last()),
           ("search (sonuncu)", None)]
    for n in sizes:
        print(f"\n  === n = {n} (µs / əməliyyat, orta {k} təkrar) ===")
        print(f"  {'Əməliyyat':<18}" + "".join(f"{names[x]:>15}" for x in names))
        for op_name, op in ops:
            row = f"  {op_name:<18}"
            for kind in names:
                s = make(kind, n, 2 * k + 5)
                if op is None:
                    row += f"{timed(lambda: s.search(n - 1), 10):>15.1f}"
                else:
                    row += f"{timed(lambda: op(s), k):>15.1f}"
            print(row)
    print("\n  Qeyd: Array-də front əməliyyatları O(n), LL-də O(1). Singly LL-də delete last O(n),"
          "\n  Doubly LL-də O(1). Axtarış hamısında O(n). Dynamic Array append amortized O(1).")


def benchmark_hash():
    print("\n  === Hash Table vs Linked List axtarışı (µs / axtarış) ===")
    for n in [1000, 10000, 50000]:
        ht, ll = HashTable(), SinglyLinkedList()
        for i in range(n):
            ht.put(str(i), i)
            ll.append(str(i))
        t_h = timed(lambda: ht.get(str(n - 1)), 200)
        t_l = timed(lambda: ll.search(str(n - 1)), 5)
        print(f"  n={n:<7} HashTable={t_h:8.2f}   LinkedList={t_l:10.2f}")
        print("   ", ht.stats())


def benchmark_bst():
    n = 2000
    keys = list(range(n))
    rnd = keys[:]
    random.shuffle(rnd)
    print(f"\n  === BST: {n} açar - təsadüfi vs sıralı əlavə ===")
    for name, order in [("Təsadüfi", rnd), ("Sıralı (artan)", keys)]:
        t = BST()
        for x in order:
            t.insert(x, x)
        steps = sum(t.search(x)[1] for x in random.sample(keys, 200)) / 200
        tm = timed(lambda: t.search(n - 1), 200)
        print(f"  {name:<16} hündürlük={t.height():<5} orta müqayisə={steps:7.1f}  vaxt={tm:7.2f} µs")
    print("""
  İzah: Sıralı verilənlər əlavə ediləndə hər yeni açar əvvəlkilərdən böyük olduğuna görə
  həmişə sağ tərəfə qoşulur. Ağac budaqlanmır, "degenerate" (əslində linked list-ə bənzər)
  formaya düşür: hündürlük ~ n olur. Nəticədə axtarış/əlavə/silmə O(log n) əvəzinə O(n) olur.
  Təsadüfi sıra ilə ağac balanslı qalır (hündürlük ~ 2·log2 n). Həll: AVL / Red-Black kimi
  self-balancing ağaclar və ya əlavə etməzdən əvvəl verilənləri qarışdırmaq.""")


# ====================== MENYU ======================
MENU = """
==== KİTABXANA SİSTEMİ ====
 1. Kitab əlavə et            (Hash Table + BST)
 2. Kitabı sil                (Hash Table + BST)
 3. ISBN ilə axtar            (Hash Table)
 4. Ada görə axtar            (BST)
 5. Kitabları əlifba ilə göstər (BST inorder)
 6. Son əməliyyatı geri qaytar (Stack - Undo)
 7. Borc sorğusu əlavə et     (Queue)
 8. Növbəti sorğunu emal et   (Queue)
 9. Son baxılan kitablar      (Deque)
10. Oxu siyahısı naviqasiyası (Doubly LL)
11. Benchmark: Array / Dynamic Array / Singly LL / Doubly LL
12. Benchmark: Hash Table (collision statistikası)
13. Benchmark: BST (sıralı vs təsadüfi)
14. Hazır kataloqu bərpa et
15. Statistika
 0. Çıxış"""


def reading_list_menu(lib):
    rl = lib.reading_list
    while True:
        cur = lib.cursor.v if lib.cursor else "-"
        print(f"\n  Oxu siyahısı ({rl.size} kitab). Hazırkı: {cur}")
        raw = input("  [a]dd ISBN / [n]ext / [p]rev / [b]ack: ").strip()
        c = raw.lower()
        if c.startswith("a"):
            isbn = raw[1:].strip() or input("  ID/ISBN: ").strip()
            b = lib.by_isbn.get(isbn)
            if b:
                rl.append(b.title)
                lib.cursor = lib.cursor or rl.tail
            else:
                print("  Kitab tapılmadı.")
        elif c == "n" and lib.cursor and lib.cursor.next:
            lib.cursor = lib.cursor.next
        elif c == "p" and lib.cursor and lib.cursor.prev:
            lib.cursor = lib.cursor.prev
        elif c == "b":
            return
        else:
            print("  Mümkün deyil / yanlış əmr.")


def main():
    lib = Library()
    while True:
        print(MENU)
        c = input("Seçim: ").strip()
        if c == "0":
            print("Sağ olun!")
            break
        elif c == "1":
            lib.add(Book(input("  ID/ISBN: ").strip(), input("  Ad: ").strip(), input("  Müəllif: ").strip(),
                         input("  İl: ").strip() or "-", input("  Janr: ").strip() or "-"))
        elif c == "2":
            lib.remove(input("  ISBN: "))
        elif c == "3":
            lib.view(input("  ISBN: "))
        elif c == "4":
            q = input("  Ad (və ya başlanğıc hissəsi): ").strip().lower()
            v, steps = lib.by_title.search(q)
            hits = [b for k, b in lib.by_title.inorder() if q and k.startswith(q)]
            if v and v not in hits:
                hits.insert(0, v)
            if hits:
                print_table(hits)
            else:
                print("  Tapılmadı.")
            print(f"  (dəqiq axtarışda BST müqayisə sayı: {steps})")
        elif c == "5":
            print_table([b for _, b in lib.by_title.inorder()])
            print(f"  Ağacın hündürlüyü: {lib.by_title.height()}")
        elif c == "6":
            lib.undo_last()
        elif c == "7":
            lib.borrow_request(input("  ISBN: "), input("  İstifadəçi: "))
        elif c == "8":
            lib.process_request()
        elif c == "9":
            print("  Son baxılanlar (ən yenisi birinci):")
            for b in lib.recent:
                print("   ", b)
        elif c == "10":
            reading_list_menu(lib)
        elif c == "11":
            benchmark_lists()
        elif c == "12":
            benchmark_hash()
        elif c == "13":
            benchmark_bst()
        elif c == "14":
            seed(lib)
        elif c == "15":
            print(f"  Kitab sayı: {lib.by_title.size}   BST hündürlüyü: {lib.by_title.height()}")
            print(f"  Hash Table: {lib.by_isbn.stats()}")
            print(f"  Sorğu növbəsi: {len(lib.requests)}   Undo: {len(lib.undo)}   Son baxılan: {len(lib.recent)}")
        else:
            print("  Yanlış seçim.")


if __name__ == "__main__":
    main()
