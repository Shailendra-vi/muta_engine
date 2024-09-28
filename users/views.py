from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, UpdatePasswordSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
import time
import requests
from social_django.utils import psa
from .utils import generate_invoice_pdf, send_invoice_email


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    @psa('social:complete')
    def post(self, request):
        """
        This view handles Google OAuth2 sign-in/sign-up and issues JWT tokens.
        """
        token = request.data.get('token', None)
        if token is None:
            return Response({"error": "Token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = request.backend.do_auth(token)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if user:
            if user.is_active:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            else:
                return Response({"error": "User account is disabled."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Authentication failed."}, status=status.HTTP_400_BAD_REQUEST)


class CashfreePaymentView(APIView):
    """
    View to handle Cashfree UPI payments, simulating PhonePe.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            amount = request.data.get('amount')
            upi_id = request.data.get('upi_id')
            if not amount:
                return Response({"error": "Amount is required."}, status=status.HTTP_400_BAD_REQUEST)
            if not upi_id:
                return Response({"error": "UPI ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            user = request.user
            
            order_id = 'order_' + str(int(time.time()))
            payload = {
                "order_id": order_id,
                "order_amount": amount,
                "order_currency": "INR",
                "customer_details": {
                    "customer_id": str(user.id),
                    "customer_email": user.email,
                    "customer_phone": "1234567890"
                },
                "payment_method": {
                    "upi": {
                        "channel": "phonepe",
                        "upi_id": upi_id # From request
                    }
                }
            }

            headers = {
                "Content-Type": "application/json",
                "x-client-id": settings.CASHFREE_APP_ID,
                "x-client-secret": settings.CASHFREE_SECRET_KEY,
                "x-api-version": "2023-08-01"
            }

            response = requests.post(
                "https://sandbox.cashfree.com/pg/orders",
                json=payload,
                headers=headers
            )

            if response.status_code == 200:
                transaction_details = response.json()
                
                pdf_path = generate_invoice_pdf(user, transaction_details)
                
                if pdf_path:
                    send_invoice_email(user, pdf_path)

                return Response(transaction_details, status=status.HTTP_200_OK)
            else:
                return Response({"error": response.text}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdatePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UpdatePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


