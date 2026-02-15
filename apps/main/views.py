from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.http import FileResponse, Http404

import markdown as md

from .models import Project, Skill, About, SocialLink, SiteSettings, PageContent
from .forms import ContactForm, CustomAuthenticationForm, CustomUserCreationForm


def serve_media(request, path):
    """Serve media files in production."""
    import os
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path): 
        return FileResponse(open(file_path, 'rb'))
    raise Http404("File not found")


def get_site_settings():
    """Helper function to get site settings."""
    return SiteSettings.get_instance()


def get_page_content(page, section=None):
    """Helper function to get page content."""
    queryset = PageContent.objects.filter(page=page, is_active=True)
    if section:
        queryset = queryset.filter(section=section)
    return queryset.order_by('order')


def home(request):
    """Home page view."""
    site_settings = get_site_settings()
    projects = Project.objects.filter(is_published=True).order_by('order', '-created_at')[:6]
    skills = Skill.objects.filter(is_active=True).order_by('order', 'category')
    about = About.get_instance()
    social_links = SocialLink.objects.filter(is_active=True).order_by('order')
    
    # Convert bio to markdown if it exists
    about_bio_html = ''
    if about and about.bio:
        about_bio_html = mark_safe(md.markdown(about.bio, extensions=['fenced_code', 'tables']))
    
    context = {
        'site_settings': site_settings,
        'projects': projects,
        'skills': skills,
        'about': about,
        'about_bio_html': about_bio_html,
        'social_links': social_links,
    }
    return render(request, 'pages/home.html', context)


def projects(request):
    """Projects page view."""
    site_settings = get_site_settings()
    projects = Project.objects.filter(is_published=True).order_by('order', '-created_at')
    context = {
        'site_settings': site_settings,
        'projects': projects,
    }
    return render(request, 'pages/projects.html', context)


def project_detail(request, project_id):
    """Project detail view."""
    site_settings = get_site_settings()
    project = get_object_or_404(Project, id=project_id, is_published=True)
    
    context = {
        'site_settings': site_settings,
        'project': project,
    }
    return render(request, 'pages/project_detail.html', context)


def about(request):
    """About page view."""
    site_settings = get_site_settings()
    about = About.get_instance()
    social_links = SocialLink.objects.filter(is_active=True).order_by('order')
    
    # Convert bio to markdown if it exists
    about_bio_html = ''
    if about and about.bio:
        about_bio_html = mark_safe(md.markdown(about.bio, extensions=['fenced_code', 'tables']))
    
    context = {
        'site_settings': site_settings,
        'about': about,
        'about_bio_html': about_bio_html,
        'social_links': social_links,
    }
    return render(request, 'pages/about.html', context)


def contact(request):
    """Contact page view."""
    site_settings = get_site_settings()
    social_links = SocialLink.objects.filter(is_active=True).order_by('order')

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()

            # Send email notifications
            try:
                # 1. Send HTML notification to admin
                admin_context = {
                    'name': contact.name,
                    'email': contact.email,
                    'subject': contact.subject,
                    'message': contact.message,
                    'date': timezone.now().strftime('%d/%m/%Y à %H:%M'),
                }
                admin_html_content = render_to_string('email/contact_notification.html', admin_context)
                
                admin_email = EmailMessage(
                    subject=f"[Portfolio] Nouveau message de {contact.name}",
                    body=admin_html_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.CONTACT_EMAIL],
                )
                admin_email.content_subtype = 'html'
                admin_email.send(fail_silently=False)
                
                # 2. Send HTML confirmation email to user
                user_context = {
                    'name': contact.name,
                    'subject': contact.subject,
                    'date': timezone.now().strftime('%d/%m/%Y à %H:%M'),
                }
                user_html_content = render_to_string('email/contact_confirmation.html', user_context)
                
                confirmation_email = EmailMessage(
                    subject=f"Reçu: {contact.subject}",
                    body=user_html_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[contact.email],
                )
                confirmation_email.content_subtype = 'html'
                confirmation_email.send(fail_silently=False)
                
                messages.success(request, "Votre message a été envoyé avec succès avec confirmation email!", extra_tags='success_contact')
            except Exception:
                messages.error(request, f"Une erreur s'est produite lors de l'envoie d'email. Cependant, nous avons reçu quand même votre message.", extra_tags='error_contact')
            
            return redirect('contact')
    else:
        form = ContactForm()
    
    context = {
        'site_settings': site_settings,
        'form': form,
        'social_links':social_links,
    }
    return render(request, 'pages/contact.html', context)


def handler404(request, exception):
    """Custom 404 error handler."""
    return render(request, 'pages/error/404.html', status=404)


def handler500(request):
    """Custom 500 error handler."""
    return render(request, 'pages/error/500.html', status=500)


def login_view(request):
    """Login page view."""
    if request.user.is_authenticated:
        return redirect('home')
    
    site_settings = get_site_settings()
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenue, {user.username}!")
            
            # Redirect to next page if specified, otherwise home
            next_page = request.GET.get('next', 'home')
            return redirect(next_page)
    else:
        form = CustomAuthenticationForm()
    
    context = {
        'site_settings': site_settings,
        'form': form,
    }
    return render(request, 'account/login.html', context)


def signup_view(request):
    """Signup page view."""
    if request.user.is_authenticated:
        return redirect('home')
    
    site_settings = get_site_settings()
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Compte créé avec succès! Bienvenue, {user.username}!")
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'site_settings': site_settings,
        'form': form,
    }
    return render(request, 'account/signup.html', context)


@login_required
def logout_view(request):
    """Logout view - requires login."""
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('home')
