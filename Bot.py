import telebot
from Parser import Parser


TOKEN = '1030953540:AAFt6-O5laMVRjO8hN1uA-dt7qZPPG0439c'
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(func=lambda message: True)
def get_text(message):
    user_message = message.text
    print(user_message)

    parser = Parser(user_message)
    ads = parser.ads[:len(parser.ads)//2]
    bot.send_message(chat_id=message.chat.id, text=ads)


bot.polling(none_stop=True)
