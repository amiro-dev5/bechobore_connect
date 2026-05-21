from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model  
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User  # 👈 በCustomUser ፋንታ በUser ተካው
        fields = UserCreationForm.Meta.fields + ('email', 'role',)

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User  
        fields = '__all__'

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User  
    
   
    list_display = ['username', 'email', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_active']
    
  
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role', 'email'),
        }),
    )
    
   
    fieldsets = UserAdmin.fieldsets + (
        ('User Role Assignment', {'fields': ('role',)}),
    )


from .models import IssueReport
admin.site.register(User, CustomUserAdmin)
admin.site.register(IssueReport)