import re

def get_product_id(text):
    '''Extracts product id from text.'''

    regex = r'(?<=Артикул: )[0-9]+'
    id = re.search(regex, text)
    if id:
        id = id.group()

    return id

def get_product_title(text):
    '''Gets product title from text.'''

    regex = r'(?<=Наименование: ).+'
    title = re.search(regex, text)
    if title:
        title = title.group().rstrip(' ')
    
    return title


def get_name(text):
    '''Gets name from text.'''

    regex = r'(?<=ФИО: ).+'
    name = re.search(regex, text)
    if name:
        name = name.group().rstrip(' ')
    
    return name


def get_number(text):
    '''Gets phone number from text.'''

    regex = r'(?<=Номер телефона: ).+'
    number = re.search(regex, text)
    if number:
        number = number.group().rstrip(' ')
    
    return number