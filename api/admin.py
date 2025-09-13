from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    User, Category, Quest, Challenge, 
    UserQuestProgress, UserChallengeCompletion,
    PartnerOrganization, Partnership
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom admin for the User model"""
    model = User
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'experience_points', 'level')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_subscribed')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'profile_picture', 'bio')}),
        (_('Progress'), {'fields': ('experience_points', 'level')}),
        (_('Preferences'), {'fields': ('is_subscribed', 'notification_preferences')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

class ChallengeInline(admin.TabularInline):
    """Inline admin for challenges in Quest admin"""
    model = Challenge
    extra = 1
    ordering = ('order',)

@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    """Admin for Quest model"""
    list_display = ('title', 'quest_type', 'difficulty', 'duration_minutes', 'experience_reward', 'is_active')
    list_filter = ('quest_type', 'difficulty', 'is_active')
    search_fields = ('title', 'description')
    filter_horizontal = ('categories',)
    inlines = [ChallengeInline]
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for Category model"""
    list_display = ('name', 'description')
    search_fields = ('name',)

class UserChallengeCompletionInline(admin.TabularInline):
    """Inline admin for challenge completions in UserQuestProgress admin"""
    model = UserChallengeCompletion
    extra = 0
    readonly_fields = ('challenge', 'completed_at')
    can_delete = False

@admin.register(UserQuestProgress)
class UserQuestProgressAdmin(admin.ModelAdmin):
    """Admin for UserQuestProgress model"""
    list_display = ('user', 'quest', 'status', 'progress', 'start_date', 'completion_date')
    list_filter = ('status', 'quest')
    search_fields = ('user__username', 'quest__title')
    inlines = [UserChallengeCompletionInline]
    readonly_fields = ('progress',)

@admin.register(PartnerOrganization)
class PartnerOrganizationAdmin(admin.ModelAdmin):
    """Admin for PartnerOrganization model"""
    list_display = ('name', 'contact_email', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description', 'contact_email')
    readonly_fields = ('created_at',)

@admin.register(Partnership)
class PartnershipAdmin(admin.ModelAdmin):
    """Admin for Partnership model"""
    list_display = ('organization', 'quest', 'is_featured', 'start_date', 'end_date')
    list_filter = ('is_featured', 'start_date', 'end_date')
    search_fields = ('organization__name', 'quest__title')
    date_hierarchy = 'start_date'
