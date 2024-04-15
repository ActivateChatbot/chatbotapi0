from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import UserDetailAPI,RegisterUserAPIView, LoginView, UserMessageView, send_message

urlpatterns = [
  path("get-details",UserDetailAPI.as_view()),
  path('register',RegisterUserAPIView.as_view()),
  #path('login', LoginView.as_view()),
  path('message', UserMessageView.as_view()),
  path('send-message', send_message),
  path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
]