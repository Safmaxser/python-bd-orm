import sqlalchemy
from sqlalchemy.orm import sessionmaker
from models import create_tables_models, Publisher, Book, Shop, Stock, Sale
import json
import os
from dotenv import load_dotenv

load_dotenv()
drive = os.getenv('DB_DRIVER')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
connect_name = os.getenv('DB_CONNECT_NAME')
port = os.getenv('DB_PORT')
database = os.getenv('DB_DATABASE')


class BookShop:

    def __init__(self, drive, database, connect_name, port, user, password):
        self.drive = drive
        self.database = database
        self.connect_name = connect_name
        self.port = port
        self.user = user
        self.password = password

    def connect(self):
        DSN = f'{self.drive}://{self.user}:{self.password}@{self.connect_name}:{self.port}/{self.database}'
        self.engine = sqlalchemy.create_engine(DSN)

    def create_tables(self):
        create_tables_models(self.engine)

    def open_session(self):
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def close_session(self):
        self.session.close()

    def load_data(self, file):
        with open(file, encoding="utf-8") as f:
            json_data = json.load(f)  
        list_data = []
        for dict_data in json_data:
            model = dict_data.get('model')
            pk = dict_data.get('pk')
            fields = dict_data.get('fields')
            if model == 'publisher':
                list_data.append(Publisher(id=pk, name=fields.get('name')))        
            elif model == 'book':
                list_data.append(Book(id=pk, title=fields.get('title'),
                                    id_publisher=fields.get('id_publisher')))    
            elif model == 'shop':
                list_data.append(Shop(id=pk, name=fields.get('name')))   
            elif model == 'stock':
                list_data.append(Stock(id=pk, id_book=fields.get('id_book'),
                                    id_shop=fields.get('id_shop'),
                                    count=fields.get('count')))  
            elif model == 'sale':
                list_data.append(Sale(id=pk, price=fields.get('price'),
                                    date_sale=fields.get('date_sale'),
                                    id_stock=fields.get('id_stock'),
                                    count=fields.get('count'),)) 
        self.session.add_all(list_data)
        self.session.commit()

    def publisher_output(self, search):
        for sel_stock in (self.session.query(Stock).join(Book).join(Publisher).
                          filter(Publisher.name.ilike(f'%{search}%')).all()):
            sql_query = (self.session.query(Sale).join(Stock).
                         filter(Sale.stock == sel_stock).all())
            if len(sql_query) > 0:
                for sel_sale in sql_query: 
                    print("{0:<40s} | {1:<10s} | {2:^8f} | {3:^10s}".
                        format(sel_stock.book.title, sel_stock.shop.name,
                                sel_sale.price*sel_sale.count,
                                sel_sale.date_sale.strftime("%d.%m.%y %H:%M")))      
            else:
                print("{0:<40s} | {1:<10s} | {2:^8s} | {3:^10s}".
                    format(sel_stock.book.title,
                            sel_stock.shop.name, 'None', 'None')) 


if __name__ == '__main__':
    book_shop = BookShop(drive, database, connect_name, port, user, password)
    book_shop.connect()
    book_shop.create_tables()
    book_shop.open_session()

    book_shop.load_data('tests_data.json')
    search = input('Введите строку поиска по "Издателю": ')
    book_shop.publisher_output(search)

    book_shop.close_session()