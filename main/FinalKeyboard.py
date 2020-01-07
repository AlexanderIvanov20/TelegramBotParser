from telebot.types import *


def main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = (InlineKeyboardButton(text='Поиск по названию',
                                    switch_inline_query_current_chat=''),
               InlineKeyboardButton(text='Поиск по ссылке',
                                    callback_data='by_link'))
    keyboard.add(*buttons)
    return keyboard
