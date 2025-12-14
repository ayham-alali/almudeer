"""Al-Mudeer Services Package"""

from .email_service import EmailService, EMAIL_PROVIDERS
from .telegram_service import TelegramService, TelegramBotManager, TELEGRAM_SETUP_GUIDE

__all__ = [
    'EmailService',
    'EMAIL_PROVIDERS',
    'TelegramService', 
    'TelegramBotManager',
    'TELEGRAM_SETUP_GUIDE'
]

