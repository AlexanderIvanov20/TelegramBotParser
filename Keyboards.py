from telebot.types import *


def keyboard_switch_on_start():
    keyboard = InlineKeyboardMarkup(row_width=1)
    button_switch = InlineKeyboardButton(
        text='🔍 Поиск по названию компании', switch_inline_query_current_chat='')
    keyboard.add(button_switch)
    return keyboard


def pagination_keyboard(prev_btn=None, next_btn=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    button_prev = InlineKeyboardButton(text='⬅️', callback_data='prev')
    button_next = InlineKeyboardButton(text='➡️', callback_data='next')

    if prev_btn is False:
        keyboard.add(button_next)
    elif next_btn is False:
        keyboard.add(button_prev)
    else:
        keyboard.add(button_prev, button_next)
    return keyboard
