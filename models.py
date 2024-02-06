import sqlalchemy as sq
from sqlalchemy.orm import declarative_base,  relationship
from datetime import datetime


Base = declarative_base()


class Publisher(Base):
    __tablename__ = "publisher"
    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=50), unique=True)

    def __str__(self):
        return f'Publisher {self.id}: {self.name}'


class Book(Base):
    __tablename__ = "book"
    id = sq.Column(sq.Integer, primary_key=True)
    title = sq.Column(sq.String(length=80), unique=True)
    id_publisher = sq.Column(sq.Integer, sq.ForeignKey("publisher.id"),
                             nullable=False)    
    publisher = relationship(Publisher, backref="publisher")

    def __str__(self):
        return (f'Book {self.id}: ({self.title}, {self.id_publisher}, '
                f'{self.publisher})')


class Shop(Base):
    __tablename__ = "shop"
    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=50), unique=True)

    def __str__(self):
        return f'Shop {self.id}: {self.name}'

class Stock(Base):
    __tablename__ = "stock"
    id = sq.Column(sq.Integer, primary_key=True)
    id_book = sq.Column(sq.Integer, sq.ForeignKey("book.id"), nullable=False)
    id_shop = sq.Column(sq.Integer, sq.ForeignKey("shop.id"), nullable=False)
    count = sq.Column(sq.Integer)    
    book = relationship(Book, backref="book")
    shop = relationship(Shop, backref="shop")

    def __str__(self):
        return (f'Stock {self.id}: ({self.id_book}, {self.id_shop}, '
                f'{self.count}, {self.book}, {self.shop})')
    
class Sale(Base):
    __tablename__ = "sale"
    id = sq.Column(sq.Integer, primary_key=True)
    price = sq.Column(sq.DECIMAL(10,2))
    date_sale = sq.Column(sq.DateTime, default=datetime.now)
    id_stock = sq.Column(sq.Integer, sq.ForeignKey("stock.id"), nullable=False)
    count = sq.Column(sq.Integer)    
    stock = relationship(Stock, backref="stock")
    sq.CheckConstraint('price > 0')

    def __str__(self):
        return (f'Sale {self.id}: ({self.price}, {self.date_sale}, '
                f'{self.id_stock}, {self.count}, {self.stock})')


def create_tables_models(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
