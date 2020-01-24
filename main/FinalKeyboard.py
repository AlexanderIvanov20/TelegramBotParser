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


# def bottom_menu():
#     keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
#                                    one_time_keyboard=True,
#                                    selective=True, row_width=3)
#     button = KeyboardButton(text='📄 Вывести меню')
#     keyboard.add(button)
#     return keyboard


def pagination_keyboard(right=None, left=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = (
        InlineKeyboardButton(text='⬅️', callback_data='left'),
        InlineKeyboardButton(text='➡️', callback_data='right'),
        InlineKeyboardButton(text='📄 Вывести меню', callback_data='menu')
    )

    if right is False and left is False:
        keyboard.add(buttons[-1])
    elif right is False:
        keyboard.add(buttons[0], buttons[-1])
    elif left is False:
        keyboard.add(buttons[-1], buttons[1])
    else:
        keyboard.add(*buttons)
    return keyboard
