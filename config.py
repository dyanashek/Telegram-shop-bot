import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# manager's id (redirect users to him)
MANAGER_ID = os.getenv('MANAGER_ID')

# bot's ID
BOT_ID = os.getenv('BOT_ID')

#spreads name
SPREAD = os.getenv('SPREAD')

PRODUCTS_SHEET = os.getenv('PRODUCTS_SHEET')

USERS_SHEET = os.getenv('USERS_SHEET')

PRODUCTS_AMOUNT = int(os.getenv('PRODUCTS_AMOUNT'))

MANAGER_USERNAME = os.getenv('MANAGER_USERNAME')

START_IMAGE_ID = 'https://disk.yandex.ru/i/Bkq1wEgMlBkurQ'

CATEGORIES = {
    'верхняя одежда' : 1,
    'платья' : 2,
    'топы' : 3,
    'брюки' : 4,
    'сумки' : 5,
    'аксессуары' : 6,
    'обувь' : 7,
    }

START_TEXT = '''
            \nПриветствуем вас в чат-боте *Two2Lives*!\
            \nЗдесь вы можете просматривать и заказывать брендовую одежду и аксессуары.\
            \nВоспользуйтесь возможностью просмотреть каталог и оформить заказ в несколько кликов. Мы с удовольствием доставим ваш выбранный товар.\
            \nПри возникновении вопросов, обращайтесь к нашим операторам. Начните свои шопинговые приключения прямо сейчас в чат-боте Two2Lives!\
            '''

ABOUT_TEXT = '''
            \n*Two2lives* - территория ресейла брендовой одежды и аксессуаров\
            \nЗдесь вы можете посмотреть наш каталог и заказать одежду и аксессуары.\
            \nПо вопросам покупок и сотрудничества -  @imanitos\
            \n\
            \nАдрес шоурума в Москве: Большой Харитоньевский пер., д10/1\
            '''

INSTAGRAM_URL = 'https://instagram.com/two2lives_?igshid=MzRlODBiNWFlZA=='
TELEGRAM_CHANNEL = 'https://t.me/two2lives'