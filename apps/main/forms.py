from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Contact


class ContactForm(forms.ModelForm):
    """Form for submitting contact messages."""
    
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl transition-all duration-300',
                'style': 'background-color: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-primary);',
                'placeholder': 'Votre nom',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl transition-all duration-300',
                'style': 'background-color: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-primary);',
                'placeholder': 'votre@email.com',
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl transition-all duration-300',
                'style': 'background-color: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-primary);',
                'placeholder': 'Sujet de votre message',
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl transition-all duration-300 resize-none',
                'style': 'background-color: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-primary);',
                'placeholder': 'Votre message...',
                'rows': 5,
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'class' in field.widget.attrs:
                field.widget.attrs['class'] += ' focus:outline-none focus:border-accent-color'


class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form with styled fields."""
    
    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl transition-all duration-300 focus:outline-none',
            'style': 'background-color: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-primary);',
            'placeholder': 'votre@email.com',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl transition-all duration-300 focus:outline-none',
            'style': 'background-color: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-primary);',
            'placeholder': 'Votre mot de passe',
        })
    )


class CustomUserCreationForm(UserCreationForm):
    """Custom signup form with styled fields."""
    
    username = forms.CharField(
        label='Nom d\'utilisateur',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl transition-all duration-300 focus:outline-none',
            'style': 'background-color: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-primary);',
            'placeholder': 'votre_pseudo',
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl transition-all duration-300 focus:outline-none',
            'style': 'background-color: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-primary);',
            'placeholder': 'votre@email.com',
        })
    )
    password1 = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl transition-all duration-300 focus:outline-none',
            'style': 'background-color: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-primary);',
            'placeholder': 'Créez un mot de passe',
        })
    )
    password2 = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl transition-all duration-300 focus:outline-none',
            'style': 'background-color: var(--bg-tertiary); border: 1px solid var(--border-color); color: var(--text-primary);',
            'placeholder': 'Confirmez votre mot de passe',
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove default help texts
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
