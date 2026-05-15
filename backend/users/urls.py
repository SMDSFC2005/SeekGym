from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterView, MeView, ProfilePhotoUploadView, GymRequestListView, GymRequestApproveView, GymRequestRejectView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", TokenObtainPairView.as_view(), name="auth-login"),
    path("refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("me/photo/", ProfilePhotoUploadView.as_view(), name="auth-me-photo"),
    path("gym-requests/", GymRequestListView.as_view(), name="gym-requests-list"),
    path("gym-requests/<int:user_id>/approve/", GymRequestApproveView.as_view(), name="gym-requests-approve"),
    path("gym-requests/<int:user_id>/reject/", GymRequestRejectView.as_view(), name="gym-requests-reject"),
]