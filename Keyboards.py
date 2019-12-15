from telebot.types import *


def keyboard_switch_on_start():
    keyboard = InlineKeyboardMarkup(row_width=1)
    button_switch = InlineKeyboardButton(
        text='Поиск по названию компании', switch_inline_query_current_chat='')
    keyboard.add(button_switch)
    return keyboard
