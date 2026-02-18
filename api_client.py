import requests
import time
from typing import Dict, Optional, Tuple
from logger import logger, log_error, log_info, log_warning
from config import API_CONFIG

class CurrencyAPIClient:
    def __init__(self):
        self.base_url = API_CONFIG['base_url']
        self.api_key = API_CONFIG['api_key']
        self.base_currency = API_CONFIG['base_currency']
        self.target_currencies = API_CONFIG['target_currencies']
        self.session = requests.Session()
        self.session.timeout = 10
        
        self.session.headers.update({
            'User-Agent': 'CurrencyTracker/1.0',
            'Accept': 'application/json',
        })
    
    def _make_request(self, url: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        try:
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('result') == 'success':
                    return True, data, None
                else:
                    error_msg = data.get('error-type', 'Unknown API error')
                    return False, None, f"API Error: {error_msg}"
            elif response.status_code == 401:
                return False, None, "Invalid API key"
            elif response.status_code == 403:
                return False, None, "API access forbidden"
            elif response.status_code == 429:
                return False, None, "Rate limit exceeded"
            elif response.status_code == 500:
                return False, None, "Internal server error"
            else:
                return False, None, f"HTTP {response.status_code}: {response.reason}"
                
        except requests.exceptions.Timeout:
            return False, None, "Request timeout"
        except requests.exceptions.ConnectionError:
            return False, None, "Connection error"
        except requests.exceptions.RequestException as e:
            return False, None, f"Request error: {str(e)}"
        except ValueError as e:
            return False, None, f"JSON decode error: {str(e)}"
        except Exception as e:
            return False, None, f"Unexpected error: {str(e)}"
    
    def get_latest_rates(self) -> Tuple[bool, Optional[Dict[str, float]], Optional[str]]:
        if not self.api_key:
            return False, None, "API key is not configured"
        
        url = f"{self.base_url}/{self.api_key}/latest/{self.base_currency}"
        
        log_info(logger, f"Requesting currency rates from {self.base_currency}")
        
        success, data, error_msg = self._make_request(url)
        
        if not success:
            log_error(logger, "Failed to get currency rates", Exception(error_msg))
            return False, None, error_msg
        
        try:
            rates = data.get('conversion_rates', {})
            filtered_rates = {}
            
            for currency in self.target_currencies:
                if currency in rates:
                    filtered_rates[currency] = float(rates[currency])
                else:
                    log_warning(logger, f"Currency {currency} not found in API response")
            
            if not filtered_rates:
                return False, None, "No target currencies found in API response"
            
            log_info(logger, f"Received {len(filtered_rates)} currency rates")
            return True, filtered_rates, None
            
        except Exception as e:
            error_msg = f"Error processing API response: {str(e)}"
            log_error(logger, error_msg, e)
            return False, None, error_msg
    
    def health_check(self) -> bool:
        success, _, error_msg = self.get_latest_rates()
        if success:
            log_info(logger, "API health check passed")
            return True
        else:
            log_error(logger, "API health check failed", Exception(error_msg))
            return False

api_client = CurrencyAPIClient()