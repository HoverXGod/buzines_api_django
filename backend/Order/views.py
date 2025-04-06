from rest_framework.views import APIView
from BaseSecurity.permissions import isSuperUser, isAutorized
from BaseSecurity.services import SecureResponse
from .serializers import *
from .models import *
from User.models import User

class GetAllOrders(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = OrderSerializer

    def get(self, request):

        try:    
            return SecureResponse(
                request=request,
                data=self.serializer_class(
                    instance=Order.objects.all(),
                    many=True
                    ).data,
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)

class GetUserOrders(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = OrderSerializer

    def get(self, request):

        try:    
            return SecureResponse(
                request=request,
                data=self.serializer_class(
                    instance=Order.objects.all(user=User.objects.get(request.GET['user_id'])),
                    many=True
                    ).data,
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)
        
class GetMyOrders(APIView): 
    
    permission_classes = [isAutorized]
    serializer_class = OrderSerializer

    def get(self, request):

        try:    
            return SecureResponse(
                request=request,
                data=self.serializer_class(
                    instance=Order.objects.all(user=request.user),
                    many=True
                    ).data,
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)
        
class StartOrder(APIView): 
    
    permission_classes = [isAutorized]
    serializer_class = OrderSerializer

    def get(self, request):

        try:    
            return SecureResponse(
                request=request,
                data=self.serializer_class(
                    instance=Order.create__order(
                        request=request,
                        promo=request.GET['promocode'],
                        method_name=request.GET['method_name'],
                        ),
                    ).data,
                status=200
                )
        except: 
            try:    
                return SecureResponse(
                    request=request,
                    data=self.serializer_class(
                        instance=Order.create__order(
                            request=request,
                            promo="",
                            method_name=request.GET['method_name'],
                            ),
                        ).data,
                    status=200
                    )
            except:
                return SecureResponse(request=request, status=400)
            
class GetOrder(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = OrderSerializer

    def get(self, request):

        try:    
            return SecureResponse(
                request=request,
                data=self.serializer_class(
                    instance=Order.objects.get(id=request.GET['order_id']),
                    ).data,
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)
            
