from rest_framework.views import APIView
from BaseSecurity.permissions import isAutorized, isSuperUser, isAdmin
from BaseSecurity.services import SecureResponse
from .serializers import CategorySerializer, ProductSerializer
from .models import Category, Product

class GetProductsCategory(APIView): pass

class GetAllProducts(APIView): pass

class GetProduct(APIView): pass

class UpdateProduct(APIView): pass

class CreateProduct(APIView): pass

class AddImageProduct(APIView): pass

class CreateCategory(APIView): pass

class UpdateCategory(APIView): pass

class AddImageCategory(APIView): pass

class GetAllCategorys(APIView): pass
