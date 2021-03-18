import requests
import config
import time


def send_telegram(telegram_channel_id, text: str):
    telegram_url = 'https://api.telegram.org/bot'
    telegram_url += config.telegram_settings['telegram_token']
    method = telegram_url + '/sendMessage'
    r = requests.post(method, data={
        'chat_id': telegram_channel_id,
        'text': text
    })
    if r.status_code != 200:
        raise Exception('post_text error')


class Person:
    def __init__(self, properties):
        self.properties = properties
        self.old_tickets = []
        self.to_send_tickets = []

    def check_tickets(self):
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
        if len(self.to_send_tickets) > 2:
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
    while True:
        for sub in subs:
            sub.check_tickets()
            time.sleep(10)


def init_subscriber(subs_ar):
    for sub in subs_ar:
        return Person(sub)


subs_array = [init_subscriber(config.telegram_subscribers)]
checker_loop(subs_array)
