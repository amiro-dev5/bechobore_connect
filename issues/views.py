from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomUser,IssueReport

def home(request):
    # ተጠቃሚው ቀድሞ Log In ካደረገ በቀጥታ ወደ ሚናው ዳሽቦርድ ይመራዋል
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    return render(request, 'home.html')

def auth_page(request):
    # ተጠቃሚው ቀድሞውኑ ገብቶ ከሆነ ወደ ዳሽቦርዱ ያሻግረዋል
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        action = request.POST.get('action')

        # 🔐 ሀ. የመግቢያ ሂደት (SIGN IN LOGIC)
        if action == 'login':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('dashboard_redirect')
            else:
                messages.error(request, "Invalid username or password.")

        # 📝 ለ. የምዝገባ ሂደት (SIGN UP LOGIC)
        elif action == 'register':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')

            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, "Username already exists.")
            else:
                # 🛡️ ፓስወርዱን በከፍተኛ ደረጃ ሀሽ (Hashed) አድርጎ ዳታቤዝ ውስጥ በሰላም ያስቀምጠዋል
                user = CustomUser.objects.create_user(username=username, email=email, password=password)
                
                # 🔒 ሴኪውሪቲ፡ የፍሮንት-አንድ ምርጫን ትተን በራሳችን ነባሪ ሚናውን 'resident' አደረግነው
                user.role = 'resident'
                user.save()
                
                # ✨ ከተመዘገበ በኋላ በቀጥታ ከማስገባት ይልቅ መልዕክት አሳይተን ወደ Sign In እንመራዋለን
                messages.success(request, "Account created successfully! Please sign in with your credentials.")
                return redirect('/auth/?mode=login')

    return render(request, 'auth_page.html')

def sign_out(request):
    # የተጠቃሚውን ሴሽን (Session) ያጠፋና ወደ ሆም ፔጅ ይመልሰዋል
    logout(request)
    return redirect('home')

@login_required
def dashboard_redirect(request):
    # የተጠቃሚውን ሚና (Role) አይቶ አቅጣጫ የሚያስይዝ ዋናው ማዕከል
    if request.user.role == 'kebele_admin':
        return redirect('admin_dashboard')
    else:
        return redirect('resident_dashboard')

@login_required
def resident_dashboard(request):
    # ነዋሪ ካልሆነ ወደ አድሚን ዳሽቦርድ ይመልሰዋል (ደህንነትን ለመጠበቅ)
    if request.user.role != 'resident':
        return redirect('admin_dashboard')
    return render(request, 'resident_dashboard.html')

@login_required
def admin_dashboard(request):
    # አድሚን ካልሆነ ወደ ነዋሪ ዳሽቦርድ ይመልሰዋል
    if request.user.role != 'kebele_admin':
        return redirect('resident_dashboard')
    return render(request, 'admin_dashboard.html')
@login_required
def report_issue(request):
    if request.user.role != 'resident':
        return redirect('admin_dashboard')
        
    if request.method == 'POST':
        issue_type = request.POST.get('issue_type')
        description = request.POST.get('description')
        
        # Guard Clause: Only allow anonymity check if the category is strictly 'corruption'
        if issue_type == 'corruption':
            is_anonymous_raw = request.POST.get('is_anonymous')
            is_anonymous = True if is_anonymous_raw == 'yes' else False
        else:
            # All other categories (waste, utility, crime) default to standard public reporting
            is_anonymous = False
        
        # Enforce empty identity details if the report is flagged as anonymous
        reporter_name = request.POST.get('full_name') if not is_anonymous else None
        reporter_phone = request.POST.get('phone') if not is_anonymous else None
        
        evidence_image = request.FILES.get('evidence_image')
        
        # 🛡️ TRUE ANONYMITY SECURITY LOCK: 
        # ሪፖርቱ አኖኒመስ ከሆነ የ 'user' ግንኙነትን 'None' በማድረግ ከገቡበት አካውንት ጋር ያለውን ትራክ በዳታቤዝ ደረጃ እንበጥሰዋለን።
        issue = IssueReport.objects.create(
            user=request.user if not is_anonymous else None,
            issue_type=issue_type,
            is_anonymous=is_anonymous,
            reporter_name=reporter_name,
            reporter_phone=reporter_phone,
            description=description,
            evidence_image=evidence_image
        )
        
        # Conditional message routing based on the evaluated anonymity state
        if is_anonymous:
            success_msg = (
                "🚨 Ticket ID: <b>#BC-{id}</b><br>"
                "🎯 <b>Submitted Anonymously!</b><br>"
                "Your identity, name, and phone number are fully protected and confidential. Thank you for your cooperation."
            ).format(id=issue.id)
        else:
            success_msg = (
                "✅ <b>Report Submitted Successfully!</b><br>"
                "Ticket ID: <b>#BC-{id}</b><br>"
                "We have received your report and our team will review the details promptly."
            ).format(id=issue.id)
            
        messages.success(request, success_msg)
        return redirect('resident_dashboard')
        
    return render(request, 'report_issue.html')

@login_required
def my_reports(request):
    if request.user.role != 'resident':
        return redirect('admin_dashboard')
        
    # 🔍 እዚህ ጋር ከገቡበት አካውንት ጋር የተያያዙ መደበኛ ሪፖርቶችን ብቻ ያመጣል
    user_reports = IssueReport.objects.filter(user=request.user).order_by('-id')
    
    return render(request, 'my_reports.html', {'reports': user_reports})