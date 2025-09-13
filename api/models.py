from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    """Custom user model for Napoleon API"""
    email = models.EmailField(_('email address'), unique=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    experience_points = models.PositiveIntegerField(default=0)
    level = models.PositiveSmallIntegerField(default=1)
    
    # Track user preferences
    is_subscribed = models.BooleanField(default=False)
    notification_preferences = models.JSONField(default=dict)
    
    def __str__(self):
        return self.username

class Category(models.Model):
    """Categories for quests and challenges"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    
    class Meta:
        verbose_name_plural = 'categories'
        
    def __str__(self):
        return self.name

class Quest(models.Model):
    """Main quest model for outdoor adventures"""
    QUEST_TYPES = [
        ('outdoor', 'Outdoor Adventure'),
        ('indoor', 'Indoor Challenge'),
        ('social', 'Social Challenge'),
    ]
    
    DIFFICULTY_LEVELS = [
        (1, 'Easy'),
        (2, 'Moderate'),
        (3, 'Challenging'),
        (4, 'Expert'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    quest_type = models.CharField(max_length=20, choices=QUEST_TYPES)
    difficulty = models.PositiveSmallIntegerField(
        choices=DIFFICULTY_LEVELS,
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
    categories = models.ManyToManyField(Category, related_name='quests')
    duration_minutes = models.PositiveIntegerField(help_text="Estimated duration in minutes")
    experience_reward = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_quest_type_display()}: {self.title}"

class Challenge(models.Model):
    """Individual challenges within quests"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name='challenges')
    order = models.PositiveSmallIntegerField(help_text="Order in which challenges appear in the quest")
    is_required = models.BooleanField(default=True)
    experience_reward = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return f"{self.quest.title} - {self.title}"

class UserQuestProgress(models.Model):
    """Tracks user progress through quests"""
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quest_progress')
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name='user_progress')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    start_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    progress = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(100)])
    
    class Meta:
        verbose_name_plural = 'User Quest Progress'
        unique_together = ('user', 'quest')
    
    def __str__(self):
        return f"{self.user.username} - {self.quest.title} ({self.status})"

class UserChallengeCompletion(models.Model):
    """Tracks user completion of individual challenges"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='challenge_completions')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='completions')
    completed_at = models.DateTimeField(auto_now_add=True)
    evidence = models.TextField(blank=True, help_text="User's description or proof of completion")
    evidence_photo = models.ImageField(upload_to='challenge_evidence/', null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'challenge')
    
    def __str__(self):
        return f"{self.user.username} completed {self.challenge.title}"

class PartnerOrganization(models.Model):
    """Partner organizations like game parks and eco-organizations"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='partner_logos/', null=True, blank=True)
    contact_email = models.EmailField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Partnership(models.Model):
    """Partnerships between Napoleon and organizations"""
    organization = models.ForeignKey(PartnerOrganization, on_delete=models.CASCADE, related_name='partnerships')
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name='partnerships')
    benefits = models.TextField(help_text="Benefits for users who complete this quest through this partner")
    is_featured = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-is_featured', 'start_date']
    
    def __str__(self):
        return f"{self.organization.name} - {self.quest.title}"
