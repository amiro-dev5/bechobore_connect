from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model  # 👈 ይህንን ተጠቀም
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

# 🔒 get_user_model() አሁን ያለውን ንቁ የCustomUser ሞዴል በደህንነት ይጠራዋል
User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User  # 👈 በCustomUser ፋንታ በUser ተካው
        fields = UserCreationForm.Meta.fields + ('email', 'role',)

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User  # 👈 እዚህም ላይ በUser ተካው
        fields = '__all__'

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User  # 👈 እዚህም ላይ
    
    # 1. በዝርዝር ገጹ ላይ የሮል አምድ ማሳያ
    list_display = ['username', 'email', 'role', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_active']
    
    # 2. አዲስ ተጠቃሚ ሲፈጠር (Add User) የጅንጎን ሜዳዎች ወርሰን የኛን ሮል እንጨምራለን
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role', 'email'),
        }),
    )
    
    # 3. ያለውን ተጠቃሚ ስናስተካክል (Edit User) ሮሉን ለመቀየር
    fieldsets = UserAdmin.fieldsets + (
        ('User Role Assignment', {'fields': ('role',)}),
    )

# 🚀 አዲሱን የIssueReport ሞዴልም እዚሁ አድሚን ላይ እንዲታይ እንመዝግበው
from .models import IssueReport
admin.site.register(User, CustomUserAdmin)
admin.site.register(IssueReport)