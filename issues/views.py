from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomUser,IssueReport
import json
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from django.db.models import Q

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
    if request.user.role != 'resident':
        return redirect('admin_dashboard')
    
    # በ 'is_resolved' ፊልድ ላይ ተመስርቶ በብቃት መቁጠር
    report_stats = IssueReport.objects.filter(user=request.user).aggregate(
        total=Count('id'),
        resolved=Count('id', filter=Q(is_resolved=True)),
        pending=Count('id', filter=Q(is_resolved=False))
    )
    
    # የመጨረሻዋን ሪፖርት ማምጣት
    latest_report = IssueReport.objects.filter(user=request.user).order_by('-created_at').first()
    
    context = {
        'stats': report_stats,
        'latest_report': latest_report,
    }
    
    return render(request, 'resident_dashboard.html', context)
@login_required
def admin_dashboard(request):
    if request.user.role != 'kebele_admin':
        return redirect('resident_dashboard')

    today = timezone.now().date()
    start_of_week = today - timedelta(days=6)  # ላለፉት 7 ቀናት

    # 📊 ሀ) የትንታኔ ካውንተሮች (ከ IssueReport ሞዴልህ ጋር የተጣጣሙ)
    today_reports_count = IssueReport.objects.filter(created_at__date=today).count()
    active_progress_count = IssueReport.objects.filter(is_resolved=False).count() 
    resolved_this_week_count = IssueReport.objects.filter(
        is_resolved=True, 
        created_at__date__gte=today - timedelta(days=7) # እዚህ ጋር updated_at ስለሌለ በcreated_at ተተክቷል
    ).count()
    anonymous_corruption_count = IssueReport.objects.filter(
        is_anonymous=True, 
        issue_type='corruption'
    ).count()

    # 📋 ለ) የቅርብ ጊዜ ሪፖርቶች ሰንጠረዥ (Urgent Incoming Reports)
    urgent_reports = IssueReport.objects.all().order_by('-created_at')[:5]

    # 🍩 ሐ) የቅሬታዎች ስርጭት በመደብ (Doughnut Chart Data)
    # በ issue_type ግሩፕ አድርጎ መቁጠር
    category_data = IssueReport.objects.values('issue_type').annotate(count=Count('id'))
    
    category_labels = [item['issue_type'].upper() for item in category_data]
    category_counts = [item['count'] for item in category_data]

    # 📈 መ) የሪፖርቶች ሳምንታዊ አዝማሚያ (Line Chart Data)
    days_labels = []
    incoming_trends = []
    resolved_trends = []

    for i in range(7):
        current_date = start_of_week + timedelta(days=i)
        days_labels.append(current_date.strftime('%a'))
        
        day_incoming = IssueReport.objects.filter(created_at__date=current_date).count()
        # ማስታወሻ፡ በሞዴልህ ላይ updated_at ስለሌለ፣ ለአዝማሚያው በዚያ ቀን የገቡትንና የተፈቱትን በcreated_at እና በis_resolved እንለያለን
        day_resolved = IssueReport.objects.filter(created_at__date=current_date, is_resolved=True).count()
        
        incoming_trends.append(day_incoming)
        resolved_trends.append(day_resolved)

    context = {
        'today_reports_count': today_reports_count,
        'active_progress_count': active_progress_count,
        'resolved_this_week_count': resolved_this_week_count,
        'anonymous_corruption_count': anonymous_corruption_count,
        'urgent_reports': urgent_reports,
        
        # ለፍሮንት-አንድ ቻርት (Chart.js) እንዲመች ወደ ጄሰን የተቀየሩ
        'category_labels': json.dumps(category_labels),
        'category_counts': json.dumps(category_counts),
        'days_labels': json.dumps(days_labels),
        'incoming_trends': json.dumps(incoming_trends),
        'resolved_trends': json.dumps(resolved_trends),
    }
    
    return render(request, 'admin_dashboard.html', context)
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

@login_required
def manage_reports(request):
    # 🛡️ የደህንነት ጥበቃ፡ የገባው ተጠቃሚ 'kebele_admin' ካልሆነ ወደ ነዋሪው ዳሽቦርድ ይመልሰዋል
    if request.user.role != 'kebele_admin':
        return redirect('resident_dashboard')

    # 📥 አድሚኑ የሪፖርቱን ሁኔታ ሲቀይር (POST Request)
    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        status_update = request.POST.get('status_update')
        
        try:
            # ሪፖርቱን ከዳታቤዝ መፈለግ
            report = IssueReport.objects.get(id=report_id)
            
            # በአድሚኑ ምርጫ መሰረት ሁኔታውን ማሻሻል
            if status_update == 'resolved':
                report.is_resolved = True
            else:
                report.is_resolved = False
                
            report.save()  # በዳታቤዝ ደረጃ ሴቭ ማድረግ
            messages.success(request, f"Ticket #BC-{report.id} status updated successfully!")
            
        except IssueReport.DoesNotExist:
            messages.error(request, "The requested report was not found.")
            
        return redirect('manage_reports')  # ገጹን በነበረበት ማደስ (Refresh)

    # 📋 ገጹ በኖርማል ሲከፈት (GET Request) ሁሉንም ሪፖርቶች አዲስ ከባለ በቅደም ተከተል ማምጣት
    # አዳዲሶቹ ሁልጊዜ ከላይ እንዲመጡ .order_by('-created_at') ተጠቅመናል
    reports = IssueReport.objects.all().order_by('-created_at')
    
    context = {
        'reports': reports
    }
    return render(request, 'manage_reports.html', context)

@login_required
def manage_users(request):
    # Security Lock: Only allow kebele_admin to access this view
    if request.user.role != 'kebele_admin':
        return redirect('resident_dashboard')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        
        try:
            target_user = CustomUser.objects.get(id=user_id)

            # Prevent administrative self-lockouts or self-deletion
            if target_user.id == request.user.id:
                messages.error(request, "You cannot modify or delete your own active administrative account.")
                return redirect('manage_users')

            # Handle Role Update Action
            if action == 'update_role':
                assigned_role = request.POST.get('assigned_role')
                if assigned_role == 'admin':
                    target_user.role = 'kebele_admin'
                elif assigned_role == 'resident':
                    target_user.role = 'resident'
                target_user.save()
                messages.success(request, f"Roles updated successfully for {target_user.username}.")

            # Handle User Deletion Action
            elif action == 'delete_user':
                username = target_user.username
                target_user.delete()
                messages.success(request, f"Account profile for {username} has been permanently deleted.")

        except CustomUser.DoesNotExist:
            messages.error(request, "The requested user profile was not found.")

        return redirect('manage_users')

    # GET Request: Fetch all accounts except system superusers, ordered by ID
    users = CustomUser.objects.all().order_by('-id')
    context = {
        'users': users
    }
    return render(request, 'manage_users.html', context)