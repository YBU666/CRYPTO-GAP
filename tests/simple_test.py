"""
Simple test script for CryptoGap+ application
"""
import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_cryptogap')

def test_project_structure():
    """Test if all required files and directories exist"""
    logger.info("Testing project structure...")
    
    # Check directories
    directories = [
        'data', 'utils', 'models', 'config', 'tests'
    ]
    
    for directory in directories:
        if os.path.isdir(directory):
            logger.info(f"✓ Directory '{directory}' exists")
        else:
            logger.error(f"✗ Directory '{directory}' does not exist")
            return False
    
    # Check key files
    files = [
        'app.py',
        'data/binance_fetcher.py',
        'data/kraken_fetcher.py',
        'utils/arbitrage_calculator.py',
        'models/llm_analyzer.py',
        'config/config.py'
    ]
    
    for file in files:
        if os.path.isfile(file):
            logger.info(f"✓ File '{file}' exists")
        else:
            logger.error(f"✗ File '{file}' does not exist")
            return False
    
    logger.info("Project structure test passed")
    return True

def test_app_imports():
    """Test if the main app can import all required modules"""
    logger.info("Testing app imports...")
    
    try:
        # Test importing modules directly
        import data.binance_fetcher
        import data.kraken_fetcher
        import utils.arbitrage_calculator
        import models.llm_analyzer
        import config.config
        
        logger.info("✓ All modules imported successfully")
        return True
    except Exception as e:
        logger.error(f"✗ Error importing modules: {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    logger.info("Starting CryptoGap+ tests")
    
    results = {
        "Project Structure": test_project_structure(),
        "App Imports": test_app_imports()
    }
    
    # Print summary
    logger.info("Test Results Summary:")
    all_passed = True
    
    for test, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        logger.info(f"{test}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        logger.info("All tests passed successfully!")
    else:
        logger.error("Some tests failed. Check logs for details.")
    
    return all_passed

if __name__ == "__main__":
    run_all_tests()
