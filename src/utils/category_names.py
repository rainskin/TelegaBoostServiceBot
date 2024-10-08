
def get_category_name(system_name: str):
    api_name = ''
    if system_name == 'views':
        api_name = 'Views Telegram'
    elif system_name == 'subscribers':
        api_name = 'Telegram Subscribers'
    elif system_name == 'premium_subscribers':
        api_name = 'Telegram Premium подписчики'
    elif system_name == 'boosts':
        api_name = 'Telegram Boost [БАЗА #1]'
    elif system_name == 'boosts_18':
        api_name = 'Telegram Boost [Для 18+ каналов]'
    elif system_name == 'reactions':
        api_name = 'Telegram Reactions'
    elif system_name == 'bot_launches':
        api_name = 'BOT START'
    elif system_name == 'vk':
        api_name = 'VK'
    elif system_name == 'twitch':
        api_name = 'Twitch'
    elif system_name == 'referrals':
        api_name = 'Рефералы в бот'

    return api_name
