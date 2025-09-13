from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Category, Quest, Challenge, 
    UserQuestProgress, UserChallengeCompletion,
    PartnerOrganization, Partnership
)

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'bio', 'profile_picture', 'experience_points', 'level',
            'is_subscribed', 'date_joined'
        )
        read_only_fields = ('id', 'date_joined', 'experience_points', 'level')
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def create(self, validated_data):
        """Create and return a new user with encrypted password"""
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly if provided"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for the Category model"""
    class Meta:
        model = Category
        fields = '__all__'

class ChallengeSerializer(serializers.ModelSerializer):
    """Serializer for the Challenge model"""
    class Meta:
        model = Challenge
        fields = '__all__'
        read_only_fields = ('quest',)

class QuestSerializer(serializers.ModelSerializer):
    """Serializer for the Quest model"""
    challenges = ChallengeSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Category.objects.all(),
        source='categories'
    )
    
    class Meta:
        model = Quest
        fields = [
            'id', 'title', 'description', 'quest_type', 'difficulty',
            'duration_minutes', 'experience_reward', 'is_active',
            'created_at', 'updated_at', 'challenges', 'categories', 'category_ids'
        ]
        read_only_fields = ('id', 'created_at', 'updated_at', 'challenges')

class UserChallengeCompletionSerializer(serializers.ModelSerializer):
    """Serializer for UserChallengeCompletion model"""
    challenge_title = serializers.CharField(source='challenge.title', read_only=True)
    
    class Meta:
        model = UserChallengeCompletion
        fields = ['id', 'challenge', 'challenge_title', 'completed_at', 'evidence', 'evidence_photo']
        read_only_fields = ('id', 'completed_at', 'challenge_title')

class UserQuestProgressSerializer(serializers.ModelSerializer):
    """Serializer for UserQuestProgress model"""
    quest_title = serializers.CharField(source='quest.title', read_only=True)
    quest_type = serializers.CharField(source='quest.quest_type', read_only=True)
    quest_difficulty = serializers.IntegerField(source='quest.difficulty', read_only=True)
    challenge_completions = UserChallengeCompletionSerializer(many=True, read_only=True)
    
    class Meta:
        model = UserQuestProgress
        fields = [
            'id', 'quest', 'quest_title', 'quest_type', 'quest_difficulty',
            'status', 'start_date', 'completion_date', 'progress',
            'challenge_completions'
        ]
        read_only_fields = ('id', 'progress', 'challenge_completions')

class PartnerOrganizationSerializer(serializers.ModelSerializer):
    """Serializer for PartnerOrganization model"""
    class Meta:
        model = PartnerOrganization
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

class PartnershipSerializer(serializers.ModelSerializer):
    """Serializer for Partnership model"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    quest_title = serializers.CharField(source='quest.title', read_only=True)
    
    class Meta:
        model = Partnership
        fields = [
            'id', 'organization', 'organization_name', 'quest', 'quest_title',
            'benefits', 'is_featured', 'start_date', 'end_date'
        ]
        read_only_fields = ('id', 'organization_name', 'quest_title')
