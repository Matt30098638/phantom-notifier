import os
import yaml

# Load environment configuration
ENV = os.getenv("APP_ENV", "development")  # Default to 'development' if not set

# Path to config files
CONFIG_PATHS = {
    "development": "config.yaml",
}

# Load configuration
def load_config():
    """Load configuration based on environment."""
    config_path = CONFIG_PATHS.get(ENV)
    if not config_path or not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file for {ENV} environment not found.")
    
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)

config = load_config()


# Validation of Required Configurations
def validate_config_section(section_name, required_keys):
    """Ensure that the specified section in config contains all required keys."""
    section = config.get(section_name, {})
    missing_keys = [key for key in required_keys if key not in section]
    if missing_keys:
        raise ValueError(f"Missing required configuration keys in '{section_name}': {', '.join(missing_keys)}")
    return section


# Config Retrieval Functions
def get_jellyfin_config():
    """Retrieve and validate Jellyfin configuration."""
    return validate_config_section("jellyfin", ["url", "api_key"])


def get_tmdb_config():
    """Retrieve and validate TMDB configuration."""
    return validate_config_section("tmdb", ["api_key"])


def get_email_config():
    """Retrieve and validate email configuration."""
    return validate_config_section("email", ["smtp_server", "smtp_port", "sender", "password"])


# Usage Examples (Functions to fetch configurations with validations)
jellyfin_config = get_jellyfin_config()
tmdb_config = get_tmdb_config()
email_config = get_email_config()

# Optionally, log the environment for clarity
print(f"Loaded configuration for {ENV} environment.")
