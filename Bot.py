import telebot
import threading
from telebot.types import *
from Parser import Parser
from Keyboards import *


# Iniialize Bot and Parser objects
TOKEN = '1030953540:AAFt6-O5laMVRjO8hN1uA-dt7qZPPG0439c'
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
        id='1', title='Название компании', input_message_content=InputTextMessageContent(message_text='Название компании'),
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
@bot.message_handler(func=lambda message: (message.text)[0] == '/' and (message.text)[-1] == '/')
def get_reviews(message: Message) -> None:
    user_message = (message.text)[1:-1]
    print(user_message)

    final_dict = data[f'{message.chat.id}_parser'].get_ads(user_message)
    if data[f'{message.chat.id}_parser'].company_exist:
        if data[f'{message.chat.id}_parser'].reviews_condition:
            for even in final_dict:
                bot.send_message(chat_id=message.chat.id,
                                 text=f"Дата: {even['date']}\nОткуда: {even['town_from']}\nКуда: {even['town_to']}\nОтзыв: {even['short']}")
        else:
            bot.send_message(chat_id=message.chat.id,
                             text='У данной компании нет отзывов\nПопробуйте еще раз ввести название', reply_markup=keyboard_switch_on_start())
    else:
        bot.send_message(chat_id=message.chat.id,
                         text='Такой компании не существует\nПопробуйте еще раз ввести название', reply_markup=keyboard_switch_on_start())


# Else block
@bot.message_handler(func=lambda message: True)
def else_block(message: Message) -> None:
    bot.send_message(chat_id=message.chat.id,
                     text='Я Вас не понимаю... Введите корректное значение...')


bot.polling(none_stop=True)
