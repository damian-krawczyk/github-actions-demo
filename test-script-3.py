from urllib.request import urlopen
import ssl
from bs4 import BeautifulSoup, SoupStrainer
import datetime
import os
import telegram
from translate import Translator
import dateparser

def get_articles(url, date=None):

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    page = urlopen(url, context=ctx)
    html = page.read().decode("utf-8")

    product = SoupStrainer('article')
    soup = BeautifulSoup(html, "html.parser", parse_only=product)

    articles = soup.find_all("li")

    article_list = []

    for count, article in enumerate(articles):
        article_date = article.find_all(class_="date")
        article_date = article_date[0].string.strip()
        article_date = datetime.datetime.strptime(article_date, "%d.%m.%Y").strftime("%Y-%m-%d")

        if date:
            if article_date == date:
                article_list.append({"id": count})

                article_list[count].update({"date": article_date})
                
                article_name = article.find_all(class_="title")
                article_list[count].update({"title": article_name[0].string})

                article_intro = article.find_all(class_="intro")
                if article_intro:
                    article_list[count].update({"intro": article_intro[0].string})
                else:
                    article_list[count].update({"intro": None})

                article_urls = article.find_all(href=True)
                article_list[count].update({"url": "https://www.gov.pl"+article_urls[0]['href']})
        else:
            article_list.append({"id": count})

            article_list[count].update({"date": article_date})
            
            article_name = article.find_all(class_="title")
            article_list[count].update({"title": article_name[0].string})

            article_intro = article.find_all(class_="intro")
            if article_intro:
                article_list[count].update({"intro": article_intro[0].string})
            else:
                article_list[count].update({"intro": None})

            article_urls = article.find_all(href=True)
            article_list[count].update({"url": "https://www.gov.pl"+article_urls[0]['href']}) 

    if not article_list:
        article_list.append({"warning": f"Brak artykułów na dzień {date}"})

    return article_list

def send_message(article, feed_name, channel, test_channel, token):
    translator= Translator(from_lang="polish",to_lang="english")

    bot = telegram.Bot(token=token)

    if 'warning' in article:
        info = article['warning']
        info_en = translator.translate(info)
        message = f"{feed_name}\n{info}\n{info_en}"
        print(message)
        bot.send_message(test_channel,text=message, parse_mode='Markdown')

    else:
        date = article['date']
        title = article['title']
        title_en = translator.translate(title)
        intro = article['intro']
        intro_en = translator.translate(intro)
        url = article['url']

        message = f"`{date}`\n**PL:** {title}\n\n{intro}\n---\n**EN:** {title_en}\n\n{intro_en}\n---\n[Szczegóły / Details]({url})"
        print(message)
        bot.send_message(channel,text=message, parse_mode='Markdown')


url = os.environ['FEED_URL']
given_date = dateparser.parse(os.environ['GIVEN_DATE'], date_formats=["%Y-%m-%d"]).strftime("%Y-%m-%d")
feed_name = os.environ['FEED_NAME']
channel = os.environ['CHANNEL_URL']
test_channel = os.environ['TEST_CHANNEL_URL']
token = os.environ['TELEGRAM_TOKEN']

article_list = get_articles(url, given_date)

for article in article_list:
    # print(article,"\n")
    send_message(article, feed_name, channel, test_channel, token)