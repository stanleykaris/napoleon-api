from django.conf import settings

def site_info(request):
    """Add site information to the template context."""
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Napoleon API'),
        'SITE_URL': getattr(settings, 'SITE_URL', 'http://localhost:8000'),
        'ENVIRONMENT': getattr(settings, 'ENVIRONMENT', 'development'),
        'VERSION': getattr(settings, 'VERSION', '1.0.0'),
        'GOOGLE_ANALYTICS_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
    }

def user_notifications(request):
    """Add user notifications to the template context."""
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return {}
        
    # Get unread notifications count (example implementation)
    unread_count = 0
    if hasattr(request.user, 'notifications'):
        unread_count = request.user.notifications.unread().count()
    
    return {
        'unread_notifications_count': unread_count,
    }
