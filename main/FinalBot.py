import telebot
import mysql.connector as mysql_connector
import json

from telebot.types import *
from Parser import *
from FinalKeyboard import main_keyboard, no_vip_keyboard, bottom_menu
from datetime import datetime, timedelta


CONNECTION = mysql_connector.connect(user='root', password='domestosroot50',
                                     host='localhost', database='database1',
                                     auth_plugin='mysql_native_password')
CURSOR = CONNECTION.cursor(buffered=True)
TOKEN = '917181533:AAHB0gNsOFCw4nHYpRyrDGDfQQySzFu7YMI'
BOT = telebot.TeleBot(token=TOKEN)
PRICES = [
    LabeledPrice(label='Подписка на месяц', amount=100)
]
SHIPPING_OPTIONS = [
    ShippingOption(id='instant',
                   title='Vip-подписка').add_price(
                       LabeledPrice(label='Vip-подписка',
                                    amount=100)
    )
]
PROVIDER_TOKEN = '632593626:TEST:i56982357197'
DATA = {}


# Texts to answer of bot
def all_text():
    with open('Texts.json', 'r', encoding='utf-8') as file:
        data_text = json.load(file)
    return data_text


# Check subcription till
def check_date(chat_id):
    today_now = datetime.timestamp(datetime.now())

    CURSOR.execute('SELECT activation_till FROM database1.users_profile '
                   f'WHERE id_user={chat_id};')
    current_activation_till = CURSOR.fetchone()

    if current_activation_till is not None and today_now > current_activation_till[0]:
        CURSOR.execute("UPDATE database1.users_profile SET "
                       f"vip=False, activation_date=0, "
                       f"activation_till=0 "
                       f"WHERE id_user={chat_id};")
        CONNECTION.commit()


# Check on 1 request
def check_today(chat_id):
    today_now = datetime.timestamp(datetime.now())
    try:
        till_date_today = DATA[f'{chat_id}_today_till']

        if today_now > till_date_today:
            del DATA[f'{chat_id}_today_till']
            DATA[f'{chat_id}_count_requests'] = 0
    except KeyError:
        pass


@BOT.message_handler(commands=['start'])
def on_start(message: Message) -> None:
    print(all_text())

    parser = Parser()
    DATA[f'{message.chat.id}_parser'] = parser
    DATA[f'{message.chat.id}_count_requests'] = 0

    check_date(chat_id=message.chat.id)
    check_today(chat_id=message.chat.id)

    # Try to get a user
    CURSOR.execute("SELECT * FROM database1.users_profile "
                   f"WHERE id_user={message.chat.id};")
    current_user = CURSOR.fetchone()

    if current_user is None:
        # Create user if he/she doesn't exist
        CURSOR.execute("INSERT INTO database1.users_profile "
                       "(vip, activation_date, activation_till, id_user) "
                       f"VALUES (False, 0, 0, '{message.chat.id}')")
        CONNECTION.commit()

    keyboard = main_keyboard()
    BOT.send_message(chat_id=message.chat.id,
                     text=all_text()['greeting'], reply_markup=keyboard)


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


# Successful payment
@BOT.message_handler(content_types=['successful_payment'])
def got_payment(message: Message) -> None:
    # Get now-time, set now + 30 days
    now_time = datetime.timestamp(datetime.now())
    through_month = datetime.timestamp(datetime.now() + timedelta(30))
    print(message)

    # Take to user vip-subscription
    CURSOR.execute("UPDATE database1.users_profile SET "
                   f"vip=True, activation_date={now_time}, "
                   f"activation_till={through_month} "
                   f"WHERE id_user={message.chat.id};")
    CONNECTION.commit()

    BOT.send_message(chat_id=message.chat.id,
                     text=f'Поздравляем! Вы преобрели подписку за '
                          f'`{message.successful_payment.total_amount / 100} '
                          f'{message.successful_payment.currency}` \n\n'
                          'Спасибо за покупку!', parse_mode='Markdown')


# Get title of company and take all comments about it
@BOT.message_handler(content_types=['text'])
def get_company(message: Message) -> None:
    check_date(chat_id=message.chat.id)
    check_today(chat_id=message.chat.id)
    if message.text[0] == '/' and message.text[-1] == '/':
        # Slice a text of message
        user_message = message.text[1:-1]

        # Get user
        CURSOR.execute("SELECT * FROM database1.users_profile "
                       f"WHERE id_user={message.chat.id};")
        current_user = CURSOR.fetchone()

        # Get all comments on current company
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
            if current_user[1] == 1:
                result_string = ''
                for even_comment in current_comments:
                    result_string += f"🏙️ Города перевозки: {even_comment[1]} - {even_comment[2]}\n📅 Дата перевозки: {even_comment[3]}\n⏰ Дата размещения отзыва: {even_comment[4]}\n🏳️ Страны перевозки: {even_comment[5]} - {even_comment[6]}\n👨Заказчик: {even_comment[7]}\n🔗 Заказчик(ссылка): {even_comment[8]}\n👨 Перевозчик: {even_comment[9]}\n🔗 Перевозчик(ссылка): {even_comment[10]}\n📰 Текст отзыва: {even_comment[11]}\n\n"

                DATA[f'{message.chat.id}_count_requests'] += 1
                if f'{message.chat.id}_today_till' not in DATA.keys():
                    DATA[f'{message.chat.id}_today_till'] = datetime.timestamp(
                        datetime.now() + timedelta(1)
                    )
                BOT.send_message(chat_id=message.chat.id, text=result_string,
                                 disable_web_page_preview=True,
                                 reply_markup=bottom_menu())
            else:
                if DATA[f'{message.chat.id}_count_requests'] <= 0:
                    result_string = ''
                    for even_comment in current_comments:
                        result_string += f"🏙️ Города перевозки: {even_comment[1]} - {even_comment[2]}\n📅 Дата перевозки: {even_comment[3]}\n⏰ Дата размещения отзыва: {even_comment[4]}\n🏳️ Страны перевозки: {even_comment[5]} - {even_comment[6]}\n👨Заказчик: {even_comment[7]}\n🔗 Заказчик(ссылка): {even_comment[8]}\n👨 Перевозчик: {even_comment[9]}\n🔗 Перевозчик(ссылка): {even_comment[10]}\n📰 Текст отзыва: {even_comment[11]}\n\n"

                    DATA[f'{message.chat.id}_count_requests'] += 1
                    if f'{message.chat.id}_today_till' not in DATA.keys():
                        DATA[
                            f'{message.chat.id}_today_till'
                        ] = datetime.timestamp(
                            datetime.now() + timedelta(1)
                        )
                    BOT.send_message(chat_id=message.chat.id,
                                     text=result_string,
                                     disable_web_page_preview=True,
                                     reply_markup=bottom_menu())
                else:
                    BOT.send_message(chat_id=message.chat.id,
                                     text='Запрос за сегодня уже сделан.\n\n'
                                     'Купите подписку чтобы получать отзывы '
                                     'бесконечно в течении месяца, либо '
                                     'подождите до завтра.',
                                     reply_markup=no_vip_keyboard())
    elif message.text == 'Вывести меню':
        keyboard = main_keyboard()
        BOT.send_message(chat_id=message.chat.id,
                         text='Выбере нужный Вам пункт', reply_markup=keyboard)
    else:
        BOT.send_message(chat_id=message.chat.id,
                         text='Я не могу обработать введеный Вами текст')


# Get link on a company and and take all comments about it
def get_url(message: Message) -> None:
    check_date(chat_id=message.chat.id)
    check_today(chat_id=message.chat.id)
    user_message = DATA[
        f'{message.from_user.id}_parser'
    ].get_by_url(message.text)

    # Get user
    CURSOR.execute("SELECT * FROM database1.users_profile "
                   f"WHERE id_user={message.chat.id};")
    current_user = CURSOR.fetchone()

    # Get all comments on current company
    CURSOR.execute(f"SELECT * FROM database1.telegram_parser_comment "
                   f"WHERE recipient='{user_message}';")
    current_comments = CURSOR.fetchall()
    print(current_comments)

    # Check on existing company
    if DATA[f'{message.from_user.id}_parser'].company_exist is False or current_comments == [] or current_comments is None:
        keyboard = main_keyboard()
        BOT.send_message(chat_id=message.chat.id,
                         text='Компания не найдена или '
                              'отзывов на нее в нашей базе нет. '
                              'Попробуйте еще раз',
                         reply_markup=keyboard)
    else:
        if current_user[1] == 1:
            result_string = ''
            for even_comment in current_comments:
                result_string += f"🏙️ Города перевозки: {even_comment[1]} - {even_comment[2]}\n📅 Дата перевозки: {even_comment[3]}\n⏰ Дата размещения отзыва: {even_comment[4]}\n🏳️ Страны перевозки: {even_comment[5]} - {even_comment[6]}\n👨Заказчик: {even_comment[7]}\n🔗 Заказчик(ссылка): {even_comment[8]}\n👨 Перевозчик: {even_comment[9]}\n🔗 Перевозчик(ссылка): {even_comment[10]}\n📰 Текст отзыва: {even_comment[11]}\n\n"

            DATA[f'{message.chat.id}_count_requests'] += 1
            if f'{message.chat.id}_today_till' not in DATA.keys():
                DATA[f'{message.chat.id}_today_till'] = datetime.timestamp(
                    datetime.now() + timedelta(1)
                )
            BOT.send_message(chat_id=message.chat.id, text=result_string,
                             disable_web_page_preview=True,
                             reply_markup=bottom_menu())
        else:
            if DATA[f'{message.chat.id}_count_requests'] <= 0:
                result_string = ''
                for even_comment in current_comments:
                    result_string += f"🏙️ Города перевозки: {even_comment[1]} - {even_comment[2]}\n📅 Дата перевозки: {even_comment[3]}\n⏰ Дата размещения отзыва: {even_comment[4]}\n🏳️ Страны перевозки: {even_comment[5]} - {even_comment[6]}\n👨Заказчик: {even_comment[7]}\n🔗 Заказчик(ссылка): {even_comment[8]}\n👨 Перевозчик: {even_comment[9]}\n🔗 Перевозчик(ссылка): {even_comment[10]}\n📰 Текст отзыва: {even_comment[11]}\n\n"

                DATA[f'{message.chat.id}_count_requests'] += 1
                if f'{message.chat.id}_today_till' not in DATA.keys():
                    DATA[f'{message.chat.id}_today_till'] = datetime.timestamp(
                        datetime.now() + timedelta(1)
                    )
                BOT.send_message(chat_id=message.chat.id, text=result_string,
                                 disable_web_page_preview=True,
                                 reply_markup=bottom_menu())
            else:
                BOT.send_message(chat_id=message.chat.id,
                                 text='Вы уже сделали запрос за сегодня.\n\n'
                                      'Купите подписку чтобы получать отзывы '
                                      'бесконечно в течении месяца, либо '
                                      'подождите до завтра.',
                                 reply_markup=no_vip_keyboard())


@BOT.callback_query_handler(func=lambda call: True)
def get_calls(call: CallbackQuery) -> None:
    check_date(chat_id=call.from_user.id)
    check_today(chat_id=call.from_user.id)
    if call.data == 'by_link':
        # Get link it self
        some = BOT.send_message(chat_id=call.from_user.id,
                                text='Введите ссылку на компанию')
        BOT.register_next_step_handler(some, get_url)

    # Send invoice
    elif call.data == 'no_vip':
        BOT.send_invoice(chat_id=call.from_user.id, title='Подписка на месяц',
                         description='Если Вы хотите делать больше, '
                         'чем 1 запрос в день, '
                         'купите подписку за 99 UAH',
                         provider_token=PROVIDER_TOKEN, currency='uah',
                         is_flexible=False, prices=PRICES,
                         start_parameter='subscription-example',
                         invoice_payload='HAPPY FRIDAYS COUPON')


# Get all shipping query
@BOT.shipping_query_handler(func=lambda query: True)
def shipping(shipping_query: ShippingQuery) -> None:
    print(shipping_query)
    BOT.answer_shipping_query(shipping_query_id=shipping_query.id, ok=True,
                              shipping_options=SHIPPING_OPTIONS,
                              error_message='Наша команда сейчас занята. '
                                            'Попробуйте еще раз позже.')


# Get all pre checkout query
@BOT.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query: PreCheckoutQuery) -> None:
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
