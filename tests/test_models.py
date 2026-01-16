from sqlalchemy import Integer, String
from app.models import Book

def test_book_model_structure():
    assert Book.__tablename__ == "books"

    # require all expected attributes
    for attr in ["id", "title", "author", "description", "year"]:
        assert hasattr(Book, attr)

    # check column types
    assert isinstance(Book.__table__.c.id.type, Integer)
    assert isinstance(Book.__table__.c.title.type, String)
    assert isinstance(Book.__table__.c.author.type, String)
    assert isinstance(Book.__table__.c.description.type, String)
    assert isinstance(Book.__table__.c.year.type, Integer)
