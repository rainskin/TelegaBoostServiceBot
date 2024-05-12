lang_codes = ['ru', 'en']
lang_names = ['🇷🇺 Русский', '🇬🇧 English']


def default_language(user_lang_code: str):
    return user_lang_code if user_lang_code in lang_codes else 'en'



