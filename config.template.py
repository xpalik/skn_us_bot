userside_settings = {
    'api_url': 'https://userside.yurdomain.ru/api.php?',
    'api_key': 'youkey',
    'browser_url': 'https://userside.yurdomain.ru/oper/journal.php?type=working&type2=show&code=',
    'pure_browser_url': 'https://userside.yurdomain.ru/'
}

telegram_settings = {
    'telegram_token': 'you_telega_tocken'
}

telegram_subscribers = [{
        'type': 'test',
        'name': 'Name',
        'phone': '+12345678',
        'channel_id': '12345689',
        'userside_params': {
            'division_id': '14',
            'state_id': '1'
        }
    }
]