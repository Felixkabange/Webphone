from django.urls import path, include
from django.conf import settings  
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('call/', views.make_call, name='make_call'),
    path('call-status/', views.call_status, name='call_status'),
    path('call-status/<str:sid>/', views.get_call_status, name='get_call_status'),
    path('hangup/', views.hangup_call, name='hangup_call'),
    path('voice/', views.voice_response, name='voice_response'),
    path('get-twilio-token/', views.get_twilio_token, name='get_twilio_token'),
    # path('logs/', views.CallLogsView.as_view(), name='call_logs'),
    # path('receive-call/', views.receive_call, name='receive_call'),
]