from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Project, Skill, About, Contact, SocialLink, SiteSettings, PageContent


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'updated_at')
    fieldsets = (
        (_('General'), {'fields': ('site_name', 'site_description', 'logo_text')}),
        (_('Hero Section'), {'fields': ('hero_title', 'hero_subtitle', 'hero_cta_text', 'hero_cta_url', 'hero_secondary_cta_text', 'hero_secondary_cta_url')}),
        (_('Stats'), {'fields': ('stats_years', 'stats_projects', 'stats_clients', 'stats_passion')}),
        (_('CTA Section'), {'fields': ('cta_title', 'cta_subtitle', 'cta_button_text', 'cta_button_url')}),
        (_('Contact Info'), {'fields': ('contact_email', 'contact_location')}),
        (_('Footer'), {'fields': ('footer_text', 'footer_copyright')}),
    )


@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ('page', 'section', 'title', 'is_active', 'order')
    list_filter = ('page', 'section', 'is_active')
    search_fields = ('title', 'content')
    ordering = ('page', 'section', 'order')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_published', 'order', 'featured')
    list_filter = ('is_published', 'featured', 'created_at')
    search_fields = ('title', 'description', 'technologies')
    ordering = ('order', '-created_at')
    
    fieldsets = (
        (_('General'), {'fields': ('title', 'short_description', 'description', 'image', 'technologies')}),
        (_('Links'), {'fields': ('link', 'github_link')}),
        (_('Settings'), {'fields': ('is_published', 'featured', 'order')}),
    )


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'proficiency', 'is_active', 'order')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)
    ordering = ('order', 'category', 'name')


class AboutAdmin(admin.ModelAdmin):
    list_display = ('title', 'updated_at')
    ordering = ('-updated_at',)


admin.site.register(About, AboutAdmin)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('order', 'name')
