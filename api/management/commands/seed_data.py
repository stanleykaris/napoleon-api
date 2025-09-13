from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import random
import os
from pathlib import Path

from api.models import (
    Category, Quest, Challenge, 
    UserQuestProgress, UserChallengeCompletion,
    PartnerOrganization, Partnership
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
        with transaction.atomic():
            # Clear existing data
            self.clear_data()
            
            # Create categories
            categories = self.create_categories()
            
            # Create quests
            quests = self.create_quests(categories)
            
            # Create challenges for each quest
            for quest in quests:
                self.create_challenges(quest)
            
            # Create partner organizations
            partners = self.create_partner_organizations()
            
            # Create partnerships
            self.create_partnerships(quests, partners)
            
            # Create a test user
            user = self.create_test_user()
            
            # Create quest progress for the test user
            self.create_user_progress(user, quests)
            
        self.stdout.write(self.style.SUCCESS('Successfully seeded database'))
    
    def clear_data(self):
        """Clear existing data"""
        self.stdout.write('Clearing existing data...')
        models = [
            UserChallengeCompletion, UserQuestProgress,
            Challenge, Quest, Category,
            Partnership, PartnerOrganization
        ]
        
        for model in models:
            model.objects.all().delete()
        
        # Clear media directory
        media_path = Path('media')
        if media_path.exists():
            for item in media_path.iterdir():
                if item.is_dir():
                    for subitem in item.iterdir():
                        subitem.unlink()
                    item.rmdir()
                else:
                    item.unlink()
    
    def create_categories(self):
        """Create initial categories"""
        self.stdout.write('Creating categories...')
        categories = [
            {'name': 'Nature', 'description': 'Explore and connect with nature'},
            {'name': 'Fitness', 'description': 'Physical activities and exercises'},
            {'name': 'Knowledge', 'description': 'Learn about the environment'},
            {'name': 'Community', 'description': 'Engage with your community'},
            {'name': 'Wildlife', 'description': 'Discover local wildlife'},
        ]
        
        return [Category.objects.create(**cat) for cat in categories]
    
    def create_quests(self, categories):
        """Create initial quests"""
        self.stdout.write('Creating quests...')
        quests_data = [
            {
                'title': 'Urban Explorer',
                'description': 'Discover nature in your city',
                'quest_type': 'outdoor',
                'difficulty': 1,
                'duration_minutes': 120,
                'experience_reward': 100,
                'categories': [categories[0], categories[1]],  # Nature, Fitness
            },
            {
                'title': 'Bird Watcher',
                'description': 'Identify and document local bird species',
                'quest_type': 'outdoor',
                'difficulty': 2,
                'duration_minutes': 180,
                'experience_reward': 200,
                'categories': [categories[0], categories[4]],  # Nature, Wildlife
            },
            {
                'title': 'Eco Warrior',
                'description': 'Complete eco-friendly challenges',
                'quest_type': 'indoor',
                'difficulty': 2,
                'duration_minutes': 240,
                'experience_reward': 250,
                'categories': [categories[2], categories[3]],  # Knowledge, Community
            },
            {
                'title': 'Mountain Trekker',
                'description': 'Conquer local hiking trails',
                'quest_type': 'outdoor',
                'difficulty': 3,
                'duration_minutes': 360,
                'experience_reward': 400,
                'categories': [categories[0], categories[1], categories[4]],  # Nature, Fitness, Wildlife
            },
        ]
        
        quests = []
        for quest_data in quests_data:
            categories = quest_data.pop('categories')
            quest = Quest.objects.create(**quest_data)
            quest.categories.set(categories)
            quests.append(quest)
            
        return quests
    
    def create_challenges(self, quest):
        """Create challenges for a quest"""
        challenges_data = {
            'Urban Explorer': [
                {'title': 'Find a Park', 'description': 'Visit a local park and take a photo', 'order': 1, 'is_required': True, 'experience_reward': 20},
                {'title': 'Tree Identification', 'description': 'Identify and photograph 3 different tree species', 'order': 2, 'is_required': True, 'experience_reward': 30},
                {'title': 'Park Bench Reflection', 'description': 'Spend 10 minutes sitting on a park bench observing nature', 'order': 3, 'is_required': False, 'experience_reward': 20},
                {'title': 'Urban Wildlife', 'description': 'Spot and document 5 different animals or insects', 'order': 4, 'is_required': True, 'experience_reward': 30},
            ],
            'Bird Watcher': [
                {'title': 'Bird Identification', 'description': 'Identify and photograph 5 different bird species', 'order': 1, 'is_required': True, 'experience_reward': 40},
                {'title': 'Bird Call', 'description': 'Record and identify 3 different bird calls', 'order': 2, 'is_required': True, 'experience_reward': 50},
                {'title': 'Nest Spotting', 'description': 'Find and document 2 bird nests (without disturbing them)', 'order': 3, 'is_required': False, 'experience_reward': 30},
                {'title': 'Feeding Time', 'description': 'Set up a bird feeder and document visitors for a week', 'order': 4, 'is_required': True, 'experience_reward': 80},
            ],
            'Eco Warrior': [
                {'title': 'Waste Audit', 'description': 'Document your waste for a week and identify areas to reduce', 'order': 1, 'is_required': True, 'experience_reward': 50},
                {'title': 'Plastic-Free Day', 'description': 'Go a full day without using single-use plastics', 'order': 2, 'is_required': True, 'experience_reward': 40},
                {'title': 'Upcycle Project', 'description': 'Create something useful from items that would have been thrown away', 'order': 3, 'is_required': False, 'experience_reward': 60},
                {'title': 'Community Cleanup', 'description': 'Organize or participate in a local cleanup event', 'order': 4, 'is_required': True, 'experience_reward': 100},
            ],
            'Mountain Trekker': [
                {'title': 'Trail Research', 'description': 'Research and plan a local hiking trail', 'order': 1, 'is_required': True, 'experience_reward': 50},
                {'title': 'Packing List', 'description': 'Create and pack the essential gear for a day hike', 'order': 2, 'is_required': True, 'experience_reward': 30},
                {'title': 'Summit Photo', 'description': 'Reach the summit and take a photo of the view', 'order': 3, 'is_required': True, 'experience_reward': 100},
                {'title': 'Trail Journal', 'description': 'Document your hike with notes and photos', 'order': 4, 'is_required': False, 'experience_reward': 70},
                {'title': 'Leave No Trace', 'description': 'Practice Leave No Trace principles and document how', 'order': 5, 'is_required': True, 'experience_reward': 150},
            ],
        }
        
        for challenge_data in challenges_data.get(quest.title, []):
            Challenge.objects.create(quest=quest, **challenge_data)
    
    def create_partner_organizations(self):
        """Create partner organizations"""
        self.stdout.write('Creating partner organizations...')
        partners = [
            {
                'name': 'Green Earth Initiative',
                'description': 'Dedicated to preserving natural habitats and promoting biodiversity',
                'website': 'https://greenearth.example.com',
                'contact_email': 'info@greenearth.example.com',
                'is_active': True,
            },
            {
                'name': 'Urban Parks Foundation',
                'description': 'Creating and maintaining green spaces in urban environments',
                'website': 'https://urbanparks.example.com',
                'contact_email': 'contact@urbanparks.example.com',
                'is_active': True,
            },
            {
                'name': 'Wildlife Conservation Society',
                'description': 'Protecting wildlife and their habitats around the world',
                'website': 'https://wildlifeconservation.example.com',
                'contact_email': 'support@wildlifeconservation.example.com',
                'is_active': True,
            },
        ]
        
        return [PartnerOrganization.objects.create(**partner) for partner in partners]
    
    def create_partnerships(self, quests, partners):
        """Create partnerships between quests and organizations"""
        self.stdout.write('Creating partnerships...')
        partnerships = [
            {
                'organization': partners[0],
                'quest': quests[1],  # Bird Watcher
                'benefits': 'Free entry to our bird sanctuary and guided tours',
                'is_featured': True,
                'start_date': timezone.now().date(),
                'end_date': timezone.now().date() + timedelta(days=365),
            },
            {
                'organization': partners[1],
                'quest': quests[0],  # Urban Explorer
                'benefits': 'Discount on urban gardening workshops and free park maps',
                'is_featured': True,
                'start_date': timezone.now().date(),
                'end_date': timezone.now().date() + timedelta(days=180),
            },
            {
                'organization': partners[2],
                'quest': quests[3],  # Mountain Trekker
                'benefits': 'Free wildlife guidebook and 20% off conservation tours',
                'is_featured': False,
                'start_date': timezone.now().date(),
                'end_date': None,  # Ongoing
            },
        ]
        
        for data in partnerships:
            Partnership.objects.create(**data)
    
    def create_test_user(self):
        """Create a test user"""
        self.stdout.write('Creating test user...')
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'is_staff': False,
            }
        )
        
        if created or not user.check_password('testpass123'):
            user.set_password('testpass123')
            user.save()
        
        return user
    
    def create_user_progress(self, user, quests):
        """Create quest progress for the test user"""
        self.stdout.write('Creating user progress...')
        
        # Start the first quest
        quest1 = quests[0]
        progress1 = UserQuestProgress.objects.create(
            user=user,
            quest=quest1,
            status='in_progress',
            start_date=timezone.now() - timedelta(days=7),
            progress=50,
        )
        
        # Complete some challenges in the first quest
        challenges1 = quest1.challenges.order_by('order')
        UserChallengeCompletion.objects.create(
            user=user,
            challenge=challenges1[0],
            evidence="Visited Central Park and took photos",
            completed_at=timezone.now() - timedelta(days=6),
        )
        UserChallengeCompletion.objects.create(
            user=user,
            challenge=challenges1[1],
            evidence="Identified oak, maple, and pine trees",
            completed_at=timezone.now() - timedelta(days=5),
        )
        
        # Complete the second quest
        quest2 = quests[1]
        progress2 = UserQuestProgress.objects.create(
            user=user,
            quest=quest2,
            status='completed',
            start_date=timezone.now() - timedelta(days=14),
            completion_date=timezone.now() - timedelta(days=7),
            progress=100,
        )
        
        # Complete all challenges in the second quest
        for challenge in quest2.challenges.all():
            UserChallengeCompletion.objects.create(
                user=user,
                challenge=challenge,
                evidence=f"Completed {challenge.title}",
                completed_at=timezone.now() - timedelta(days=random.randint(7, 14)),
            )
        
        # Leave the third quest not started
        
        # Start but abandon the fourth quest
        quest4 = quests[3]
        progress4 = UserQuestProgress.objects.create(
            user=user,
            quest=quest4,
            status='abandoned',
            start_date=timezone.now() - timedelta(days=10),
            progress=25,
        )
        
        # Complete one challenge in the abandoned quest
        challenge = quest4.challenges.first()
        UserChallengeCompletion.objects.create(
            user=user,
            challenge=challenge,
            evidence="Researched Mount Rainier trail",
            completed_at=timezone.now() - timedelta(days=9),
        )
