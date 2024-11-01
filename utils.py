import logging
import time
from functools import wraps
import re
import smtplib
from config import config

# Setup logging with levels
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def log_message(message, level="info"):
    """Log messages with specific log levels."""
    if level == "info":
        logging.info(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "error":
        logging.error(message)
    else:
        logging.info(message)


# Retry Decorator for network calls
def retry(retries=3, delay=2, backoff=2):
    """Retry decorator for retrying network calls with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    log_message(f"Attempt {attempt + 1} failed for {func.__name__}: {e}", level="warning")
                    time.sleep(delay)
                    attempt += 1
                    delay *= backoff
            log_message(f"All {retries} retries failed for {func.__name__}", level="error")
            return None
        return wrapper
    return decorator


# Data Cleaning Utilities
def standardize_title(title):
    """Standardize media titles by removing unwanted characters and adjusting format for search accuracy."""
    # Remove special characters and trailing year info
    title = re.sub(r'\(\d{4}\)$', '', title)  # Remove year if in the format "(YYYY)"
    title = re.sub(r'[^\w\s]', '', title)  # Remove non-alphanumeric characters
    title = title.strip()
    return title


def get_email_smtp_client():
    """Helper to get an SMTP client based on configuration settings."""
    smtp_config = config["email"]
    server = smtplib.SMTP(smtp_config["smtp_server"], smtp_config["smtp_port"])
    server.starttls()
    server.login(smtp_config["sender"], smtp_config["password"])
    return server


# Example usage of retry decorator
@retry(retries=3, delay=2, backoff=2)
def fetch_data_with_retry():
    """Simulated network call to demonstrate retry behavior. Replace with actual network code."""
    # Example placeholder for a network call
    raise ConnectionError("Network call failed.")


# Enhanced error logging
def log_error(message):
    """Log errors specifically with error level."""
    log_message(message, level="error")
