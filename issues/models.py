from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # የDrop-down ምርጫዎች መለያ
    ROLE_CHOICES = [
        ('resident', 'Resident'),
        ('kebele_admin', 'Kebele Admin'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='resident')

    def __str__(self):
        return self.username



# -------------------------------------------------------------------
# 🔒 አዲሱ የደህንነቱ የተጠበቀ የሪፖርት ማቅረቢያ ሞዴል (እዚህ ላይ ቀጥል)
# -------------------------------------------------------------------

class IssueReport(models.Model):
    # ሪፖርት አድራጊው ማንነቱ እንዲታወቅ ከፈለገ ብቻ ካንተ CustomUser ጋር ይያያዛል፤ ካልሆነ ባዶ (Null) ይሆናል
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='issues')
    
    # የቅሬታው አይነት (waste, utility, crime, corruption)
    issue_type = models.CharField(max_length=50)
    
    # ተጠቃሚው ማንነቱ እንዳይታይ የመረጠው ምርጫ (True/False)
    is_anonymous = models.BooleanField(default=False)
    
    # ማንነቱ እንዲታወቅ ከፈለገ የሚሞላቸው (Anonymous ከሆነ በቪው ሎጂካችን ባዶ እናደርጋቸዋለን)
    reporter_name = models.CharField(max_length=150, null=True, blank=True)
    reporter_phone = models.CharField(max_length=20, null=True, blank=True)
    
    # የቅሬታው ዝርዝር መግለጫ
    description = models.TextField()
    
    # ማስረጃ ፎቶ (አማራጭ)
    evidence_image = models.ImageField(upload_to='issue_evidences/', null=True, blank=True)
    
    # ሲስተሙ በራሱ የሚመዘግባቸው መረጃዎች
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False) # ችግሩ መፍትሄ ማግኘቱን መከታተያ

    def __str__(self):
        if self.is_anonymous:
            return f"[{self.issue_type.upper()}] Anonymous Report - {self.created_at.strftime('%Y-%m-%d')}"
        return f"[{self.issue_type.upper()}] By {self.reporter_name or self.user.username} - {self.created_at.strftime('%Y-%m-%d')}"