import os
import requests
import datetime as dt
import smtplib

STOCK = "GOOGL"
COMPANY_NAME = "Google"

main_dir = os.path.dirname(__file__)

API_KEY_ALPHA = os.environ["API_KEY_ALPHA"]
alpha_api = "https://www.alphavantage.co/query"

API_KEY_NEWS = os.environ["API_KEY_NEWS"]
news_api = "https://newsapi.org/v2/everything"

my_email = "test5242023@gmail.com"
my_password = os.environ["EMAIL_PASSWORD"]

yesterday = dt.date.today() - dt.timedelta(days=1)
day_before_yesterday = yesterday - dt.timedelta(days=1)
yesterday_2 = day_before_yesterday - dt.timedelta(days=1)


def send_email(email_address, msg):
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(user=my_email, password=my_password)
        connection.sendmail(from_addr=my_email, to_addrs=email_address, msg=f"Subject:Stock Situation\n\n{msg}")
        print("Email Sent")


parameters_stocks = {
    "function": "TIME_SERIES_INTRADAY",
    "symbol": STOCK,
    "interval": "60min",
    "apikey": API_KEY_ALPHA,
    "outputsize": "compact",
}

response_stocks = requests.get(url=alpha_api, params=parameters_stocks)
response_stocks.raise_for_status()
stock_data = response_stocks.json()["Time Series (60min)"]
stock_situation = "down"

for day_and_hour in stock_data:
    if "19:00:00" in str(day_and_hour) and str(yesterday) in str(day_and_hour):
        stock_yesterday = stock_data[day_and_hour]["4. close"]
    if "19:00:00" in str(day_and_hour) and str(day_before_yesterday) in str(day_and_hour):
        stock_day_before_yesterday = stock_data[day_and_hour]["4. close"]
    if str(yesterday_2) in str(day_and_hour):
        break
    else:
        continue


percentage_of_difference = round(abs((float(stock_yesterday) - float(stock_day_before_yesterday)) / float(stock_day_before_yesterday)) * 100.0)
if stock_day_before_yesterday > stock_yesterday:
    stock_situation = "up"

parameters_news = {
    "q": COMPANY_NAME,
    "from": yesterday,
    "apiKey": API_KEY_NEWS,
}

data_news = requests.get(url=news_api, params=parameters_news)
data_news.raise_for_status()

data_news = data_news.json()["articles"][:5]
articles_list = [str(data_news[index]["title"] + ".\n" + data_news[index]["description"]).encode('ascii', 'ignore').decode('ascii')
                 + "\n\n" for index in range(len(data_news))]

articles = "".join(articles_list)
print(articles)

send_email("danielionut@puscas.xyz", f"{COMPANY_NAME} stock is {stock_situation}"
                                     f" by {percentage_of_difference}%\n" +
           f"Current value is ${stock_yesterday}\n\n" + articles)
