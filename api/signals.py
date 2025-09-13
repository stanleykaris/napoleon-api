import logging
from datetime import timedelta

from django.db.models.signals import (
    post_save, pre_save, pre_delete, m2m_changed
)
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from .models import (
    UserQuestProgress, Quest, Challenge, 
    UserChallengeCompletion, PartnerOrganization, Partnership
)
from .tasks import send_notification_email

User = get_user_model()
logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create initial quest progress for new users
    """
    if created and not instance.is_superuser:
        # Create quest progress for all active quests
        active_quests = Quest.objects.filter(is_active=True)
        for quest in active_quests:
            UserQuestProgress.objects.get_or_create(
                user=instance,
                quest=quest,
                defaults={'status': 'not_started'}
            )
        
        # Send welcome email
        if instance.email:
            send_notification_email.delay(
                user_id=instance.id,
                subject_template='emails/welcome_email_subject.txt',
                message_template='emails/welcome_email.txt',
                context={
                    'first_name': instance.first_name or 'there',
                }
            )

@receiver(post_save, sender=Quest)
def create_quest_progress_for_all_users(sender, instance, created, **kwargs):
    """
    Signal to create quest progress for all users when a new quest is created
    """
    if created and instance.is_active:
        # Create quest progress for all active users
        for user in User.objects.filter(is_active=True):
            UserQuestProgress.objects.get_or_create(
                user=user,
                quest=instance,
                defaults={'status': 'not_started'}
            )

@receiver(post_save, sender=UserChallengeCompletion)
def update_quest_progress_on_challenge_completion(sender, instance, created, **kwargs):
    """
    Update the quest progress when a challenge is completed
    """
    if created:
        # Get the quest for this challenge
        quest = instance.challenge.quest
        
        # Get or create the quest progress
        progress, _ = UserQuestProgress.objects.get_or_create(
            user=instance.user,
            quest=quest,
            defaults={'status': 'in_progress'}
        )
        
        # Update progress percentage
        total_challenges = quest.challenges.count()
        completed_challenges = UserChallengeCompletion.objects.filter(
            user=instance.user,
            challenge__quest=quest
        ).values('challenge').distinct().count()
        
        new_progress = int((completed_challenges / total_challenges) * 100) if total_challenges > 0 else 0
        
        # Update progress
        progress.progress = new_progress
        
        # Check if quest is completed
        if new_progress >= 100 and progress.status != 'completed':
            progress.status = 'completed'
            progress.completion_date = timezone.now()
            
            # Award experience points
            instance.user.experience_points += quest.experience_reward
            instance.user.save(update_fields=['experience_points'])
            
            # Send notification
            send_notification_email.delay(
                user_id=instance.user.id,
                subject_template='emails/quest_completed_subject.txt',
                message_template='emails/quest_completed.txt',
                context={
                    'quest_title': quest.title,
                    'experience_reward': quest.experience_reward,
                }
            )
        
        progress.save()

@receiver(pre_save, sender=Quest)
def handle_quest_activation(sender, instance, **kwargs):
    """
    Handle quest activation/deactivation
    """
    if instance.pk:
        try:
            old_instance = Quest.objects.get(pk=instance.pk)
            
            # If quest is being activated
            if instance.is_active and not old_instance.is_active:
                # Create quest progress for all active users
                for user in User.objects.filter(is_active=True):
                    UserQuestProgress.objects.get_or_create(
                        user=user,
                        quest=instance,
                        defaults={'status': 'not_started'}
                    )
            # If quest is being deactivated
            elif not instance.is_active and old_instance.is_active:
                # Update all in-progress quests to abandoned
                UserQuestProgress.objects.filter(
                    quest=instance,
                    status='in_progress'
                ).update(status='abandoned')
                
        except Quest.DoesNotExist:
            pass

@receiver(m2m_changed, sender=Quest.categories.through)
def update_quest_categories(sender, instance, action, **kwargs):
    """
    Handle changes to quest categories
    """
    if action in ['post_add', 'post_remove', 'post_clear']:
        # Update quest search index or clear cache if needed
        instance.save(update_fields=['updated_at'])

@receiver(post_save, sender=Partnership)
def notify_partnership_created(sender, instance, created, **kwargs):
    """
    Send notifications when a new partnership is created
    """
    if created:
        # Notify organization contact
        send_notification_email.delay(
            user_id=instance.organization.contact_user.id if instance.organization.contact_user else None,
            subject_template='emails/partnership_created_subject.txt',
            message_template='emails/partnership_created.txt',
            context={
                'organization_name': instance.organization.name,
                'quest_title': instance.quest.title,
                'start_date': instance.start_date,
                'end_date': instance.end_date,
            }
        )

@receiver(pre_delete, sender=User)
def handle_user_deletion(sender, instance, **kwargs):
    """
    Handle cleanup when a user is deleted
    """
    # Anonymize user data instead of deleting
    instance.email = f'deleted_{instance.id}@example.com'
    instance.username = f'deleted_{instance.id}'
    instance.first_name = ''
    instance.last_name = ''
    instance.is_active = False
    instance.save(update_fields=[
        'email', 'username', 'first_name', 'last_name', 'is_active'
    ])
    
    # Cancel any scheduled tasks for this user
    # (implementation depends on your task queue)

@receiver(post_save, sender=Challenge)
def update_quest_on_challenge_change(sender, instance, created, **kwargs):
    """
    Update quest progress when a challenge is added, updated, or removed
    """
    quest = instance.quest
    
    # Get all users who have progress on this quest
    user_progress = UserQuestProgress.objects.filter(quest=quest)
    
    for progress in user_progress:
        # Recalculate progress
        total_challenges = quest.challenges.count()
        if total_challenges == 0:
            progress.progress = 0
        else:
            completed_challenges = UserChallengeCompletion.objects.filter(
                user=progress.user,
                challenge__quest=quest
            ).values('challenge').distinct().count()
            progress.progress = int((completed_challenges / total_challenges) * 100)
        
        # Update status if needed
        if progress.progress >= 100 and progress.status != 'completed':
            progress.status = 'completed'
            progress.completion_date = timezone.now()
        elif progress.progress > 0 and progress.status == 'not_started':
            progress.status = 'in_progress'
        
        progress.save()
