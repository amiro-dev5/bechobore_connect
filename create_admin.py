import os
import django

# የጃንጎን ሲስተም ማስጀመር
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bechobore_connect.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# አንተ የፈለግከው የአድሚን መረጃ
USERNAME = 'admin'
PASSWORD = 'admin123'
EMAIL = 'admin@example.com'

if not User.objects.filter(username=USERNAME).exists():
    User.objects.create_superuser(username=USERNAME, email=EMAIL, password=PASSWORD)
    print("=========================================")
    print(f"የአድሚን አካውንት በተሳካ ሁኔታ ተፈጥሯል!")
    print(f"Username: {USERNAME} | Password: {PASSWORD}")
    print("=========================================")
else:
    print("አድሚኑ አስቀድሞ ስለተፈጠረ በድጋሚ አልተፈጠረም።")