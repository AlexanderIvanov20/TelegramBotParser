import telebot
from Parser import Parser


TOKEN = '1030953540:AAFt6-O5laMVRjO8hN1uA-dt7qZPPG0439c'
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(func=lambda message: True)
def get_text(message):
    user_message = message.text

    parser = Parser(user_message)
    ads = parser.ads

    if ads != []:
        print(ads[0])
        bot.send_message(chat_id=message.chat.id, text=f"\
        Перевозчик: {ads[0]['per_name']}\nЗаказчик: {ads[0]['cli_name']}\nОтзыв: {ads[0]['short']}\n")
    else:
        bot.send_message(chat_id=message.chat.id, text='Couldn\'t find company')


bot.polling(none_stop=True)
