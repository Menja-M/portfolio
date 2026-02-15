from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser

import uuid


class SiteSettings(models.Model):
    """Model for global site settings."""
    site_name = models.CharField(_("Site Name"), max_length=100, default="MMR Portfolio")
    site_description = models.TextField(_("Site Description"), blank=True)
    logo_text = models.CharField(_("Logo Text"), max_length=100, default="MMR")
    
    # Hero Section
    hero_title = models.CharField(_("Hero Title"), max_length=200, default="Bonjour, je suis MMR")
    hero_subtitle = models.TextField(_("Hero Subtitle"), default="Je conçois et développe des expériences numériques modernes, performantes et accessibles.")
    hero_cta_text = models.CharField(_("Hero CTA Text"), max_length=100, default="Voir mes projets")
    hero_cta_url = models.CharField(_("Hero CTA URL"), max_length=200, default="/projects/")
    hero_secondary_cta_text = models.CharField(_("Hero Secondary CTA Text"), max_length=100, default="Me contacter")
    hero_secondary_cta_url = models.CharField(_("Hero Secondary CTA URL"), max_length=200, default="/contact/")
    
    # Stats
    stats_years = models.CharField(_("Years Experience"), max_length=50, default="5+")
    stats_projects = models.CharField(_("Projects Count"), max_length=50, default="50+")
    stats_clients = models.CharField(_("Clients Count"), max_length=50, default="30+")
    stats_passion = models.CharField(_("Passion Text"), max_length=50, default="100%")
    
    # CTA Section
    cta_title = models.CharField(_("CTA Title"), max_length=200, default="Prêt à démarrer votre projet ?")
    cta_subtitle = models.TextField(_("CTA Subtitle"), default="Discutons de votre projet et transformons vos idées en réalité numérique.")
    cta_button_text = models.CharField(_("CTA Button Text"), max_length=100, default="Me contacter")
    cta_button_url = models.CharField(_("CTA Button URL"), max_length=200, default="/contact/")
    
    # Footer
    footer_text = models.TextField(_("Footer Text"), blank=True)
    footer_copyright = models.CharField(_("Copyright"), max_length=200, default="© 2024 MMR Portfolio. Tous droits réservés.")
    
    # Contact Info (overrides About model for display)
    contact_email = models.EmailField(_("Contact Email"), blank=True)
    contact_location = models.CharField(_("Location"), max_length=100, default="Paris, France")
    
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    
    class Meta:
        verbose_name = _("Site Settings")
        verbose_name_plural = _("Site Settings")
    
    def __str__(self):
        return self.site_name
    
    @classmethod
    def get_instance(cls):
        """Get the singleton SiteSettings instance."""
        instance = cls.objects.first()
        if not instance:
            instance = cls.objects.create()
        return instance


class PageContent(models.Model):
    """Model for customizable page content sections."""
    PAGE_CHOICES = [
        ('home', _('Home')),
        ('about', _('About')),
        ('projects', _('Projects')),
        ('contact', _('Contact')),
    ]
    
    SECTION_CHOICES = [
        ('hero', _('Hero')),
        ('stats', _('Stats')),
        ('skills', _('Skills')),
        ('featured_projects', _('Featured Projects')),
        ('cta', _('CTA')),
        ('bio', _('Biography')),
        ('services', _('Services')),
        ('timeline', _('Timeline')),
        ('header', _('Header')),
        ('footer', _('Footer')),
        ('custom', _('Custom')),
    ]
    
    page = models.CharField(_("Page"), max_length=50, choices=PAGE_CHOICES)
    section = models.CharField(_("Section"), max_length=50, choices=SECTION_CHOICES)
    title = models.CharField(_("Title"), max_length=200, blank=True)
    subtitle = models.TextField(_("Subtitle"), blank=True)
    content = models.TextField(_("Content"), blank=True, help_text=_("Use Markdown for formatting"))
    content_html = models.TextField(_("Content HTML"), blank=True, help_text=_("Raw HTML content"))
    
    # Media
    image = models.ImageField(_("Image"), upload_to='page_content/', blank=True, null=True)
    icon = models.CharField(_("Icon"), max_length=100, blank=True, help_text=_("SVG icon name"))
    
    # Links
    button_text = models.CharField(_("Button Text"), max_length=100, blank=True)
    button_url = models.CharField(_("Button URL"), max_length=200, blank=True)
    
    # Styling
    order = models.PositiveIntegerField(_("Order"), default=0)
    is_active = models.BooleanField(_("Is Active"), default=True)
    
    class Meta:
        ordering = ['page', 'section', 'order']
        verbose_name = _("Page Content")
        verbose_name_plural = _("Page Contents")
    
    def __str__(self):
        return f"{self.get_page_display()} - {self.get_section_display()}"


class Project(models.Model):
    """Model representing a portfolio project."""
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(_("Title"), max_length=200)
    short_description = models.TextField(_("Short Description"), blank=True)
    description = models.TextField(_("Description"))
    image = models.ImageField(_("Image"), upload_to='projects/', blank=True, null=True)
    link = models.URLField(_("Project Link"), blank=True, null=True)
    github_link = models.URLField(_("GitHub Link"), blank=True, null=True)
    technologies = models.CharField(_("Technologies"), max_length=500, help_text=_("Comma-separated list of technologies"))
    
    # Flags
    is_published = models.BooleanField(_("Is Published"), default=True)
    featured = models.BooleanField(_("Featured"), default=False)
    
    # Ordering
    order = models.PositiveIntegerField(_("Order"), default=0)
    
    # Timestamps
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")

    def __str__(self):
        return self.title

    def get_technologies_list(self):
        """Return technologies as a list."""
        return [tech.strip() for tech in self.technologies.split(',') if tech.strip()]


class Skill(models.Model):
    """Model representing a skill."""
    name = models.CharField(_("Skill Name"), max_length=100)
    category = models.CharField(
        _("Category"),
        max_length=50,
        choices=[
            ('frontend', _('Frontend')),
            ('backend', _('Backend')),
            ('database', _('Database')),
            ('devops', _('DevOps')),
            ('tools', _('Tools & Others')),
        ]
    )
    icon = models.CharField(_("Icon Class"), max_length=100, blank=True, help_text=_("Font Awesome icon class"))
    proficiency = models.PositiveIntegerField(_("Proficiency"), default=50, help_text=_("0-100"))
    is_active = models.BooleanField(_("Is Active"), default=True)
    order = models.PositiveIntegerField(_("Order"), default=0)

    class Meta:
        ordering = ['order', 'category', 'name']
        verbose_name = _("Skill")
        verbose_name_plural = _("Skills")

    def __str__(self):
        return self.name


class About(models.Model):
    """Model representing about information."""
    title = models.CharField(_("Title"), max_length=200, default=_("About Me"))
    bio = models.TextField(_("Biography"))
    photo = models.ImageField(_("Photo"), upload_to='about/', blank=True, null=True)
    resume = models.FileField(_("Resume/CV"), upload_to='resumes/', blank=True, null=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("About")
        verbose_name_plural = _("About")

    def __str__(self):
        return self.title

    @classmethod
    def get_instance(cls):
        """Get the singleton About instance."""
        instance = cls.objects.first()
        if not instance:
            instance = cls.objects.create(
                title=cls._meta.get_field('title').get_default(),
                bio=""
            )
        return instance


class Contact(models.Model):
    """Model representing a contact message."""
    name = models.CharField(_("Name"), max_length=200)
    email = models.EmailField(_("Email"))
    subject = models.CharField(_("Subject"), max_length=300)
    message = models.TextField(_("Message"))
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    is_read = models.BooleanField(_("Is Read"), default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("Contact Message")
        verbose_name_plural = _("Contact Messages")

    def __str__(self):
        return f"{self.name} - {self.subject}"


class SocialLink(models.Model):
    """Model representing social media links."""
    name = models.CharField(_("Name"), max_length=100)
    url = models.URLField(_("URL"))
    icon = models.TextField(_("Icon Class"), help_text=_("Code svg (taille 24)"))
    is_active = models.BooleanField(_("Is Active"), default=True)
    order = models.PositiveIntegerField(_("Order"), default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = _("Social Link")
        verbose_name_plural = _("Social Links")

    def __str__(self):
        return self.name
