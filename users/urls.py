from django.urls import path
from .views import RegisterView, LogoutView, UpdatePasswordView, CashfreePaymentView, GoogleLoginView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password/update/', UpdatePasswordView.as_view(), name='password_update'),
    path('payment/', CashfreePaymentView.as_view(), name='cashfree_payment'),
    path('login/google/', GoogleLoginView.as_view(), name='google_login'),
]
