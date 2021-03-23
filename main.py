import requests
import config
import time
import telebot
from threading import Thread


def listener(messages):
    for m in messages:
        print(m)
        chat_id = m.chat.id
        if (m.content_type == 'text') and (m.text == 'chat_id'):
            text = 'chat_id: ' + str(chat_id)
            bot.send_message(chat_id, text)


def bot_polling():
    bot.polling()


def send_telegram(telegram_channel_id, text: str):
    telegram_url = 'https://api.telegram.org/bot'
    telegram_url += config.telegram_settings['telegram_token']
    method = telegram_url + '/sendMessage'
    r = requests.post(method, data={
        'chat_id': telegram_channel_id,
        'text': text
    })
    if r.status_code != 200:
        print('telegram error:', r)
        # raise Exception('post_text error')


class Person:
    def __init__(self, properties):
        self.properties = properties
        self.old_tickets = []
        self.to_send_tickets = []

    def check_tickets(self, is_first):
        # userside API check block
        params = {'key': config.userside_settings['api_key'],
                  'cat': 'task',
                  'action': 'get_list'}
        params.update(self.properties['userside_params'])
        api_response = requests.get(config.userside_settings['api_url'],
                                    params=params)
        current_tickets = api_response.json()['list'].split(',')

        # Get task to send
        for cur_ticket in current_tickets:
            is_sended = False
            for sended_ticket in self.old_tickets:
                if cur_ticket == sended_ticket:
                    is_sended = True
            if not is_sended:
                self.to_send_tickets.append(cur_ticket)
                self.old_tickets.append(cur_ticket)

        print(self.properties['name'], 'old =', self.old_tickets, 'send=', self.to_send_tickets)

        # Telegram send block
        if not is_first:
            if len(self.to_send_tickets) > 3:
                send_telegram(self.properties['channel_id'], 'В userside есть не закрытые заявки. %s'
                              % (config.userside_settings['pure_browser_url']))
            else:
                for ticket in self.to_send_tickets:
                    message = 'Новая заявка в userside. %s' % (config.userside_settings['browser_url'] + ticket)
                    send_telegram(self.properties['channel_id'], message)
        self.to_send_tickets = []

        # Clear self.old_tickets
        for sended_ticket in self.old_tickets:
            is_gone = True
            for cur_ticket in current_tickets:
                if cur_ticket == sended_ticket:
                    is_gone = False
            if is_gone:
                self.old_tickets.remove(sended_ticket)


def checker_loop(subs):
    is_first = True
    while True:
        for sub in subs:
            sub.check_tickets(is_first)
        time.sleep(60)
        is_first = False


def init_subscriber(subs_ar):
    subs_array = []
    for sub in subs_ar:
        subs_array.append(Person(sub))
    return subs_array


bot = telebot.TeleBot(config.telegram_settings['telegram_token'])
bot.set_update_listener(listener)
poling_tread = Thread(target=bot_polling, args=())
poling_tread.start()

checker_loop(init_subscriber(config.telegram_subscribers))
