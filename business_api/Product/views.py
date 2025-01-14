from rest_framework.views import APIView
from BaseSecurity.permissions import isSuperUser
from BaseSecurity.services import SecureResponse
from .serializers import CategorySerializer, ProductSerializer
from .models import Category, Product

class GetProductsCategory(APIView): 
    
    permission_classes = []
    serializer_class = ProductSerializer

    def get(self, request):
        category_name = request.GET['category_name']

        try:    
            return SecureResponse(
                request=request,
                data=self.serializer_class(
                    instance=Category.objects.filter(
                        is_active=True,
                        category=Category.objects.filter(name=category_name)
                        ),
                    many=True
                    ),
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)

class GetAllProducts(APIView): 
    
    permission_classes = []
    serializer_class = ProductSerializer

    def get(self, request):
        return SecureResponse(
            request=request,
            data=self.serializer_class(
                instance=Product.objects.filter(is_active=True),
                many=True
                ),
            status=200
            )

class GetProduct(APIView): 
    
    permission_classes = []
    serializer_class = ProductSerializer

    def get(self, request):
        product_id = request.GET['product_id']

        try:
            return SecureResponse(
                request=request,
                data=self.serializer_class(
                    instance=Product.objects.get(
                        is_active=True,
                        id=product_id
                        ),
                status=200
                    ),
                )
        except: 
            return SecureResponse(request=request, status=400)

class UpdateProduct(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = ProductSerializer

    def get(self, request):
        return SecureResponse(request=request)

class CreateProduct(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = ProductSerializer

    def get(self, request):
        return SecureResponse(request=request)

class AddImageProduct(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = ProductSerializer

    def get(self, request):
        return SecureResponse(request=request)

class CreateCategory(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = CategorySerializer

    def get(self, request):
        return SecureResponse(request=request)

class UpdateCategory(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = CategorySerializer

    def get(self, request):
        return SecureResponse(request=request)

class AddImageCategory(APIView): 

    permission_classes = [isSuperUser]
    serializer_class = CategorySerializer

    def get(self, request):
        return SecureResponse(request=request)

class GetAllCategorys(APIView): 
    
    permission_classes = []
    serializer_class = CategorySerializer

    def get(self, request):
        try:
            return SecureResponse(
                request=request,
                data=self.serializer_class(
                    instance=Category.objects.filter(is_active=True),
                    many=True
                    ),
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)