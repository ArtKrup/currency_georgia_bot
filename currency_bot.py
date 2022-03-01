import json
import time
import requests
import schedule
from bs4 import BeautifulSoup


def call_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def find_currency_rico():
    soup = call_url('https://www.rico.ge/')
    quotes = soup.find_all('td', class_='h5 font-weight-bold text-primary')
    rico_list = []
    for item in quotes[:2]:
        rico_list.append(item.text.strip().replace(',', '.'))

    return rico_list


def find_currency_state_bank():
    soup = call_url('http://www.finmarket.ru/currency/rates/?id=10122')
    quotes = soup.find_all('div', class_='info')
    state_rate = quotes[0].text[3:9].replace(',', '.')

    return state_rate


def find_currency_credo():
    soup = call_url('https://credobank.ge/')
    quotes = soup.find_all('div', class_='currency-item firago medium flex-wrap')
    credo_list = []
    credo_list.append(quotes[0].text[8:14].replace(',', '.'))
    credo_list.append(quotes[0].text[15:21].replace(',', '.'))
    return credo_list


def find_currency_mbc():
    soup = call_url('https://fxrates.mbc.com.ge:8022/api/fxrates/mbc/commercial?fbclid=IwAR0YnhhhQgvHblGe06uyIwQmyv4s8ngxTjZInSVlTKvKNcMZshPdaoydFfo/api/fxrates/mbc/commercial')
    quotes = str(soup.p)[3:-4]
    mbc_list = []
    json_obj = json.loads(quotes)
    mbc_list.append(json_obj['FXRates'][4]['Buy'])
    mbc_list.append(json_obj['FXRates'][4]['Sell'])

    return mbc_list


def send_message_to_bot(text, chat_id='1288690761'):
    parameters = {'chat_id': chat_id, 'text': text}
    bot = 'https://api.telegram.org/bot5261629533:AAE8K9wLxUssY2ak6nIF2xk-wOaDK7KNn_4/'
    requests.post(bot + 'sendMessage', data=parameters)


def daily_report():
    moment = time.strftime("%H:%M")
    currency_dict = {}
    currency_state = float(find_currency_state_bank())
    total_message = f'Время {moment} \n'
    currency_dict['Курс Доллара в Rico'] = float(find_currency_rico()[0])
    currency_dict['Курс Доллара в Credo'] = float(find_currency_credo()[0])
    currency_dict['Курс Доллара в MBC'] = float(find_currency_mbc()[0])

    best_currency_value = max(currency_dict.values())

    if currency_state < currency_dict['Курс Доллара в Rico'] and best_currency_value == currency_dict[
        'Курс Доллара в Rico']:
        sell_message = 'Выгодно сдать доллары в Rico'
        safe = round((currency_dict['Курс Доллара в Rico'] - currency_state) * 900, 2)

    if currency_state < currency_dict['Курс Доллара в Credo'] and best_currency_value == currency_dict[
        'Курс Доллара в Credo']:
        sell_message = 'Выгодно сдать доллары в Credo'
        safe = round((currency_dict['Курс Доллара в Credo'] - currency_state) * 900, 2)

    if currency_state < currency_dict['Курс Доллара в MBC'] and best_currency_value == currency_dict[
        'Курс Доллара в MBC']:
        sell_message = 'Выгодно сдать доллары в MBC'
        safe = round((currency_dict['Курс Доллара в MBC'] - currency_state) * 900, 2)

    else:
        sell_message = 'Не выгодно сдавать доллары сегодня'
        safe = round((best_currency_value - currency_state) * 900, 2)
    safe_message = f'Выгода за 900 долларов составит {safe} Лари'

    total_message += f'Курс Нац.Банка Грузии : {currency_state} \n'

    for i, v in currency_dict.items():
        total_message += (f'{i} : {v} \n')
    total_message += f'{sell_message} \n'
    total_message += f'{safe_message} \n'

    send_message_to_bot(total_message)

daily_report()


schedule.every().day.at("11:00").do(daily_report)
schedule.every().day.at("15:00").do(daily_report)

# run script infinitely
while True:
    schedule.run_pending()
