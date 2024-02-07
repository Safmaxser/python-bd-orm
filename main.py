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

    def get_shops(self, search):
        sql_query = self.session.query(Book.title, Shop.name,
                                       Sale.price*Sale.count, Sale.date_sale)
        sql_query = sql_query.select_from(Shop)
        sql_query = sql_query.join(Stock).join(Book).join(Publisher).join(Sale)
        if search.isdigit():
            sql_query = sql_query.filter(Publisher.id == search).all()
        else:
            sql_query = sql_query.filter(Publisher.name == search).all()    
        for sqls in sql_query:
            print(f"{sqls[0] : <40} | {sqls[1] : <10} | {sqls[2] : <8} | "
                  f"{sqls[3].strftime('%d-%m-%Y')}")


if __name__ == '__main__':
    book_shop = BookShop(drive, database, connect_name, port, user, password)
    book_shop.connect()
    book_shop.create_tables()
    book_shop.open_session()

    book_shop.load_data('tests_data.json')
    search = input('Введите имя или id "Издателя": ')
    book_shop.get_shops(search)

    book_shop.close_session()