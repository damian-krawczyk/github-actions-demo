from urllib.request import urlopen
import ssl
from bs4 import BeautifulSoup, SoupStrainer
import datetime
import os
import telegram
from translate import Translator

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://www.gov.pl/web/gis/ostrzezenia"

page = urlopen(url, context=ctx)
html = page.read().decode("utf-8")

product = SoupStrainer('article')
soup = BeautifulSoup(html, "html.parser", parse_only=product)

articles = soup.find_all("li")

article_list = []

for count, value in enumerate(articles, start=1):
    article_list.append({"id": count})

article_date = soup.find_all(class_="date")
for number, value in enumerate(article_date):
    article_list[number].update({"date": value.string.strip()})
    
article_name = soup.find_all(class_="title")
for number, value in enumerate(article_name):
    article_list[number].update({"title": value.string})
    
article_urls = soup.find_all(href=True)
for number, value in enumerate(article_urls):
    if value.parent.name == 'li':
        article_list[number].update({"url": "https://www.gov.pl"+value['href']}) 

yesterday = datetime.datetime.today() - datetime.timedelta(days=0)
yesterday = yesterday.strftime("%Y-%m-%d")

translator= Translator(from_lang="polish",to_lang="english")

telegram_token = os.environ['TELEGRAM_TOKEN']
bot = telegram.Bot(token=telegram_token)

warnings = False

for article_item in article_list:
    article_item_date = article_item['date']
    article_item_date = datetime.datetime.strptime(article_item_date, "%d.%m.%Y").strftime("%Y-%m-%d")


    if article_item_date == yesterday:
        print(article_item,"\n")
        warnings = True
        article_item_url = article_item['url']
        article_item_title = article_item['title']
        article_item_title_en = translator.translate(article_item_title)

        message = f"`{article_item_date}`\n**PL: **{article_item_title}\n---\n**EN: **{article_item_title_en}\n---\n[Szczegóły / Details]({article_item_url})"

        try:
            bot.send_message('@DamianTestChannel',text=message, parse_mode='Markdown')
            bot.send_message('@msi_pl_warnings',text=message, parse_mode='Markdown')
            bot.send_message('@gis_pl_ostrzezenia',text=message, parse_mode='Markdown')
            print("Message send successfully\n")
        except:
            print("Message sending error\n")

if not warnings:
    info = f"Brak ostrzeżeń na dzień {yesterday}"
    info_en = translator.translate(info)
    message = f"{info}\n{info_en}"
    print(message)

    bot.send_message('@DamianTestChannel',text=message, parse_mode='Markdown')