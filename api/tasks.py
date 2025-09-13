"""Celery tasks for the api app."""
import logging
from datetime import datetime, timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from .models import UserQuestProgress, Quest, User

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def update_quest_status(self):
    """Update the status of all in-progress quests."""
    try:
        # Get all in-progress quests
        in_progress_quests = UserQuestProgress.objects.filter(
            status='in_progress'
        ).select_related('quest', 'user')
        
        updated_count = 0
        now = timezone.now()
        
        for progress in in_progress_quests:
            # Check if quest has expired
            if progress.quest.expires_at and progress.quest.expires_at < now:
                progress.status = 'expired'
                progress.save(update_fields=['status', 'updated_at'])
                updated_count += 1
                continue
                
            # Check if all challenges are completed
            total_challenges = progress.quest.challenges.count()
            completed_challenges = progress.user.challenge_completions.filter(
                challenge__quest=progress.quest
            ).count()
            
            # Update progress percentage
            if total_challenges > 0:
                new_progress = int((completed_challenges / total_challenges) * 100)
                if new_progress != progress.progress:
                    progress.progress = new_progress
                    
                    # Mark as completed if all challenges are done
                    if new_progress >= 100:
                        progress.status = 'completed'
                        progress.completion_date = now
                        
                        # Award experience points to the user
                        progress.user.experience_points += progress.quest.experience_reward
                        progress.user.save(update_fields=['experience_points'])
                    
                    progress.save(
                        update_fields=['progress', 'status', 'completion_date', 'updated_at']
                    )
                    updated_count += 1
        
        logger.info(f"Updated status for {updated_count} quests.")
        return f"Updated {updated_count} quests."
        
    except Exception as e:
        logger.error(f"Error updating quest status: {e}", exc_info=True)
        # Retry the task with exponential backoff
        raise self.retry(exc=e, countdown=60 * 5)  # Retry after 5 minutes


@shared_task(bind=True, max_retries=3)
def send_daily_digest(self):
    """Send a daily digest email to users with their quest progress."""
    try:
        # Get all active users who want to receive emails
        users = User.objects.filter(
            is_active=True,
            notification_preferences__daily_digest=True
        )
        
        sent_count = 0
        for user in users:
            # Get user's in-progress quests
            in_progress_quests = UserQuestProgress.objects.filter(
                user=user,
                status='in_progress'
            ).select_related('quest')
            
            # Skip if user has no in-progress quests
            if not in_progress_quests.exists():
                continue
            
            # Get new quests available
            new_quests = Quest.objects.filter(
                is_active=True,
                created_at__gte=timezone.now() - timedelta(days=7)
            ).exclude(
                id__in=in_progress_quests.values_list('quest_id', flat=True)
            )[:3]  # Limit to 3 new quests
            
            # Render email content
            context = {
                'user': user,
                'in_progress_quests': in_progress_quests,
                'new_quests': new_quests,
                'site_name': 'Napoleon API',
                'base_url': settings.SITE_URL,
            }
            
            subject = f"Your Daily Quest Digest - {timezone.now().strftime('%B %d, %Y')}"
            message = render_to_string('emails/daily_digest.txt', context)
            html_message = render_to_string('emails/daily_digest.html', context)
            
            # Send email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            sent_count += 1
            
        logger.info(f"Sent daily digest to {sent_count} users.")
        return f"Sent daily digest to {sent_count} users."
        
    except Exception as e:
        logger.error(f"Error sending daily digest: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * 5)  # Retry after 5 minutes


@shared_task(bind=True, max_retries=3)
def send_notification_email(self, user_id, subject_template, message_template, context=None):
    """Send a notification email to a user.
    
    Args:
        user_id: ID of the user to send the email to
        subject_template: Path to the subject template
        message_template: Path to the message template
        context: Dictionary of context variables for the templates
    """
    try:
        user = User.objects.get(id=user_id)
        
        if context is None:
            context = {}
            
        context.update({
            'user': user,
            'site_name': 'Napoleon API',
            'base_url': settings.SITE_URL,
        })
        
        subject = render_to_string(subject_template, context).strip()
        message = render_to_string(message_template, context)
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        
        return f"Notification email sent to {user.email}"
        
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending notification email: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * 5)  # Retry after 5 minutes
