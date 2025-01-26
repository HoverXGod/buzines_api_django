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
                    ).data,
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
                ).data,
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
                    ).data,
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)

class UpdateProduct(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = ProductSerializer

    def get(self, request):
        try:
            try: name = request.GET['name']
            except: name = None
            try: price = request.GET['price']
            except: price = None
            try: description = request.GET['description']
            except: description = None
            try: product_id = request.GET['id']
            except: return SecureResponse(request=request, status=400)
            pr = Product.objects.get(id=product_id)
            pr = pr.update_product(self, name=name, description=description, price=price)

        except: return SecureResponse(request=request,status=400)
        return SecureResponse(request=request)

class CreateProduct(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = ProductSerializer

    def get(self, request):
        try:
            weigth = request.GET['by_weigth']
            name = request.GET['name']
            description = request.GET['description']
            price = request.GET['price']
            category = request.GET['category_name']

            if int(weigth) == 1:
                weight = request.GET['weight']
                weight_start = request.GET['weight_start']
                weight_end = request.GET['weight_end']
                pr = Product.create_product(name, description, price, category, weight, weight_start, weight_end)
            else:
                pr = Product.create_product(name, description, price, category)
        except: return SecureResponse(request=request, status=400)
        
        return SecureResponse(request=request,data=self.serializer_class(instance=pr).data, status=200)
        

class AddImageProduct(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = ProductSerializer

    def get(self, request):
        return SecureResponse(request=request)

class CreateCategory(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = CategorySerializer

    def get(self, request):
        try:
            description = request.GET['description']
            name = request.GET['name']
        except: return SecureResponse(request=request, status=400)

        ct = Category.create_category(name, description)
        return SecureResponse(request=request, data=self.serializer_class(instance=ct).data, status=200)

class UpdateCategory(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = CategorySerializer

    def get(self, request):
        try: description = request.GET['description']
        except: description = None
        try: name = request.GET['name']
        except: name = None
        try: category_id = request.GET['id']
        except: return SecureResponse(request=request, status=400)

        try:
            ct = Category.objects.get(id=category_id)
            ct = ct.update_category(name=name, description=description)
        except: 
            return SecureResponse(request=request, status=400)

        return SecureResponse(request=request, data=self.serializer_class(instance=ct).data, status=200)

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
                    ).data,
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)