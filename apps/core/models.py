from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    """Custom User model with role-based access."""
    ROLE_CHOICES = [
        ('company', 'Company'),
        ('candidate', 'Candidate'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='candidate')
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.role})"


class Company(models.Model):
    """Company profile linked to a User with 'company' role."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=255)
    industry = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'companies'
        verbose_name_plural = 'Companies'
        ordering = ['-created_at']

    def __str__(self):
        return self.company_name


class Candidate(models.Model):
    """Candidate profile linked to a User with 'candidate' role."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    full_name = models.CharField(max_length=255)
    cv_file = models.FileField(upload_to='cvs/', blank=True, null=True)
    cv_parsed_data = models.JSONField(default=dict, blank=True)
    skills = models.JSONField(default=list, blank=True)
    experience_years = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    education = models.TextField(blank=True)
    linkedin_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'candidates'
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name


class JobPosting(models.Model):
    """Job postings created by companies."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='job_postings')
    title = models.CharField(max_length=255)
    description = models.TextField()
    required_skills = models.JSONField(default=list)
    experience_required = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    location = models.CharField(max_length=255, blank=True)
    salary_range = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job_postings'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.company.company_name}"


class Interview(models.Model):
    """Interview sessions between candidates and the intelligent agent."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='interviews')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='interviews')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    channel = models.CharField(max_length=20, default='web')  # web, whatsapp, telegram
    skill_match_score = models.FloatField(
        default=0.0, 
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    final_score = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    questions_data = models.JSONField(default=list, blank=True)
    answers_data = models.JSONField(default=list, blank=True)
    agent_recommendation = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'interviews'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'job_posting']),
            models.Index(fields=['candidate', 'status']),
        ]

    def __str__(self):
        return f"Interview: {self.candidate.full_name} - {self.job_posting.title}"


class Question(models.Model):
    """Dynamic questions generated by the agent during interviews."""
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    skill_evaluated = models.CharField(max_length=100)
    expected_answer_keywords = models.JSONField(default=list, blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'questions'
        ordering = ['interview', 'order']

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."


class Answer(models.Model):
    """Candidate answers to interview questions."""
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='answer')
    answer_text = models.TextField()
    score = models.FloatField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)]
    )
    evaluation_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'answers'

    def __str__(self):
        return f"Answer to Q{self.question.order}"
