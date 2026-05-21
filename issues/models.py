from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('resident', 'Resident'),
        ('kebele_admin', 'Kebele Admin'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='resident')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    fan = models.CharField(max_length=50, unique=True, blank=True, null=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class IssueReport(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='issues')
    issue_type = models.CharField(max_length=50)
    is_anonymous = models.BooleanField(default=False)
    reporter_name = models.CharField(max_length=150, null=True, blank=True)
    reporter_phone = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField()
    evidence_image = models.ImageField(upload_to='issue_evidences/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        if self.is_anonymous:
            return f"[{self.issue_type.upper()}] Anonymous Report - {self.created_at.strftime('%Y-%m-%d')}"
        return f"[{self.issue_type.upper()}] By {self.reporter_name or self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"