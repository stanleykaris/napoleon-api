from .base import *  # noqa: F401, F403

# Import environment-specific settings
try:
    from .local import *  # noqa: F401, F403
except ImportError:
    pass

# Import production settings if needed
if os.getenv('DJANGO_SETTINGS_MODULE') == 'config.settings.production':
    from .production import *  # noqa: F401, F403
