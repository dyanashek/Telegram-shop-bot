import telebot
import threading

import config
import utils
import functions
import keyboards
import logging


logging.basicConfig(level=logging.ERROR, 
                    filename="py_log.log", 
                    filemode="w", 
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    )

bot = telebot.TeleBot(config.TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    # bot.send_message(chat_id=message.chat.id,
    #                  text='Приветственное сообщение, к которому прикрепляется клавиатура, отображающаяся у пользователя *(reply-клавиатура)*.',
    #                  reply_markup=keyboards.reply_keyboard(),
    #                  parse_mode='Markdown',
    #                  )
    
    bot.send_photo(chat_id=message.chat.id,
                   photo=config.START_IMAGE_ID,
                   caption=config.START_TEXT,
                   parse_mode='Markdown',
                   )
    
    bot.send_message(chat_id=message.chat.id,
                   text='Выберите интересующий Вас раздел:',
                   reply_markup=keyboards.main_keyboard(),
                   parse_mode='Markdown',
                   )

@bot.message_handler(commands=['menu'])
def menu_message(message):
    bot.send_message(chat_id=message.chat.id,
                   text='Выберите интересующий Вас раздел:',
                   reply_markup=keyboards.main_keyboard(),
                   parse_mode='Markdown',
                   )


@bot.message_handler(commands=['update'])
def start_message(message):
    if str(message.from_user.id) in config.MANAGER_ID:
        if functions.check_if_unique_id():
            chat_id = message.chat.id
            threading.Thread(daemon=True, target=functions.move_info_from_google, args=(chat_id,)).start()

        else:
            bot.send_message(chat_id=message.chat.id,
                             text='В таблице присутствуют неуникальные ID - обновление данных невозможно.',
                             )
            
    else:
        bot.send_message(chat_id=message.chat.id,
                             text='В таблице присутствуют неуникальные ID - обновление данных невозможно.',
                             )


@bot.callback_query_handler(func = lambda call: True)
def callback_query(call):
    """Handles queries from inline keyboards."""

    # getting message's and user's ids
    message_id = call.message.id
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    user_username = call.from_user.username

    call_data = call.data.split('_')
    query = call_data[0]

    if query == 'katalog':

        try:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
        except:
            pass

        bot.send_message(chat_id=chat_id,
                            text='Выберите заинтересовавший Вас раздел:',
                            reply_markup=keyboards.katalog_keyboard(),
                            )
    
    elif query == 'about':
        try:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
        except:
            pass

        bot.send_message(chat_id=chat_id,
                   text=config.ABOUT_TEXT,
                   reply_markup=keyboards.back_keyboard(),
                   parse_mode='Markdown',
                   )
        
    elif query == 'category':
        category = int(call_data[1])
        page = int(call_data[2])
        delete_message_id = call_data[3]

        if delete_message_id != '0':
            threading.Thread(daemon=True, target=functions.delete_messages_wrapper, args=(chat_id, delete_message_id,)).start()

        try:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
        except:
            pass

        products = functions.select_products_by_category(category)
        group_media = functions.construct_group_media(products, page)

        try:
            delete_messages = bot.send_media_group(chat_id=chat_id,
                                media=group_media,
                                timeout=30,
                                )
            
            delete_photo = ''
            for delete_message in delete_messages:
                delete_photo += f'{delete_message.id}/'
            delete_photo = delete_photo.rstrip('/')

        except:
            delete_photo = '0'

        bot.send_message(chat_id=chat_id,
                            text='Выберите заинтересовавший Вас товар:',
                            reply_markup=keyboards.products_keyboard(products, category, page, delete_photo),
                            )

    elif query == 'product':
        product_id = call_data[1]
        delete_messages_ids = call_data[2]
        category = call_data[3]
        page = call_data[4]

        if delete_messages_ids != '0':
            threading.Thread(daemon=True, target=functions.delete_messages_wrapper, args=(chat_id, delete_messages_ids,)).start()

        try:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
        except:
            pass
        
        product_info = functions.get_product_info(product_id)
        if product_info:
            title = product_info[2].replace('_', ' ')
            description = product_info[3]
            photo_url = product_info[4]

            bot.send_photo(chat_id=chat_id,
                    photo=photo_url,
                    caption=f'*{title}*\n\n{description}',
                    reply_markup=keyboards.order_keyboard(category, page, product_id, title),
                    parse_mode='Markdown',
                    )
    
    elif query == 'order':
        product_id = call_data[1]
        title = call_data[2]

        try:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
        except:
            pass

        reply_text = f'''
                    \n*Артикул:* {product_id}\
                    \n*Наименование:* {title}\
                    \n\
                    \nВ ответ на это сообщение введите свои ФИО.\
                    '''
        
        bot.send_message(chat_id=chat_id,
                         text=reply_text,
                         reply_markup=keyboards.enter_name_keyboard(),
                         parse_mode='Markdown',
                         )
        
    elif query == 'confirm':
        threading.Thread(daemon=True, 
                         target=functions.handle_order, 
                         args=(call.message.text, 
                               user_id,
                               user_username,
                               ),
                         ).start()
        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text='Ваш заказ принят в работу.\nНаш менеджер с вами свяжется.',
                              reply_markup=keyboards.back_main_keyboard(),
                              )
    
    elif query == 'cancel':
        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text='Заказ отменен.',
                              reply_markup=keyboards.back_main_keyboard(),
                              )
    
    elif query == 'back':
        destination = call_data[1]
        
        if destination == 'main':
            try:
                bot.delete_message(chat_id=chat_id, message_id=message_id)
            except:
                pass

            bot.send_message(chat_id=chat_id,
                   text='Выберите интересующий Вас раздел:',
                   reply_markup=keyboards.main_keyboard(),
                   parse_mode='Markdown',
                   )
        
        elif destination == 'katalog':
            delete_messages_ids = call_data[2]

            threading.Thread(daemon=True, target=functions.delete_messages_wrapper, args=(chat_id, delete_messages_ids,)).start()

            try:
                bot.delete_message(chat_id=chat_id, message_id=message_id)
            except:
                pass
            
            bot.send_message(chat_id=chat_id,
                            text='Выберите заинтересовавший Вас раздел:',
                            reply_markup=keyboards.katalog_keyboard(),
                            )
        
        elif destination == 'home':
            try:
                bot.edit_message_reply_markup(chat_id=chat_id,
                                              message_id=message_id,
                                              reply_markup=telebot.types.InlineKeyboardMarkup(),
                                              )
            except:
                pass

            bot.send_message(chat_id=chat_id,
                   text='Выберите интересующий Вас раздел:',
                   reply_markup=keyboards.main_keyboard(),
                   parse_mode='Markdown',
                   )


@bot.message_handler(content_types=['text'])
def handle_text(message):
    """Handles message with type text."""
    
    if (message.reply_to_message is not None) and\
    (str(message.reply_to_message.from_user.id) == config.BOT_ID):
        
        user_id = message.from_user.id
        chat_id = message.chat.id
        message_id = message.reply_to_message.id

        if 'ФИО.' in message.reply_to_message.text:
            try:
                bot.delete_message(chat_id=chat_id, message_id=message_id)
            except:
                pass

            product_id = utils.get_product_id(message.reply_to_message.text)
            title = utils.get_product_title(message.reply_to_message.text)

            reply_text = f'''
                        \n*Артикул:* {product_id}\
                        \n*Наименование:* {title}\
                        \n*ФИО:* {message.text}\
                        \n\
                        \nВ ответ на это сообщение введите Ваш номер телефона.\
                        '''
            try:
                bot.send_message(chat_id=chat_id,
                            text=reply_text,
                            reply_markup=keyboards.enter_phone_keyboard(),
                            parse_mode='Markdown'
                            )
            except:
                reply_text = f'''
                        \nАртикул: {product_id}\
                        \nНаименование: {title}\
                        \nФИО: {message.text}\
                        \n\
                        \nВ ответ на это сообщение введите Ваш номер телефона.\
                        '''
                
                bot.send_message(chat_id=chat_id,
                            text=reply_text,
                            reply_markup=keyboards.enter_phone_keyboard(),
                            )

        
        elif 'номер телефона' in message.reply_to_message.text:
            try:
                bot.delete_message(chat_id=chat_id, message_id=message_id)
            except:
                pass

            product_id = utils.get_product_id(message.reply_to_message.text)
            title = utils.get_product_title(message.reply_to_message.text)
            name = utils.get_name(message.reply_to_message.text)
            number = message.text

            reply_text = f'''
                        \nВаш заказ:\
                        \n*Артикул:* {product_id}\
                        \n*Наименование:* {title}\
                        \n*ФИО:* {name}\
                        \n*Номер телефона:* {number}\
                        \n\
                        \nДля подтверждения заявки воспользуйтесь кнопкой ниже 👇\
                        '''
            
            try:
                bot.send_message(chat_id=chat_id,
                                text=reply_text,
                                reply_markup=keyboards.confirm_keyboard(),
                                parse_mode='Markdown',
                                )
            except:
                reply_text = f'''
                        \nВаш заказ:\
                        \nАртикул: {product_id}\
                        \nНаименование: {title}\
                        \nФИО: {name}\
                        \nНомер телефона: {number}\
                        \n\
                        \nДля подтверждения заявки воспользуйтесь кнопкой ниже 👇\
                        '''
                
                bot.send_message(chat_id=chat_id,
                                text=reply_text,
                                reply_markup=keyboards.confirm_keyboard(),
                                )

    
    # elif message.text == '🛒 Каталог':
    #     bot.send_message(chat_id=message.chat.id,
    #                         text='Выберите заинтересовавший Вас раздел:',
    #                         reply_markup=keyboards.katalog_keyboard(),
    #                         )
    
    # elif message.text == 'ℹ️ О нас':
    #     bot.send_photo(chat_id=message.chat.id,
    #                photo=config.ABOUT_IMAGE_ID,
    #                caption='*Заголовок \(опционально\)*\n\nТекст о компании: _c возможностью добавления_ [ссылок](https://ya.ru), изображений, видео, файлов\.',
    #                reply_markup=keyboards.back_keyboard(),
    #                parse_mode='MarkdownV2',
    #                )
    

# to get image id
# @bot.message_handler(content_types=['photo'])
# def handle_text(message):
#     print(message)
#     print('')


if __name__ == '__main__':
    # bot.polling(timeout=80)
    while True:
        try:
            bot.polling()
        except:
            pass