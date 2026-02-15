from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # User chat routes
    path('', views.chat_view, name='home'),
    
    # Admin routes
    path('admin/', views.admin_inbox, name='admin_inbox'),
    path('admin/conversation/<int:conversation_id>/', views.admin_conversation, name='admin_conversation'),
    path('admin/conversations/', views.admin_conversation_list, name='admin_conversation_list'),
]