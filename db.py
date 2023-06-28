import sqlite3
import logging

database = sqlite3.connect("store.db")
cursor = database.cursor()

try:
    # creates table with products available
    cursor.execute('''CREATE TABLE products (
        unique_id INTEGER UNIQUE,
        category INTEGER,
        title VARCHAR (100),
        description TEXT,
        url VARCHAR (50)
    )''')
except:
    logging.error('Products table already exists.')


# cursor.execute("DELETE FROM products WHERE unique_id=2")
# database.commit()