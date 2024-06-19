available_statuses = ['in_process', 'success', 'expired', 'hold']

current_payment_status_translated = {
    'in_process': {
        'ru': 'В процессе (Не оплачен)',
        'en': 'In progress (Not paid)',
    },
    'success': {
        'ru': 'Успешно оплачен',
        'en': 'Successfully paid',
    },
    'expired': {
        'ru': 'Истёк срок оплаты',
        'en': 'Payment deadline has expired',
    },
    'hold': {
        'ru': 'Оплачено, средства заморожены',
        'en': 'Paid, funds frozen',
    },

}
