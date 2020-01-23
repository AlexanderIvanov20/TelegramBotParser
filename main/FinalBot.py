import telebot
import mysql.connector as mysql_connector
import json

from telebot.types import *
from Parser import *
from FinalKeyboard import main_keyboard, no_vip_keyboard, pagination_keyboard
from datetime import datetime, timedelta


# Texts to answer of bot
def all_text() -> dict:
    with open('config.json', 'r', encoding='utf-8') as file:
        data_text = json.load(file)
    return data_text


# Create connection with database
CONNECTION = mysql_connector.connect(user='root', password='domestosroot50',
                                     host='127.0.0.1', database='database1',
                                     auth_plugin='mysql_native_password',
                                     port=3306)
CURSOR = CONNECTION.cursor(buffered=True)

# Bot settings
TOKEN = all_text()['token']
BOT = telebot.TeleBot(token=TOKEN)
# ! Prices options
# PRICES = [
#     LabeledPrice(label='Подписка на месяц', amount=300)
# ]
# SHIPPING_OPTIONS = [
#     ShippingOption(id='instant',
#                    title='Vip-подписка').add_price(
#                        LabeledPrice(label='Vip-подписка',
#                                     amount=300)
#     )
# ]
# Liqpay token
PROVIDER_TOKEN = all_text()['provider_token']
DATA = {}


# Get all titles of compaines that in database, set it and sort by alphabet
def get_all_titles():
    CURSOR.execute('SELECT recipient FROM database1.telegram_parser_comment;')
    all_titles = CURSOR.fetchall()

    # Write to set for unique
    set_of_titles = set()
    for item in all_titles:
        set_of_titles.add(item[0])

    # Sort
    list_of_titles = list(sorted(list(set_of_titles)))
    return list_of_titles


# Check subcription till
def check_date(chat_id: int) -> None:
    today_now = datetime.timestamp(datetime.now())

    CURSOR.execute('SELECT activation_till FROM database1.profiles '
                   f'WHERE id_user={chat_id};')
    current_activation_till = CURSOR.fetchone()

    if (current_activation_till is not None and
            today_now > current_activation_till[0]):

        CURSOR.execute("UPDATE database1.profiles SET "
                       f"vip=False, activation_date=0, "
                       f"activation_till=0, subscription=False, "
                       f"need_vip=False WHERE id_user={chat_id};")
        CONNECTION.commit()


# Check on 1 request
def check_today(chat_id: int) -> None:
    today_now = datetime.timestamp(datetime.now())
    try:
        till_date_today = DATA[f'{chat_id}_today_till']

        if today_now > till_date_today:
            del DATA[f'{chat_id}_today_till']
            DATA[f'{chat_id}_count_requests'] = 0
    except KeyError:
        pass


# Template for string
def template_final_string(current_comments: list, chat_id: int) -> str:
    result_string = ''

    start = DATA[f'{chat_id}_start']
    end = DATA[f'{chat_id}_end']

    for even_comment in current_comments[start:end]:
        result_string += (f"🏙️ Города перевозки: {even_comment[1]} - "
                          f"{even_comment[2]}\n"
                          f"📅 Дата перевозки: {even_comment[3]}\n"
                          f"⏰ Дата размещения отзыва: {even_comment[4]}\n"
                          f"🏳️ Страны перевозки: {even_comment[5]} - "
                          f"{even_comment[6]}\n"
                          f'👤Отзыв о <a href="{even_comment[10]}">'
                          f'{even_comment[9]}</a> от '
                          f'<a href="{even_comment[8]}">'
                          f'{even_comment[7]}</a>\n'
                          f"📰 Текст отзыва: {even_comment[11]}\n\n")
    return result_string


# Template for output a result string
def output_result_string(current_comments: list, current_user: tuple,
                         message: Message) -> None:
    # Check on existing
    if current_comments == []:
        keyboard = main_keyboard()
        BOT.send_message(chat_id=message.chat.id,
                         text='Компания или отзывов на нее не найдены. '
                              'Попробуйте еще раз',
                         reply_markup=keyboard)
    else:
        # If user have vip subcription
        if current_user[1] == 1:
            result_string = template_final_string(
                current_comments=current_comments,
                chat_id=message.chat.id
            )
            DATA[f'{message.chat.id}_comments'] = current_comments

            # Register today's request
            DATA[f'{message.chat.id}_count_requests'] += 1
            if f'{message.chat.id}_today_till' not in DATA.keys():
                DATA[f'{message.chat.id}_today_till'] = datetime.timestamp(
                    datetime.now() + timedelta(days=1)
                )

            # Check in order to output pagination
            if len(current_comments) > 3:
                BOT.send_message(chat_id=message.chat.id,
                                 text=result_string,
                                 disable_web_page_preview=True,
                                 reply_markup=pagination_keyboard(
                                     left=False
                                 ), parse_mode='HTML')
            else:
                # Without pagination
                BOT.send_message(chat_id=message.chat.id,
                                 text=result_string, parse_mode='Markdown',
                                 disable_web_page_preview=True)
        else:
            # If user don't do request yet
            if DATA[f'{message.chat.id}_count_requests'] <= 0:
                result_string = template_final_string(
                    current_comments=current_comments,
                    chat_id=message.chat.id
                )
                DATA[f'{message.chat.id}_comments'] = current_comments

                # Register today's request
                DATA[f'{message.chat.id}_count_requests'] += 1
                if f'{message.chat.id}_today_till' not in DATA.keys():
                    DATA[
                        f'{message.chat.id}_today_till'
                    ] = datetime.timestamp(
                        datetime.now() + timedelta(days=1)
                    )

                # Check in order to output pagination
                if len(current_comments) > 3:
                    BOT.send_message(chat_id=message.chat.id,
                                     text=result_string,
                                     disable_web_page_preview=True,
                                     reply_markup=pagination_keyboard(
                                         left=False
                                     ), parse_mode='HTML')
                else:
                    # Without pagination
                    BOT.send_message(chat_id=message.chat.id,
                                     text=result_string, parse_mode='Markdown',
                                     disable_web_page_preview=True)
            else:
                # If user already did request today
                BOT.send_message(chat_id=message.chat.id,
                                 text='Запрос за сегодня уже сделан.\n\n'
                                 'Купите подписку чтобы получать отзывы '
                                 'бесконечно в течении месяца, либо '
                                 'подождите до завтра.',
                                 reply_markup=no_vip_keyboard())


# Add pages in commets
def add_to_buttons(call: CallbackQuery):
    DATA[f'{call.from_user.id}_start'] += 3
    DATA[f'{call.from_user.id}_end'] += 3


# Remove pages in comments
def remove_from_buttons(call: CallbackQuery):
    DATA[f'{call.from_user.id}_start'] -= 3
    DATA[f'{call.from_user.id}_end'] -= 3


@BOT.message_handler(commands=['start'])
def on_start(message: Message) -> None:
    get_all_titles()

    # Parser class instance
    # parser = Parser()
    # DATA[f'{message.chat.id}_parser'] = parser
    DATA[f'{message.chat.id}_count_requests'] = 0

    # Check on
    check_date(chat_id=message.chat.id)
    check_today(chat_id=message.chat.id)

    # Try to get a user
    CURSOR.execute("SELECT * FROM database1.profiles "
                   f"WHERE id_user={message.chat.id};")
    current_user = CURSOR.fetchone()

    first_name = message.from_user.first_name
    last_name = message.from_user.first_name

    # Create user if he/she doesn't exist
    if current_user is None:
        CURSOR.execute("INSERT INTO database1.profiles"
                       "(vip, activation_date, activation_till, id_user, "
                       "subscription, need_vip, credentials) "
                       f"VALUES(False, 0, 0, '{message.chat.id}', False, "
                       f"False, '{first_name} {last_name}')")
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
            message_text='Название компании'
        ),
        description='Начните вводить название и выберете из предложеных '
                    'вариантов')
    BOT.answer_inline_query(inline_query_id=query.id, results=[response])


# Create drop-up menu
@BOT.inline_handler(func=lambda query: True)
def query_get(query: InlineQuery) -> None:
    try:
        # Get user message
        user_message = query.query
        print(user_message)
        # possible_variants = DATA[
        #     f'{query.from_user.id}_parser'
        # ].get_variants(user_message)['items']
        # print(possible_variants[0])
        possible_variants = get_all_titles()
        final_inline_query = []

        point = 1
        # Add point to drop-up menu
        for item in possible_variants:
            if user_message.lower() in item.lower() or \
                    user_message.lower() == item.lower():
                response = InlineQueryResultArticle(
                    id=f"{point}",
                    title=f"{item}",
                    input_message_content=InputTextMessageContent(f"/{item}/")
                )
                final_inline_query.append(response)
                point += 1

        BOT.answer_inline_query(inline_query_id=query.id,
                                results=final_inline_query)
    except Exception as error:
        print(error)


# ! Successful payment
# @BOT.message_handler(content_types=['successful_payment'])
# def got_payment(message: Message) -> None:
#     # Get now-time, set now + 30 days
#     now_time = datetime.timestamp(datetime.now())
#     through_month = datetime.timestamp(datetime.now() + timedelta(days=30))
#     print(message)

#     charged_id = (
#         message.successful_payment.provider_payment_charge_id
#     ).replace('_', '')
#     print(charged_id)

#     # Write to table 'activations' for protocol
# CURSOR.execute('INSERT INTO database1.activations(id_user, purchase_date, '
#                    'activation_till, provider_payment_charge_id) VALUES'
#                    f'({message.chat.id}, {now_time}, {through_month}, '
#                    f"'{charged_id}')")
#     CONNECTION.commit()

#     # Take to user vip-subscription
#     CURSOR.execute("UPDATE database1.profiles SET "
#                    f"vip=True, activation_date={now_time}, "
#                    f"activation_till={through_month}, subscription=False "
#                    f"WHERE id_user={message.chat.id};")
#     CONNECTION.commit()

#     BOT.send_message(chat_id=message.chat.id,
#                      text=f'Поздравляем! Вы преобрели подписку за '
#                      f'`{message.successful_payment.total_amount / 100} '
#                      f'{message.successful_payment.currency}` \n\n'
#                           'Спасибо за покупку!', parse_mode='Markdown',
#                           reply_markup=main_keyboard())


# Get title of company and take all comments about it
@BOT.message_handler(content_types=['text'])
def get_company(message: Message) -> None:
    check_date(chat_id=message.chat.id)
    check_today(chat_id=message.chat.id)

    if message.text[0] == '/' and message.text[-1] == '/':
        # Slice a text of message
        user_message = message.text[1:-1]

        # Get user
        CURSOR.execute("SELECT * FROM database1.profiles "
                       f"WHERE id_user={message.chat.id};")
        current_user = CURSOR.fetchone()

        # Get all comments on current company
        CURSOR.execute(f"SELECT * FROM database1.telegram_parser_comment "
                       f"WHERE recipient='{user_message}';")
        current_comments = CURSOR.fetchall()
        print(current_comments)

        DATA[f'{message.from_user.id}_start'] = 0
        DATA[f'{message.from_user.id}_end'] = 3

        output_result_string(current_comments=current_comments,
                             current_user=current_user, message=message)
    else:
        BOT.send_message(chat_id=message.chat.id,
                         text='Я не могу обработать введеный Вами текст')


# Get link on a company and and take all comments about it
def get_url(message: Message) -> None:
    check_date(chat_id=message.chat.id)
    check_today(chat_id=message.chat.id)

    # Get user message and check it
    user_message = message.text
    if user_message[-1] != '/':
        user_message += '/'

    # Get user
    CURSOR.execute("SELECT * FROM database1.profiles "
                   f"WHERE id_user={message.chat.id};")
    current_user = CURSOR.fetchone()

    # Get all comments on current company
    CURSOR.execute(f"SELECT * FROM database1.telegram_parser_comment "
                   f"WHERE recipient_link='{user_message}';")
    current_comments = CURSOR.fetchall()
    print(current_comments)

    DATA[f'{message.from_user.id}_start'] = 0
    DATA[f'{message.from_user.id}_end'] = 3

    output_result_string(current_comments=current_comments,
                         current_user=current_user, message=message)

# Get all callbacks
@BOT.callback_query_handler(func=lambda call: True)
def get_calls(call: CallbackQuery) -> None:
    check_date(chat_id=call.from_user.id)
    check_today(chat_id=call.from_user.id)

    if call.data == 'by_link':
        # Get link it self
        some = BOT.send_message(chat_id=call.from_user.id,
                                text='Введите ссылку на компанию')
        BOT.register_next_step_handler(some, get_url)

    # ! Invoice sending
    elif call.data == 'no_vip':
        # BOT.send_invoice(chat_id=call.from_user.id, title='Подписка на месяц'
        #                  description='Если Вы хотите делать больше, '
        #                              'чем 1 запрос в день, '
        #                              'купите подписку за 99 UAH',
        #                  provider_token=PROVIDER_TOKEN, currency='UAH',
        #                  is_flexible=False, prices=PRICES,
        #                  start_parameter='subscription-example',
        #                  invoice_payload='subcription coupon')

        BOT.send_message(chat_id=call.from_user.id,
                         text='Для приобретения подписки '
                              'пройдите по ссылке:\n'
                              'https://send.monobank.ua/6Qv6mVbS6y\n\n'
                              'В комментарии перевода укажите Ваш '
                              f'Telegram ID: `{call.from_user.id}`\n'
                              'Это обязательно, иначе мы не сможем '
                              'Вас идентифицировать',
                              parse_mode='Markdown')

    elif call.data == 'vip':
        # Get users vip options
        CURSOR.execute(
            'SELECT * FROM database1.profiles '
            f'WHERE id_user={call.from_user.id};'
        )
        current_user = CURSOR.fetchone()

        # Create request for vip-subscription
        CURSOR.execute("UPDATE database1.profiles SET "
                       f"vip=False, activation_date=0, "
                       f"activation_till=0, subscription=False, "
                       f"need_vip=True WHERE id_user={call.from_user.id};")
        CONNECTION.commit()

        string = ''
        if current_user[1] == 0:
            string += '👑 VIP:  `Нет`\n'
        else:
            string += '👑 VIP:  `Есть`\n'

        if current_user[2] != 0 and current_user[3] != 0 and \
                current_user[3] - current_user[2] != 0:
            first_date = datetime.fromtimestamp(
                current_user[2]
            ).strftime(r'%d.%m.%Y %H:%M:%S')
            second_date = datetime.fromtimestamp(
                current_user[3]
            ).strftime(r'%d.%m.%Y %H:%M:%S')
            end_of_subscription = current_user[3] - current_user[2]
            third_date = datetime.fromtimestamp(
                end_of_subscription
            ).strftime(r'%d дней')
        else:
            first_date = current_user[2]
            second_date = current_user[3]
            third_date = current_user[3] - current_user[2]

        string += (f'День активации:  `{first_date}`\n'
                   f'Окончание подписки:  `{second_date}`\n'
                   f'Осталось до окончания: `{third_date}`\n')

        if current_user[1] == 0:
            BOT.send_message(chat_id=call.from_user.id,
                             text=string, parse_mode='Markdown',
                             reply_markup=no_vip_keyboard())
        else:
            BOT.send_message(chat_id=call.from_user.id,
                             text=string, parse_mode='Markdown')

    # On right button
    elif call.data == 'right':
        # Get comments from dict
        comments = DATA[f'{call.from_user.id}_comments']

        # On end
        if len(comments) - DATA[f'{call.from_user.id}_end'] <= 3:
            add_to_buttons(call=call)
            keyboard = pagination_keyboard(right=False)

        elif DATA[f'{call.from_user.id}_end'] + 3 < len(comments):
            add_to_buttons(call=call)
            keyboard = pagination_keyboard()

        elif DATA[f'{call.from_user.id}_end'] + 3 == len(comments):
            add_to_buttons(call=call)
            keyboard = pagination_keyboard(right=False)

        else:
            start = DATA[f'{call.from_user.id}_start']
            end = DATA[f'{call.from_user.id}_end']

            keyboard = pagination_keyboard(right=False)

        # Edit message and pagination menu
        result_string = template_final_string(current_comments=comments,
                                              chat_id=call.from_user.id)
        BOT.edit_message_text(text=result_string, chat_id=call.from_user.id,
                              message_id=call.message.message_id,
                              disable_web_page_preview=True,
                              reply_markup=keyboard, parse_mode='HTML')

    # On left button
    elif call.data == 'left':
        # Get comments from dict
        comments = DATA[f'{call.from_user.id}_comments']

        # On start
        if DATA[f'{call.from_user.id}_start'] - 3 <= 0:
            remove_from_buttons(call=call)
            keyboard = pagination_keyboard(left=False)

        elif DATA[f'{call.from_user.id}_start'] - 3 > 0:
            remove_from_buttons(call=call)
            keyboard = pagination_keyboard()

        # Edit message and pagination menu
        result_string = template_final_string(current_comments=comments,
                                              chat_id=call.from_user.id)
        BOT.edit_message_text(text=result_string, chat_id=call.from_user.id,
                              message_id=call.message.message_id,
                              disable_web_page_preview=True,
                              reply_markup=keyboard, parse_mode='HTML')

    # Output menu
    elif call.data == 'menu':
        keyboard = main_keyboard()
        BOT.send_message(chat_id=call.from_user.id,
                         text='Выбере нужный Вам пункт', reply_markup=keyboard)


# ! Get all shipping query
# @BOT.shipping_query_handler(func=lambda query: True)
# def shipping(shipping_query: ShippingQuery) -> None:
#     print(shipping_query)
#     BOT.answer_shipping_query(shipping_query_id=shipping_query.id, ok=True,
#                               shipping_options=SHIPPING_OPTIONS,
#                               error_message='Наша команда сейчас занята. '
#                                             'Попробуйте еще раз позже.')


# ! Get all pre checkout query
# @BOT.pre_checkout_query_handler(func=lambda query: True)
# def checkout(pre_checkout_query: PreCheckoutQuery) -> None:
#     print(pre_checkout_query)
#     BOT.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id,
#                                   ok=True,
#                                   error_message="Некто хочет украсть "
#                                                 "CVV Вашей карты, но мы "
#                                                 "успешно защитили Ваши "
#                                            "данные. Попробуйте оплатить "
#                                                 "снова в течении нескольких "
#                                                 "минут. Нам нужен небольшой "
#                                                 "перерыв.")


# Else block for all bot
@BOT.message_handler(content_types=['location', 'photo', 'video', 'text'])
def else_block(message: Message) -> None:
    BOT.send_message(chat_id=message.chat.id,
                     text='К сожалению, я Вас не понимаю... '
                     'Попробуйте ввести корректные данные.',
                     parse_mode='HTML')


BOT.polling(none_stop=True)
