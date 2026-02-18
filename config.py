import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'currency_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
}

# API configuration
API_CONFIG = {
    'base_url': os.getenv('API_BASE_URL', 'https://v6.exchangerate-api.com/v6'),
    'api_key': os.getenv('API_KEY', ''),
    'base_currency': 'USD',
    'target_currencies': ['EUR', 'GBP', 'JPY', 'RUB', 'CAD', 'AUD'],
}

# Scheduler configuration
SCHEDULER_CONFIG = {
    'interval_minutes': int(os.getenv('REQUEST_INTERVAL_MINUTES', 5)),
}

# Logging configuration
LOGGING_CONFIG = {
    'log_file': os.getenv('LOG_FILE', 'error.log'),
    'log_level': os.getenv('LOG_LEVEL', 'INFO'),
}

# Currencies to track
CURRENCIES = ['EUR', 'GBP', 'JPY', 'RUB', 'CAD', 'AUD', 'CHF', 'CNY']