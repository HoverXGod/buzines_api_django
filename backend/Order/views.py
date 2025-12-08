from rest_framework.views import APIView
from BaseSecurity.permissions import isSuperUser, isAutorized
from BaseSecurity.services import SecureResponse
from .serializers import *
from .models import *
from User.models import User
from core.cache import cache_api_view
from django.utils.decorators import method_decorator
from BaseSecurity.models import ExceptionManager
from .tasks import create_order_task

class GetAllOrders(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = OrderSerializer

    @method_decorator(cache_api_view(use_models=[Order]))
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

    @method_decorator(cache_api_view(use_models=[Order]))
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

    @method_decorator(cache_api_view(use_models=[Order]))
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
            task = create_order_task.delay(
                user_id=request.user.id,
                promo="",
                method_name=request.GET['method_name'],
                db_name=request.tenant_db
            )
            if task.ready():
                task_data = task.result
            else:
                task_data = None

            return SecureResponse(
                request=request,
                data=self.serializer_class(task_data).data,
                status=200
                )
        except:
            try:
                task = create_order_task.delay(
                            user_id=request.user.id,
                            promo="",
                            method_name=request.GET['method_name'],
                            db_name=request.tenant_db
                            )
                if task.ready():
                   task_data = task.result
                else:
                    task_data = None

                return SecureResponse(
                    request=request,
                    data=self.serializer_class(task_data).data,
                    status=200
                    )
            except Exception as e:
                ExceptionManager.register_exception(e)
                return SecureResponse(request=request, status=400)
            
class GetOrder(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = OrderSerializer

    @method_decorator(cache_api_view(use_models=[Order]))
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
            
