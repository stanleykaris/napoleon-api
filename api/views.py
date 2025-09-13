from rest_framework import viewsets, status, permissions, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F, Case, When, Value, IntegerField, BooleanField, Q, CharField
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import (
    Category, Quest, Challenge, 
    UserQuestProgress, UserChallengeCompletion,
    PartnerOrganization, Partnership
)
from .serializers import (
    UserSerializer, CategorySerializer, QuestSerializer, ChallengeSerializer,
    UserQuestProgressSerializer, UserChallengeCompletionSerializer,
    PartnerOrganizationSerializer, PartnershipSerializer
)

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for managing users"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'date_joined']

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        """Filter queryset based on user permissions"""
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Retrieve the current user's profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def set_password(self, request, pk=None):
        """Set a new password for the user"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info("set_password method called")
        user = self.get_object()
        if user != request.user and not request.user.is_staff:
            return Response(
                {"detail": "Not authorized to change this user's password."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        password = request.data.get('password')
        if not password:
            return Response(
                {"password": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(password)
        user.save()
        return Response({"status": "password set"})

class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']

class QuestViewSet(viewsets.ModelViewSet):
    """ViewSet for managing quests"""
    queryset = Quest.objects.all()
    serializer_class = QuestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['quest_type', 'difficulty', 'is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'difficulty', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter quests based on user's progress"""
        queryset = super().get_queryset()
        
        # Filter by user progress status if specified
        status_filter = self.request.query_params.get('user_status')
        if status_filter and self.request.user.is_authenticated:
            if status_filter == 'in_progress':
                in_progress_quests = UserQuestProgress.objects.filter(
                    user=self.request.user,
                    status='in_progress'
                ).values_list('quest_id', flat=True)
                queryset = queryset.filter(id__in=in_progress_quests)
            elif status_filter == 'completed':
                completed_quests = UserQuestProgress.objects.filter(
                    user=self.request.user,
                    status='completed'
                ).values_list('quest_id', flat=True)
                queryset = queryset.filter(id__in=completed_quests)
            elif status_filter == 'not_started':
                started_quests = UserQuestProgress.objects.filter(
                    user=self.request.user
                ).values_list('quest_id', flat=True)
                queryset = queryset.exclude(id__in=started_quests)
        
        # Annotate with user's progress status if authenticated
        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                user_status=Case(
                    When(user_progress__user=self.request.user, then=F('user_progress__status')),
                    default=Value('not_started'),
                    output_field=CharField()
                )
            )
        
        return queryset

    @action(detail=True, methods=['post'])
    def start_quest(self, request, pk=None):
        """Start a quest for the current user"""
        quest = self.get_object()
        user = request.user
        
        # Check if user already has progress for this quest
        progress, created = UserQuestProgress.objects.get_or_create(
            user=user,
            quest=quest,
            defaults={'status': 'in_progress', 'progress': 0}
        )
        
        if not created and progress.status == 'abandoned':
            progress.status = 'in_progress'
            progress.save()
        
        serializer = UserQuestProgressSerializer(progress)
        return Response(serializer.data, 
                      status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class ChallengeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing challenges"""
    serializer_class = ChallengeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['quest', 'is_required']
    search_fields = ['title', 'description']
    ordering_fields = ['order', 'title']
    ordering = ['order']

    def get_queryset(self):
        """Filter challenges based on query parameters"""
        queryset = Challenge.objects.all()
        
        # Filter by quest if specified
        quest_id = self.request.query_params.get('quest')
        if quest_id:
            queryset = queryset.filter(quest_id=quest_id)
        
        # Annotate with completion status if user is authenticated
        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                is_completed=Case(
                    When(completions__user=self.request.user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )
        
        return queryset

class UserQuestProgressViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user quest progress"""
    serializer_class = UserQuestProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['quest', 'status']
    ordering_fields = ['start_date', 'completion_date']
    ordering = ['-start_date']

    def get_queryset(self):
        """Filter progress records for the current user"""
        if self.request.user.is_staff:
            return UserQuestProgress.objects.all()
        return UserQuestProgress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Set the user to the current user when creating a new progress record"""
        serializer.save(user=self.request.user)

class UserChallengeCompletionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user challenge completions"""
    serializer_class = UserChallengeCompletionSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['challenge', 'challenge__quest']
    ordering_fields = ['completed_at']
    ordering = ['-completed_at']

    def get_queryset(self):
        """Filter completions for the current user"""
        if self.request.user.is_staff:
            return UserChallengeCompletion.objects.all()
        return UserChallengeCompletion.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Set the user to the current user when creating a new completion"""
        serializer.save(user=self.request.user)
        
        # Update quest progress
        challenge = serializer.validated_data['challenge']
        quest = challenge.quest
        
        # Get or create quest progress
        progress, created = UserQuestProgress.objects.get_or_create(
            user=self.request.user,
            quest=quest,
            defaults={'status': 'in_progress'}
        )
        
        # Update progress percentage
        total_challenges = quest.challenges.count()
        completed_challenges = UserChallengeCompletion.objects.filter(
            user=self.request.user,
            challenge__quest=quest
        ).values('challenge').distinct().count()
        
        progress.progress = int((completed_challenges / total_challenges) * 100)
        
        # Update status if completed
        if progress.progress >= 100:
            progress.status = 'completed'
            progress.completion_date = timezone.now()
        
        progress.save()

class PartnerOrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing partner organizations"""
    queryset = PartnerOrganization.objects.filter(is_active=True)
    serializer_class = PartnerOrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'contact_email']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

class PartnershipViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing partnerships"""
    serializer_class = PartnershipSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['organization', 'quest', 'is_featured']
    ordering_fields = ['start_date', 'end_date']
    ordering = ['-start_date']

    def get_queryset(self):
        """Filter active partnerships"""
        queryset = Partnership.objects.filter(
            organization__is_active=True,
            start_date__lte=timezone.now().date()
        )
        
        # Filter out ended partnerships if end_date is set
        queryset = queryset.filter(
            Q(end_date__isnull=True) | 
            Q(end_date__gte=timezone.now().date())
        )
        
        return queryset
