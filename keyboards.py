from telebot import types
import math

import config

def main_keyboard():
    """Generates main keyboard that have option of filling form, check instagram."""

    keyboard = types.InlineKeyboardMarkup()
    katalog = types.InlineKeyboardButton('🛒 Каталог', callback_data = f'katalog')
    keyboard.add(types.InlineKeyboardButton('👩‍💼 Менеджер', url = f'https://t.me/{config.MANAGER_USERNAME}'))
    about = types.InlineKeyboardButton('ℹ️ О нас', callback_data = f'about')
    keyboard.add(katalog, about)
    return keyboard


def reply_keyboard():
    """Generates main keyboard that have option of filling form, check instagram."""

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    katalog = types.KeyboardButton('🛒 Каталог')
    about = types.KeyboardButton('ℹ️ О нас')
    keyboard.add(katalog, about)
    return keyboard


def katalog_keyboard():
    """Generates main keyboard that have option of filling form, check instagram."""

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Верхняя одежда ,жакеты 🧥', callback_data = f'category_1_1_0'))
    keyboard.add(types.InlineKeyboardButton('Платья и юбки 👗', callback_data = f'category_2_1_0'))
    keyboard.add(types.InlineKeyboardButton('Сумки 👜', callback_data = f'category_5_1_0'))
    keyboard.add(types.InlineKeyboardButton('Брюки и комбинезоны, шорты 👖', callback_data = f'category_4_1_0'))
    keyboard.add(types.InlineKeyboardButton('Топы / блузы /рубашки и футболки 👔', callback_data = f'category_3_1_0'))
    keyboard.add(types.InlineKeyboardButton('Головные уборы и аксессуары 🧢', callback_data = f'category_6_1_0'))
    keyboard.add(types.InlineKeyboardButton('Обувь 👟', callback_data = f'category_7_1_0'))
    keyboard.add(types.InlineKeyboardButton('⬅️ Назад', callback_data = f'back_main'))
    return keyboard


def products_keyboard(products, category, page, message_id):
    keyboard = types.InlineKeyboardMarkup(row_width=5)

    pages = math.ceil(len(products) / config.PRODUCTS_AMOUNT)
    for num, product in enumerate(products[config.PRODUCTS_AMOUNT*page-config.PRODUCTS_AMOUNT:config.PRODUCTS_AMOUNT*page]):
        keyboard.add(types.InlineKeyboardButton(f'{num + 1 + config.PRODUCTS_AMOUNT * (page - 1)}. {product[2]}', callback_data = f'product_{product[0]}_{message_id}_{category}_{page}'))

    begin_callback = f'category_{category}_1_{message_id}'
    back_callback = f'category_{category}_{page - 1}_{message_id}'
    forward_callback = f'category_{category}_{page + 1}_{message_id}'
    end_callback = f'category_{category}_{pages}_{message_id}'
    
    if page == 1:
        begin_callback = 'not_available'
        back_callback = 'not_available'
    elif page == pages:
        forward_callback = 'not_available'
        end_callback = 'not_available'

    if len(products) > config.PRODUCTS_AMOUNT:
        begin = types.InlineKeyboardButton('<<<', callback_data = begin_callback)
        back = types.InlineKeyboardButton('<-', callback_data = back_callback)
        page = types.InlineKeyboardButton(f'{page}/{pages}', callback_data = 'not_available')
        forward = types.InlineKeyboardButton('->', callback_data = forward_callback)
        end = types.InlineKeyboardButton('>>>', callback_data = end_callback)
        keyboard.add(begin, back, page, forward, end)
    
    keyboard.add(types.InlineKeyboardButton('⬅️ Назад', callback_data = f'back_katalog_{message_id}'))

    return keyboard


def order_keyboard(category, page, product_id, title):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Заказать', callback_data = f'order_{product_id}_{title}'))
    keyboard.add(types.InlineKeyboardButton('⬅️ Назад', callback_data = f'category_{category}_{page}_0'))
    return keyboard


def back_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Мы в Instagram', url = config.INSTAGRAM_URL))
    keyboard.add(types.InlineKeyboardButton('Мы в Telegram', url = config.TELEGRAM_CHANNEL))
    keyboard.add(types.InlineKeyboardButton('⬅️ Назад', callback_data = f'back_main'))
    return keyboard

def back_main_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('🏠 Главное меню', callback_data = f'back_home'))
    return keyboard

def enter_name_keyboard():
    """Makes a reply to a message that asks about the name."""
    return types.ForceReply(input_field_placeholder=f'Введите Ваши ФИО')


def enter_phone_keyboard():
    """Makes a reply to a message that asks about the name."""
    return types.ForceReply(input_field_placeholder=f'Введите Ваш номер телефона')


def confirm_keyboard():
    """Generates keyboard with 'confirm name' and self input options."""

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('✅ Подтвердить', callback_data = f'confirm'))
    keyboard.add(types.InlineKeyboardButton('❌ Отменить', callback_data = f'cancel'))
    return keyboard