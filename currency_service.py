#!/usr/bin/env python3
import schedule
import time
from datetime import datetime
from typing import Dict, Optional
from logger import logger, log_error, log_info
from config import SCHEDULER_CONFIG
from database import db_manager
from api_client import api_client

class CurrencyService:
    def __init__(self):
        self.db_connected = False
        self.api_healthy = False
    
    def initialize(self) -> bool:
        log_info(logger, "=== INITIALIZING CURRENCY SERVICE ===")
        
        if not db_manager.connect():
            log_error(logger, "Failed to connect to database")
            return False
        self.db_connected = True
        
        if not db_manager.create_tables():
            log_error(logger, "Failed to create database tables")
            return False
        
        if not api_client.health_check():
            log_error(logger, "API is unavailable or misconfigured")
            return False
        self.api_healthy = True
        
        log_info(logger, "Service initialized successfully")
        return True
    
    def fetch_and_store_rates(self):
        log_info(logger, "=== STARTING CURRENCY RATES REQUEST ===")
        
        request_id = db_manager.insert_request(
            request_type='currency_rates',
            status='pending'
        )
        
        if not request_id:
            log_error(logger, "Failed to create request record")
            return
        
        success, rates, error_msg = api_client.get_latest_rates()
        
        if success and rates:
            success_request_id = db_manager.insert_request(
                request_type='currency_rates',
                status='success'
            )
            
            if success_request_id:
                if db_manager.insert_currency_rates(success_request_id, rates):
                    log_info(logger, f"Rates saved successfully: {len(rates)}")
                else:
                    log_error(logger, "Error saving currency rates")
            else:
                log_error(logger, "Failed to create success request record")
        else:
            error_request_id = db_manager.insert_request(
                request_type='currency_rates',
                status='error',
                error_message=error_msg
            )
            log_error(logger, f"Error getting rates: {error_msg}")
        
        log_info(logger, "=== COMPLETED CURRENCY RATES REQUEST ===")
    
    def show_statistics(self):
        log_info(logger, "=== SERVICE STATISTICS ===")
        
        if not self.db_connected:
            log_error(logger, "Database unavailable")
            return
        
        latest_rates = db_manager.get_latest_rates()
        if latest_rates:
            log_info(logger, "Latest currency rates:")
            for rate in latest_rates:
                log_info(logger, f"  {rate['currency_code']}: {rate['rate']} ({rate['timestamp']})")
        else:
            log_info(logger, "No currency rate data available")
        
        request_history = db_manager.get_request_history()
        if request_history:
            success_count = sum(1 for req in request_history if req['status'] == 'success')
            error_count = sum(1 for req in request_history if req['status'] == 'error')
            log_info(logger, f"Request statistics: Successful={success_count}, Errors={error_count}")
    
    def cleanup(self):
        log_info(logger, "Shutting down service...")
        if self.db_connected:
            db_manager.disconnect()
        log_info(logger, "Service stopped")

def job_wrapper():
    service = CurrencyService()
    if service.initialize():
        service.fetch_and_store_rates()
        service.show_statistics()
        service.cleanup()

def main():
    try:
        log_info(logger, "Starting currency rates service")
        
        job_wrapper()
        
        interval = SCHEDULER_CONFIG['interval_minutes']
        schedule.every(interval).minutes.do(job_wrapper)
        
        log_info(logger, f"Service scheduled to run every {interval} minutes")
        log_info(logger, "Press Ctrl+C to stop")
        
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except KeyboardInterrupt:
        log_info(logger, "Received shutdown signal (Ctrl+C)")
    except Exception as e:
        log_error(logger, "Critical error in main loop", e)
    finally:
        log_info(logger, "Service terminated")

if __name__ == "__main__":
    main()