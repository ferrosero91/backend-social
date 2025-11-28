from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Company, Candidate, JobPosting, Interview, Question, Answer


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active', 'created_at')
    list_filter = ('role', 'is_staff', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone')}),
    )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Admin interface for Company model."""
    list_display = ('company_name', 'user', 'industry', 'size', 'created_at')
    list_filter = ('industry', 'size', 'created_at')
    search_fields = ('company_name', 'user__username', 'user__email')
    ordering = ('-created_at',)
    raw_id_fields = ('user',)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    """Admin interface for Candidate model."""
    list_display = ('full_name', 'user', 'experience_years', 'created_at')
    list_filter = ('experience_years', 'created_at')
    search_fields = ('full_name', 'user__username', 'user__email', 'skills')
    ordering = ('-created_at',)
    raw_id_fields = ('user',)


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    """Admin interface for JobPosting model."""
    list_display = ('title', 'company', 'status', 'experience_required', 'created_at')
    list_filter = ('status', 'created_at', 'experience_required')
    search_fields = ('title', 'description', 'company__company_name')
    ordering = ('-created_at',)
    raw_id_fields = ('company',)
    
    actions = ['make_active', 'make_closed']
    
    def make_active(self, request, queryset):
        queryset.update(status='active')
    make_active.short_description = "Mark selected jobs as active"
    
    def make_closed(self, request, queryset):
        queryset.update(status='closed')
    make_closed.short_description = "Mark selected jobs as closed"


class QuestionInline(admin.TabularInline):
    """Inline admin for Questions within Interview."""
    model = Question
    extra = 0
    fields = ('question_text', 'difficulty', 'skill_evaluated', 'order')


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    """Admin interface for Interview model."""
    list_display = ('id', 'candidate', 'job_posting', 'status', 'skill_match_score', 
                    'final_score', 'created_at')
    list_filter = ('status', 'channel', 'created_at')
    search_fields = ('candidate__full_name', 'job_posting__title')
    ordering = ('-created_at',)
    raw_id_fields = ('job_posting', 'candidate')
    readonly_fields = ('skill_match_score', 'final_score', 'agent_recommendation', 
                       'started_at', 'completed_at')
    
    inlines = [QuestionInline]
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('job_posting', 'candidate', 'status', 'channel')
        }),
        ('Scores', {
            'fields': ('skill_match_score', 'final_score')
        }),
        ('Agent Analysis', {
            'fields': ('agent_recommendation',)
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin interface for Question model."""
    list_display = ('id', 'interview', 'skill_evaluated', 'difficulty', 'order')
    list_filter = ('difficulty', 'created_at')
    search_fields = ('question_text', 'skill_evaluated')
    ordering = ('interview', 'order')
    raw_id_fields = ('interview',)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Admin interface for Answer model."""
    list_display = ('id', 'question', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('answer_text', 'evaluation_notes')
    ordering = ('-created_at',)
    raw_id_fields = ('question',)
