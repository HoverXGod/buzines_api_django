from rest_framework.views import APIView
from BaseSecurity.permissions import isSuperUser, isAutorized
from BaseSecurity.services import SecureResponse
from .serializers import *
from .models import *
from User.models import User

class CancelPayment(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = PaymentSerializer

    def get(self, request):

        Payment.objects.get(id=request.GET['payment_id']).cancel_payment()

        try:    
            return SecureResponse(
                request=request,
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)

class CheckStatus(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = PaymentSerializer

    def get(self, request):

        answer = Payment.objects.get(id=request.GET['payment_id']).check__status()

        try:    
            return SecureResponse(
                request=request,
                data=answer,
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)