import telebot
import threading
from telebot.types import *
from Parser import Parser
from Keyboards import *


# Iniialize Bot and Parser objects
TOKEN = '917181533:AAHB0gNsOFCw4nHYpRyrDGDfQQySzFu7YMI'
bot = telebot.TeleBot(TOKEN)
data = {}


# On start command output inline menu
@bot.message_handler(commands=['start'])
def on_start(message: Message) -> None:
    parser = Parser()
    data[f'{message.chat.id}_parser'] = parser
    keyboard = keyboard_switch_on_start()
    bot.send_message(chat_id=message.chat.id,
                     text='Выберете нужный Вам пункт', reply_markup=keyboard)


# If inline query is null
@bot.inline_handler(func=lambda query: len(query.query) == 0)
def default_query(query) -> None:
    response = InlineQueryResultArticle(
        id='1', title='Название компании',
        input_message_content=InputTextMessageContent(
            message_text='Название компании'),
        description='Начните вводить название и выберете из предложеных вариантов')
    bot.answer_inline_query(inline_query_id=query.id, results=[response])


# Create drop-up menu
@bot.inline_handler(func=lambda query: True)
def query_get(query) -> None:
    try:
        user_message = query.query
        possible_variants = data[f'{query.from_user.id}_parser'].get_variants(user_message)[
            'items']
        print(possible_variants)
        final_inline_query = []

        # Add point to drop-up menu
        for item in possible_variants:
            even_owner = item['owner']
            response = InlineQueryResultArticle(id=f"{even_owner['id']}", title=f"{even_owner['nameWithoutBrand']}", input_message_content=InputTextMessageContent(
                f"/{even_owner['nameWithoutBrand']}/"), description=f"{even_owner['timeOnSite']}. {even_owner['address']['country']}-{even_owner['address']['town']}")
            final_inline_query.append(response)

        bot.answer_inline_query(inline_query_id=query.id,
                                results=final_inline_query)
    except Exception as er:
        print(er)


# Output all reviews on current company
@bot.message_handler(content_types=['text'])
def get_reviews(message: Message) -> None:
    if (message.text)[0] == '/' and (message.text)[-1] == '/':
        user_message = (message.text)[1:-1]
        bot.send_message(chat_id=message.chat.id,
                         text='⌚️ Подождите немного... Идет сбор данных')
        print(user_message)
        result_string = ''

        try:
            final_dict = data[f'{message.chat.id}_parser'].get_ads(
                user_message)
        except KeyError as k:
            data[f'{message.chat.id}_parser'] = Parser()
            final_dict = data[f'{message.chat.id}_parser'].get_ads(
                user_message)

        data[f'{message.chat.id}_final_dict'] = final_dict

        if data[f'{message.chat.id}_parser'].company_exist:
            if data[f'{message.chat.id}_parser'].reviews_condition:
                data[f'{message.chat.id}_prev'] = 0
                data[f'{message.chat.id}_next'] = 5

                prev_btn = data[f'{message.chat.id}_prev']
                next_btn = data[f'{message.chat.id}_next']
                final_dict = final_dict[prev_btn:next_btn]

                for even in final_dict:
                    result_string += f"📅 Дата: {even['date']}\n📍 Откуда: {even['town_from']}\n📍 Куда: {even['town_to']}\n📄 Отзыв: {even['short']}\n\n"
                bot.delete_message(chat_id=message.chat.id,
                                   message_id=message.message_id + 1)
                bot.send_message(
                    chat_id=message.chat.id, text=result_string,
                    reply_markup=pagination_keyboard(prev_btn=False))
            else:
                bot.delete_message(chat_id=message.chat.id,
                                   message_id=message.message_id + 1)
                bot.send_message(chat_id=message.chat.id,
                                 text='У данной компании нет отзывов\nПопробуйте еще раз ввести название', reply_markup=keyboard_switch_on_start())
        else:
            bot.delete_message(chat_id=message.chat.id,
                               message_id=message.message_id + 1)
            bot.send_message(chat_id=message.chat.id,
                             text='Такой компании не существует\nПопробуйте еще раз ввести название', reply_markup=keyboard_switch_on_start())
    # Else block
    else:
        bot.send_message(chat_id=message.chat.id,
                         text='Я Вас не понимаю... Введенный текст не корректен...')


# Get all callbacks
@bot.callback_query_handler(func=lambda call: True)
def answer_callback(call: CallbackQuery) -> None:
    # On previous button click
    if call.data == 'prev':
        if data[f'{call.from_user.id}_prev'] - 5 <= 0:
            data[f'{call.from_user.id}_prev'] = 0
            data[f'{call.from_user.id}_next'] = 5
            keyboard = pagination_keyboard(prev_btn=False)
        elif data[f'{call.from_user.id}_prev'] - 5 > 0:
            data[f'{call.from_user.id}_prev'] -= 5
            data[f'{call.from_user.id}_next'] -= 5
            keyboard = pagination_keyboard()

        final_dict = data[f'{call.message.chat.id}_final_dict']
        prev_btn = data[f'{call.message.chat.id}_prev']
        next_btn = data[f'{call.message.chat.id}_next']
        final_dict = final_dict[prev_btn:next_btn]
        template_result_string(final_dict=final_dict,
                               keyboard=keyboard, call=call)

    # On next button click
    if call.data == 'next':
        final_dict = data[f'{call.message.chat.id}_final_dict']

        if len(final_dict) - data[f'{call.from_user.id}_next'] <= 5:
            final_dict = final_dict[data[f'{call.from_user.id}_next']:]
            data[f'{call.from_user.id}_prev'] += 5
            data[f'{call.from_user.id}_next'] += 5

            keyboard = pagination_keyboard(next_btn=False)
        elif data[f'{call.from_user.id}_next'] + 5 < len(final_dict):
            data[f'{call.from_user.id}_prev'] += 5
            data[f'{call.from_user.id}_next'] += 5

            prev_btn = data[f'{call.message.chat.id}_prev']
            next_btn = data[f'{call.message.chat.id}_next']
            final_dict = final_dict[prev_btn:next_btn]

            keyboard = pagination_keyboard()
        elif data[f'{call.from_user.id}_next'] + 5 == len(final_dict):
            data[f'{call.from_user.id}_prev'] += 5
            data[f'{call.from_user.id}_next'] += 5

            prev_btn = data[f'{call.message.chat.id}_prev']
            next_btn = data[f'{call.message.chat.id}_next']
            final_dict = final_dict[prev_btn:next_btn]

            keyboard = pagination_keyboard(next_btn=False)
        else:
            print('Else block. Next')
            prev_btn = data[f'{call.message.chat.id}_prev']
            next_btn = data[f'{call.message.chat.id}_next']
            final_dict = final_dict[prev_btn:next_btn]

            keyboard = pagination_keyboard(next_btn=False)

        template_result_string(final_dict=final_dict,
                               keyboard=keyboard, call=call)


@bot.message_handler(func=lambda message: True)
def else_block(message):
    bot.send_message(chat_id=message.chat.id,
                     text='Я Вас не понимаю... Введите корректное значение...')


def template_result_string(final_dict: dict, keyboard, call: CallbackQuery) -> None:
    result_string = ''
    for even in final_dict:
        result_string += f"📅 Дата: {even['date']}\n📍 Откуда: {even['town_from']}\n📍 Куда: {even['town_to']}\n📄 Отзыв: {even['short']}\n\n"
    bot.edit_message_text(text=result_string, chat_id=call.from_user.id,
                          message_id=call.message.message_id, 
                          reply_markup=keyboard)


bot.polling(none_stop=True)
