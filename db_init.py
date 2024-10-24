from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from typing import List, Optional

# 創建數據庫引擎
engine = create_engine('sqlite:///books.db', echo=True)

# 創建基類
Base = declarative_base()

# 定義模型
class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    books = relationship('Book', back_populates='category')

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    price = Column(Float)
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship('Category', back_populates='books')

# 創建表格
Base.metadata.create_all(engine)

# 創建會話
Session = sessionmaker(bind=engine)

class BookRepository:
    def __init__(self):
        self.session = Session()

    def add_category(self, name: str) -> Category:
        category = Category(name=name)
        self.session.add(category)
        self.session.commit()
        return category

    def add_book(self, title: str, author: str, price: float, category_name: str) -> Book:
        category = self.session.query(Category).filter_by(name=category_name).first()
        if not category:
            category = self.add_category(category_name)
        book = Book(title=title, author=author, price=price, category=category)
        self.session.add(book)
        self.session.commit()
        return book

    def get_all_books(self) -> List[Book]:
        return self.session.query(Book).all()

    def get_book_by_title(self, title: str) -> Optional[Book]:
        return self.session.query(Book).filter_by(title=title).first()

    def update_book(self, book_id: int, title: Optional[str] = None, 
                    author: Optional[str] = None, price: Optional[float] = None, 
                    category_name: Optional[str] = None):
        book = self.session.query(Book).filter_by(id=book_id).first()
        if book:
            if title:
                book.title = title
            if author:
                book.author = author
            if price:
                book.price = price
            if category_name:
                category = self.session.query(Category).filter_by(name=category_name).first()
                if not category:
                    category = self.add_category(category_name)
                book.category = category
            self.session.commit()
        return book

    def delete_book(self, book_id: int):
        book = self.session.query(Book).filter_by(id=book_id).first()
        if book:
            self.session.delete(book)
            self.session.commit()

    def close(self):
        self.session.close()

# 使用示例
if __name__ == "__main__":
    repo = BookRepository()

    # 添加書籍
    book1 = repo.add_book("Python程式設計", "張三", 299.99, "程式設計")
    book2 = repo.add_book("數據科學入門", "李四", 399.99, "數據分析")

    # 查詢所有書籍
    all_books = repo.get_all_books()
    for book in all_books:
        print(f"書名: {book.title}, 作者: {book.author}, 價格: {book.price}, 類別: {book.category.name}")

    # 更新書籍
    updated_book = repo.update_book(book1.id, price=329.99, category_name="計算機科學")
    print(f"更新後的書籍: {updated_book.title}, 新價格: {updated_book.price}, 新類別: {updated_book.category.name}")

    # 刪除書籍
    repo.delete_book(book2.id)

    # 再次查詢所有書籍
    remaining_books = repo.get_all_books()
    print("剩餘書籍:")
    for book in remaining_books:
        print(f"書名: {book.title}, 作者: {book.author}, 價格: {book.price}, 類別: {book.category.name}")

    repo.close()