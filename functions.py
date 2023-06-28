import gspread
import sqlite3
import itertools
import telebot
import logging
import inspect
import asyncio
import utils
import datetime

import config

service_acc = gspread.service_account(filename='service_account.json')
spread = service_acc.open(config.SPREAD)
work_sheet = spread.worksheet(config.PRODUCTS_SHEET)
users_sheet = spread.worksheet(config.USERS_SHEET)

bot = telebot.TeleBot(config.TELEGRAM_TOKEN)

def check_if_unique_id():
    '''Checks if all IDs are unique. Return True if they are.'''

    ids = work_sheet.col_values(1)

    if len(ids) == len(set(ids)):
        return True

    return False


def count_rows():
    '''Counts filled rows in google sheet.'''

    return len(work_sheet.col_values(1))


def get_all_products():
    '''Gets information about all added products.'''

    return work_sheet.get_all_values()[1::]


def check_if_in_db(unique_id):
    '''Checks if id already in database.'''

    database = sqlite3.connect("store.db")
    cursor = database.cursor()

    product = cursor.execute(f"SELECT * FROM products WHERE unique_id=?", (unique_id,)).fetchall()

    cursor.close()
    database.close()

    if product != []:
        product = list(product[0])
    
    return product


def update_product_info(unique_id, category, title, description, url, id):
    '''Updates information about the product in database.'''

    database = sqlite3.connect("store.db")
    cursor = database.cursor()

    try:
        cursor.execute(f'''UPDATE products
                        SET unique_id=?, category=?, title=?, 
                        description=?, url=?
                        WHERE unique_id=?
                        ''', (unique_id, category, title, description, url, unique_id,)
                        )
        database.commit()
        cursor.close()
        database.close()

        logging.info(f'{inspect.currentframe().f_code.co_name}: Обновлены данные о продукте {unique_id}.')

    except Exception as ex:

        text = f'Не удалось обновить данные о продукте {unique_id}. Проверьте поля заголовка, описания, ссылки на наличие недопустимых символов'
        send_error_message(id, text)

        logging.error(f'{inspect.currentframe().f_code.co_name}: Не удалось обновить данные о продукте {unique_id}: {ex}.')


def add_product_info(unique_id, category, title, description, url, id):
    '''Adds information about the product in database.'''

    database = sqlite3.connect("store.db")
    cursor = database.cursor()

    try:
        cursor.execute(f'''
            INSERT INTO products (unique_id, category, title, description, url)
            VALUES (?, ?, ?, ?, ?)
            ''', (unique_id, category, title, description, url,)
            )
        database.commit()
        cursor.close()
        database.close()

        logging.info(f'{inspect.currentframe().f_code.co_name}: Добавлены данные о продукте {unique_id}.')

    except Exception as ex:

        text = f'Не удалось добавить данные о продукте {unique_id}. Проверьте поля заголовка, описания, ссылки на наличие недопустимых символов'
        send_error_message(id, text)

        logging.error(f'{inspect.currentframe().f_code.co_name}: Не удалось добавить данные о продукте {unique_id}: {ex}.')


def get_all_database_ids():
    '''Gets all ids from database.'''

    database = sqlite3.connect("store.db")
    cursor = database.cursor()

    ids = cursor.execute("SELECT DISTINCT unique_id FROM products").fetchall()

    cursor.close()
    database.close()

    if ids:
        ids = itertools.chain.from_iterable(ids)
    
    return set(ids)


def get_all_sheet_ids():
    '''Gets all ids from google sheet.'''

    ids = work_sheet.col_values(1)[1::]

    ids_numbers = set()

    for id in ids:
        ids_numbers.add(int(id))

    return ids_numbers


def update_database(all_products, id):
    for product in all_products:
        try:
            unique_id = int(product[0])
        except:
            text = f'ID {product[0]} не соответствует формату, должен содержать только цифры. Обновление данных прервано.'
            send_error_message(id, text)
            break

        for category in config.CATEGORIES:
            if category in product[1].lower():
                category = config.CATEGORIES[category]
                break
        else:
            text = f'Не найдена категория {product[1]}. Обновление данных прервано.'
            send_error_message(id, text)
            break

        title = product[2]
        description = product[3]
        url = product[4].replace(' ', '')

        database_product = check_if_in_db(unique_id)
        if database_product:
            if [unique_id, category, title, description, url] != database_product:
                update_product_info(unique_id, category, title, description, url, id)

        else:
            add_product_info(unique_id, category, title, description, url, id)

    else:
        return True


def delete_from_db(unique_id):
    '''Deletes id from database.'''

    database = sqlite3.connect("store.db")
    cursor = database.cursor()

    cursor.execute("DELETE FROM products WHERE unique_id=?", (unique_id,))
    
    database.commit()
    cursor.close()
    database.close()

    logging.info(f'{inspect.currentframe().f_code.co_name}: Удалены данные о продукте {unique_id}.')


def compare_ids():
    '''Compares ids from database and google sheet. Deletes that already not in google sheet.'''

    sheet_ids = get_all_sheet_ids()
    database_ids = get_all_database_ids()

    if database_ids:
        waste_ids = database_ids - sheet_ids
        for id in waste_ids:
            delete_from_db(id)


def move_info_from_google(user_id):
    '''Updates information in database according to google sheets.'''
    all_products = get_all_products()
    if update_database(all_products, user_id):
        compare_ids()

        try:
            bot.send_message(chat_id=user_id,
                            text='Данные обновлены.',
                            )
            
        except Exception as ex:
            logging.error(f'{inspect.currentframe().f_code.co_name}: Не удалось отправить сообщение пользователю {user_id}: {ex}.')


def send_error_message(user_id, text):
    '''Sends error message to manager.'''

    try:
        bot.send_message(chat_id=user_id,
                         text=text,
                         )
    except Exception as ex:
        logging.error(f'{inspect.currentframe().f_code.co_name}: Не удалось отправить сообщение пользователю {user_id}: {ex}.')


def select_products_by_category(category):
    '''Selects products from database by category.'''

    database = sqlite3.connect("store.db")
    cursor = database.cursor()

    products = cursor.execute(f"SELECT * FROM products WHERE category={category}").fetchall()

    cursor.close()
    database.close()

    return products


def construct_group_media(products, page):
    group_media = []

    for product in products[config.PRODUCTS_AMOUNT*page-config.PRODUCTS_AMOUNT:config.PRODUCTS_AMOUNT*page]:
        group_media.append(telebot.types.InputMediaPhoto(media=product[4]))
    
    return group_media
    

async def delete_message(chat_id, message_id):
    '''Deletes message by its id.'''

    try:
        bot.delete_message(chat_id, message_id) 
    except:
        pass


async def delete_messages(chat_id, message_ids):
    '''Creates tasks to delete messages.'''

    tasks = []
    message_ids = message_ids.split('/')
    for message_id in message_ids:
        tasks.append(asyncio.create_task(delete_message(chat_id, message_id)))

    for task in tasks:
        await task


def delete_messages_wrapper(chat_id, message_ids):
    '''Wraps delete_messages function to run in thread.'''

    asyncio.run(delete_messages(chat_id, message_ids))


def get_product_info(product_id):
    '''Gets information about product by its id.'''

    database = sqlite3.connect("store.db")
    cursor = database.cursor()

    product_info = cursor.execute(f"SELECT * FROM products WHERE unique_id=?", (product_id,)).fetchall()

    cursor.close()
    database.close()

    if product_info:
        product_info = product_info[0]
    
    return product_info


def handle_order(text, user_id, username):
    '''Handles information, when user confirms order.'''

    product_id = utils.get_product_id(text)
    title = utils.get_product_title(text)
    name = utils.get_name(text)
    number = utils.get_number(text)

    inform_manager(product_id, title, name, number, user_id, username)
    fill_user_orders(product_id, title, name, number, user_id, username)


def inform_manager(product_id, title, name, number, user_id, username):
    '''Informs manager about order.'''

    reply_text = f'''
                \nПользователь @{username} (ID: {user_id}) совершил заказ:\
                \n\
                \n*Артикул:* {product_id}\
                \n*Наименование:* {title}\
                \n*ФИО:* {name}\
                \n*Номер телефона:* {number}\
                '''

    try:
        bot.send_message(chat_id=config.MANAGER_ID,
                         text=reply_text,
                         parse_mode='Markdown'
                         )
    except:
        reply_text = f'''
                \nПользователь @{username} (ID: {user_id}) совершил заказ:\
                \n\
                \nАртикул: {product_id}\
                \nНаименование: {title}\
                \nФИО: {name}\
                \nНомер телефона: {number}\
                '''
        
        try:
            bot.send_message(chat_id=config.MANAGER_ID,
                         text=reply_text,
                         )
        except Exception as ex:
            logging.error(f'{inspect.currentframe().f_code.co_name}: Не удалось отправить сообщение менеджеру: {ex}. {reply_text}')


def users_empty_row():
    '''Gets first empty row in users table.'''

    return len(users_sheet.col_values(1)) + 1


def fill_user_orders(product_id, title, name, number, user_id, username):
    '''Fills users orders in the google sheet.'''

    row = users_empty_row()
    fill_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).strftime("%d.%m.%Y %H:%M")

    order_info = [user_id, username, name, number, product_id, title, fill_time]

    users_sheet.update(f'A{row}:G{row}', [order_info])