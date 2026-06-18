"""
СТАРТОВЫЙ ФАЙЛ — Занятие 2, Упражнения с фикстурами и параметризацией.

Задача:
    1. Определить нужные фикстуры в этом файле
    2. Написать тесты с использованием фикстур
    3. Применить параметризацию для поиска
    4. Разметить тесты маркерами smoke/boundary/negative

Эталон: tests/unit/test_library_books.py, test_library_borrow.py

Как запустить:
    pytest student_tasks/exercise_3_library.py -v
    pytest student_tasks/exercise_3_library.py -m smoke -v
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from library import Book, Member, Library


# ══════════════════════════════════════════════════════════════
#  ФИКСТУРЫ
# ══════════════════════════════════════════════════════════════


@pytest.fixture
def book_python():
    """Книга 'Python для профессионалов' — 3 экземпляра."""
    return Book(
        title="Python для профессионалов",
        author="Лучано Рамальо",
        isbn="978-1-001",
        total_copies=3,
    )


@pytest.fixture
def book_algorithms():
    return Book(
        title="Алгоритмы и структуры данных",
        author="Томас Кормен",
        isbn="978-1-002",
        total_copies=2,
    )

@pytest.fixture
def member_anna():
    return Member(name="Анна Иванова", member_id="M001")


@pytest.fixture
def empty_library():
    return Library()


@pytest.fixture
def library_with_books(empty_library, book_python, book_algorithms):
    empty_library.add_book(book_python)
    empty_library.add_book(book_algorithms)
    return empty_library


@pytest.fixture
def library_full(library_with_books, member_anna):
    library_with_books.register_member(member_anna)
    return library_with_books

# ══════════════════════════════════════════════════════════════
#  ТЕСТЫ С ФИКСТУРАМИ
# ══════════════════════════════════════════════════════════════


class TestAddBook:
    """Добавление книг."""

    @pytest.mark.smoke
    def test_add_new_book(self, empty_library, book_python):
        """Добавление новой книги в пустую библиотеку."""
        empty_library.add_book(book_python)
        assert empty_library.get_book("978-1-001") is not None

    def test_add_duplicate_book_increases_copies(self, library_with_books):
        duplicate_book = Book(
            title="Python для профессионалов",
            author="Лучано Рамальо",
            isbn="978-1-001",
            total_copies=2,
        )

        library_with_books.add_book(duplicate_book)

        book = library_with_books.get_book("978-1-001")
        assert book.total_copies == 5
        assert book.available_copies == 5


# ══════════════════════════════════════════════════════════════
#  ПАРАМЕТРИЗАЦИЯ
# ══════════════════════════════════════════════════════════════


class TestSearchBooks:
    @pytest.mark.parametrize(
        "query, expected_count",
        [
            ("python", 1),
            ("PYTHON", 1),
            ("Кормен", 1),
            ("алгоритмы", 1),
            ("структуры", 1),
            ("несуществующая книга", 0),
        ],
    )
    def test_search_books(self, library_with_books, query, expected_count):
        result = library_with_books.search_books(query)

        assert len(result) == expected_count


# ══════════════════════════════════════════════════════════════
#  МАРКЕРЫ: SMOKE, BOUNDARY, NEGATIVE
# ══════════════════════════════════════════════════════════════


class TestBorrowBook:
    @pytest.mark.smoke
    def test_successful_borrow_book(self, library_full):
        record = library_full.borrow_book("M001", "978-1-001")

        assert record.member_id == "M001"
        assert record.isbn == "978-1-001"

        book = library_full.get_book("978-1-001")
        assert book.available_copies == 2

    @pytest.mark.negative
    def test_borrow_book_by_unknown_member_raises_error(self, library_full):
        with pytest.raises(ValueError):
            library_full.borrow_book("M999", "978-1-001")

    @pytest.mark.negative
    def test_borrow_unknown_book_raises_error(self, library_full):
        with pytest.raises(ValueError):
            library_full.borrow_book("M001", "978-9-999")

    @pytest.mark.boundary
    def test_borrow_same_book_twice_raises_error(self, library_full):
        library_full.borrow_book("M001", "978-1-001")

        with pytest.raises(ValueError):
            library_full.borrow_book("M001", "978-1-001")


class TestRegisterMember:
    @pytest.mark.smoke
    def test_register_member(self, empty_library, member_anna):
        empty_library.register_member(member_anna)

        member = empty_library.get_member("M001")

        assert member is not None
        assert member.name == "Анна Иванова"

    @pytest.mark.negative
    def test_register_duplicate_member_raises_error(self, empty_library, member_anna):
        empty_library.register_member(member_anna)

        with pytest.raises(ValueError):
            empty_library.register_member(member_anna)