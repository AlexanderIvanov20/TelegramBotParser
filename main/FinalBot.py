import telebot
import mysql.connector as mysql_connector

from telebot.types import *
from Parser import *
from FinalKeyboard import main_keyboard


CONNECTION = mysql_connector.connect(user='root', password='domestosroot50',
                                     host='localhost', database='database1',
                                     auth_plugin='mysql_native_password')
CURSOR = CONNECTION.cursor()
TOKEN = '917181533:AAHB0gNsOFCw4nHYpRyrDGDfQQySzFu7YMI'
BOT = telebot.TeleBot(token=TOKEN)
PRICES = [
    LabeledPrice(label='Working Time Machine', amount=100),
    LabeledPrice(label='Gift wrapping', amount=100)
]
SHIPPING_OPTIONS = [
    ShippingOption(id='instant',
                   title='WorldWide Teleporter').add_price(
                       LabeledPrice('Teleporter', 1000)
    ),
    ShippingOption(id='pickup',
                   title='Local pickup').add_price(
                       LabeledPrice('Pickup', 300)
    )
]
PROVIDER_TOKEN = '632593626:TEST:i56982357197'
DATA = {}


@BOT.message_handler(commands=['start'])
def on_start(message: Message) -> None:
    parser = Parser()
    DATA[f'{message.chat.id}_parser'] = parser

    keyboard = main_keyboard()
    BOT.send_message(chat_id=message.chat.id,
                     text='Выбере нужный Вам пункт', reply_markup=keyboard)


# If inline query is null
@BOT.inline_handler(func=lambda query: len(query.query) == 0)
def default_query(query: InlineQuery) -> None:
    response = InlineQueryResultArticle(
        id='1', title='Название компании',
        input_message_content=InputTextMessageContent(
            message_text='Название компании'),
        description='Начните вводить название и выберете из предложеных '
                    'вариантов')
    BOT.answer_inline_query(inline_query_id=query.id, results=[response])


# Create drop-up menu
@BOT.inline_handler(func=lambda query: True)
def query_get(query: InlineQuery) -> None:
    try:
        user_message = query.query
        possible_variants = DATA[
            f'{query.from_user.id}_parser'
        ].get_variants(user_message)['items']
        print(possible_variants[0])
        final_inline_query = []

        # Add point to drop-up menu
        for item in possible_variants:
            even_owner = item['owner']
            response = InlineQueryResultArticle(id=f"{even_owner['id']}",
                                                title=f"{even_owner['nameWithoutBrand']}",
                                                input_message_content=InputTextMessageContent(
                                                    f"/{even_owner['nameWithoutBrand']}/"),
                                                description=f"{even_owner['timeOnSite']}. {even_owner['address']['country']}-{even_owner['address']['town']}")
            final_inline_query.append(response)

        BOT.answer_inline_query(inline_query_id=query.id,
                                results=final_inline_query)
    except Exception as error:
        print(error)


@BOT.message_handler(content_types=['successful_payment'])
def got_payment(message):
    print(message)
    BOT.send_message(chat_id=message.chat.id,
                     text=f'Поздравляем! Вы преобрели подписку за '
                          f'`{message.successful_payment.total_amount / 100} '
                          f'{message.successful_payment.currency}` \n\n'
                          'Спасибо за покупку!', parse_mode='Markdown')


@BOT.message_handler(content_types=['text'])
def get_company(message: Message) -> None:
    if message.text[0] == '/' and message.text[-1] == '/':
        user_message = message.text[1:-1]

        CURSOR.execute(f"SELECT * FROM database1.telegram_parser_comment "
                       f"WHERE recipient='{user_message}';")
        current_comments = CURSOR.fetchall()
        print(current_comments)

        if current_comments == [] or current_comments is None:
            keyboard = main_keyboard()
            BOT.send_message(chat_id=message.chat.id,
                             text='Компания не найдена. Попробуйте еще раз',
                             reply_markup=keyboard)
        else:
            result_string = ''
            for even_comment in current_comments:
                result_string += f"🏙️ Города перевозки: {even_comment[1]} - {even_comment[2]}\n📅 Дата перевозки: {even_comment[3]}\n⏰ Дата размещения отзыва: {even_comment[4]}\n🏳️ Страны перевозки: {even_comment[5]} - {even_comment[6]}\n👨Заказчик: {even_comment[7]}\n🔗 Заказчик(ссылка): {even_comment[8]}\n👨 Перевозчик: {even_comment[9]}\n🔗 Перевозчик(ссылка): {even_comment[10]}\n📰 Текст отзыва: {even_comment[11]}\n\n"

            BOT.send_message(chat_id=message.chat.id, text=result_string,
                             disable_web_page_preview=True)
    else:
        BOT.send_message(chat_id=message.chat.id,
                         text='Я не могу обработать введеный Вами текст')


def get_url(message: Message) -> None:
    user_message = DATA[
        f'{message.from_user.id}_parser'
    ].get_by_url(message.text)

    CURSOR.execute(f"SELECT * FROM database1.telegram_parser_comment "
                   f"WHERE recipient='{user_message}';")
    current_comments = CURSOR.fetchall()
    print(current_comments)

    if DATA[f'{message.from_user.id}_parser'].company_exist is False:
        keyboard = main_keyboard()
        BOT.send_message(chat_id=message.chat.id,
                         text='Компания не найдена. Попробуйте еще раз',
                         reply_markup=keyboard)
    else:
        result_string = ''
        for even_comment in current_comments:
            result_string += f"🏙️ Города перевозки: {even_comment[1]} - {even_comment[2]}\n📅 Дата перевозки: {even_comment[3]}\n⏰ Дата размещения отзыва: {even_comment[4]}\n🏳️ Страны перевозки: {even_comment[5]} - {even_comment[6]}\n👨Заказчик: {even_comment[7]}\n🔗 Заказчик(ссылка): {even_comment[8]}\n👨 Перевозчик: {even_comment[9]}\n🔗 Перевозчик(ссылка): {even_comment[10]}\n📰 Текст отзыва: {even_comment[11]}\n\n"

        BOT.send_message(chat_id=message.chat.id, text=result_string,
                         disable_web_page_preview=True)


@BOT.callback_query_handler(func=lambda call: True)
def get_calls(call: CallbackQuery) -> None:
    if call.data == 'by_link':
        some = BOT.send_message(chat_id=call.from_user.id,
                                text='Введите ссылку на компанию')
        BOT.register_next_step_handler(some, get_url)


@BOT.message_handler(commands=['buy'])
def command_pay(message):
    BOT.send_invoice(chat_id=message.chat.id, title='Подписка на месяц',
                     description='Если Вы хотите делать больше, '
                                 'чем 1 запрос в день, '
                                 'купите подписку за 99 UAH',
                     provider_token=PROVIDER_TOKEN,
                     currency='uah',
                     is_flexible=False,
                     prices=PRICES,
                     start_parameter='subscription-example',
                     invoice_payload='HAPPY FRIDAYS COUPON')


@BOT.shipping_query_handler(func=lambda query: True)
def shipping(shipping_query):
    print(shipping_query)
    BOT.answer_shipping_query(shipping_query_id=shipping_query.id, ok=True,
                              shipping_options=SHIPPING_OPTIONS,
                              error_message='Oh, seems like our Dog couriers '
                                            'are having a lunch right now. '
                                            'Try again later!')


@BOT.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    print(pre_checkout_query)
    BOT.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id,
                                  ok=True,
                                  error_message="Некто хочет украсть "
                                                "CVV Вашей карты, но мы "
                                                "успешно защитили Ваши "
                                                "данные. Попробуйте оплатить "
                                                "снова в течении нескольких "
                                                "минут. Нам нужен небольшой "
                                                "перерыв.")


BOT.polling(none_stop=True)
