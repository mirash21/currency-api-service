#!/usr/bin/env python3
import sys
import os
from datetime import datetime
from logger import logger, log_info, log_error
from database import db_manager
from api_client import api_client

def test_database_connection():
    log_info(logger, "=== TESTING DATABASE CONNECTION ===")
    
    if db_manager.connect():
        log_info(logger, "✓ Database connection established")
        
        if db_manager.create_tables():
            log_info(logger, "✓ Tables created successfully")
        else:
            log_error(logger, "✗ Error creating tables")
            return False
            
        db_manager.disconnect()
        log_info(logger, "✓ Connection closed")
        return True
    else:
        log_error(logger, "✗ Failed to connect to database")
        return False

def test_api_connection():
    log_info(logger, "=== TESTING API CONNECTION ===")
    
    if api_client.health_check():
        log_info(logger, "✓ API is working correctly")
        return True
    else:
        log_error(logger, "✗ API unavailable or misconfigured")
        return False

def test_data_retrieval():
    log_info(logger, "=== TESTING DATA RETRIEVAL ===")
    
    success, rates, error_msg = api_client.get_latest_rates()
    
    if success and rates:
        log_info(logger, f"✓ Received {len(rates)} currency rates:")
        for currency, rate in list(rates.items())[:5]:
            log_info(logger, f"  {currency}: {rate}")
        if len(rates) > 5:
            log_info(logger, f"  ... and {len(rates) - 5} more currencies")
        return True
    else:
        log_error(logger, f"✗ Error retrieving data: {error_msg}")
        return False

def main():
    print("=" * 60)
    print("CURRENCY SERVICE TESTING")
    print("=" * 60)
    print()
    
    tests = [
        ("Database connection", test_database_connection),
        ("API connection", test_api_connection),
        ("Data retrieval", test_data_retrieval),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                passed_tests += 1
                print("✓ TEST PASSED")
            else:
                print("✗ TEST FAILED")
        except Exception as e:
            print(f"✗ TEST ENDED WITH ERROR: {e}")
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed_tests}/{total_tests} tests passed")
    print("=" * 60)
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Service is ready to run.")
        print("\nTo start the service:")
        print("python currency_service.py")
    else:
        print("❌ Some tests failed. Check configuration.")

if __name__ == "__main__":
    main()