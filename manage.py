#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def main():
    """Run administrative tasks with environment-specific settings."""
    # Set default settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    
    # Set production settings if DJANGO_ENV is set to 'production'
    if os.getenv('DJANGO_ENV') == 'production':
        os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.production'
    # Set test settings if running tests
    elif 'test' in sys.argv or 'pytest' in sys.argv[0]:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.test'
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Add the project root to the Python path
    current_path = Path(__file__).parent.resolve()
    sys.path.append(str(current_path))
    
    try:
        execute_from_command_line(sys.argv)
    except Exception as e:
        # Handle errors in a user-friendly way
        from django.core.management.utils import get_random_secret_key
        
        if 'SECRET_KEY' in str(e) and 'The SECRET_KEY setting must not be empty' in str(e):
            # Suggest setting a secret key if it's missing
            print("Error: SECRET_KEY is not set in your environment variables.")
            print("You can generate a new one by running:")
            print(f"export SECRET_KEY='{get_random_secret_key()}'")
            print("Then add it to your .env file and restart the server.")
            sys.exit(1)
        else:
            # Re-raise the original exception
            raise e


if __name__ == '__main__':
    main()
