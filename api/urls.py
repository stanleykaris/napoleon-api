from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'quests', views.QuestViewSet)
router.register(r'challenges', views.ChallengeViewSet)
router.register(r'quest-progress', views.UserQuestProgressViewSet, basename='questprogress')
router.register(r'challenge-completions', views.UserChallengeCompletionViewSet, basename='challengecompletion')
router.register(r'partners', views.PartnerOrganizationViewSet)
router.register(r'partnerships', views.PartnershipViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    
    # Include authentication URLs for the browsable API
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    # JWT Authentication endpoints
    path('auth/', include('rest_framework_simplejwt.urls')),
]

# Add a root view for the API
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'quests': reverse('quest-list', request=request, format=format),
        'categories': reverse('category-list', request=request, format=format),
        'challenges': reverse('challenge-list', request=request, format=format),
        'partners': reverse('partnerorganization-list', request=request, format=format),
        'partnerships': reverse('partnership-list', request=request, format=format),
        'documentation': 'https://github.com/yourusername/napoleon-api/docs',
    })

urlpatterns += [
    path('', api_root, name='api-root'),
]
