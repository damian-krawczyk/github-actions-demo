import os
import telegram
from translate import Translator

translator= Translator(from_lang="polish",to_lang="english")

telegram_token = os.environ['TELEGRAM_TOKEN']

bot = telegram.Bot(token=telegram_token)

message_content = "Wiadomość testowa"
message_content_en = translator.translate(message_content)

message = f"{message_content}\n{message_content_en}"

try:
    bot.send_message('@DamianTestChannell',text=message, parse_mode='Markdown')
    print("Message send successfully")
except:
    print("Message sending error")
