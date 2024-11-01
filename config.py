import os
import yaml
import logging

# Environment setup and logging
ENV = os.getenv("APP_ENV", "development")
CONFIG_PATHS = {
    "development": "config/dev_config.yaml",
    "production": "config/prod_config.yaml"
}

def load_config():
    """Load configuration based on the environment."""
    config_path = CONFIG_PATHS.get(ENV)
    if not config_path or not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file for {ENV} environment not found.")

    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# Global config variable
config_data = load_config()

def get_section(section):
    """Retrieve a section of the configuration."""
    if section not in config_data:
        logging.error(f"Missing '{section}' section in configuration.")
    return config_data.get(section, {})

# Convenience functions to retrieve specific configs
def get_jellyfin_config():
    return get_section("jellyfin")

def get_tmdb_config():
    return get_section("tmdb")

def get_email_config():
    return get_section("email")
