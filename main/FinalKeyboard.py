from telebot.types import *


def main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = (
        InlineKeyboardButton(text='🔍 Поиск по названию',
                             switch_inline_query_current_chat=''),
        InlineKeyboardButton(text='🔍 Поиск по ссылке',
                             callback_data='by_link'),
        InlineKeyboardButton(text='👑 VIP', callback_data='vip')
    )
    keyboard.add(*buttons)
    return keyboard


def no_vip_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    button = InlineKeyboardButton(text='💵 Преобрести подписку',
                                  callback_data='no_vip')
    keyboard.add(button)
    return keyboard


def bottom_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                   one_time_keyboard=True,
                                   selective=True, row_width=3)
    button = KeyboardButton(text='📄 Вывести меню')
    keyboard.add(button)
    return keyboard
