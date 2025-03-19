from rest_framework.views import APIView
from BaseSecurity.permissions import isSuperUser, isAutorized
from BaseSecurity.services import SecureResponse
from .serializers import *
from .models import *

class GetProductsCategory(APIView): 
    
    permission_classes = []
    serializer_class = ProductSerializer

    def get(self, request):
        category_name = request.GET['category_name']

        try:    
            return SecureResponse(
                request=request,
                data=self.serializer_class(
                    instance=Product.objects.filter(
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
            category = Category.objects.get(name=request.GET['category_name'])

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
        
class CreatePromotion(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = PromotionSerializer

    def get(self, request):

        product = Product.objects.get(id=request.GET['product_id'])
        discount = request.GET['discount']
        description = request.GET['description']
        name = request.GET['name']

        try:
            return SecureResponse(
                request=request, 
                data=self.serializer_class(
                    instance=Promotion.create_promotion(
                        product=product,
                        discount=discount,
                        description=description,
                        name=name,
                        )
                    ).data,
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)
        
class CreatePersonalDiscount(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = PersonalDiscountSerializer

    def get(self, request):

        product = Product.objects.get(id=request.GET['product_id'])
        discount = request.GET['discount']
        description = request.GET['description']
        name = request.GET['name']

        try:
            return SecureResponse(
                request=request, 
                data=self.serializer_class(
                    instance=PersonalDiscount.create_personal_discount(
                        user=request.user,
                        product=product,
                        discount=discount,
                        description=description,
                        name=name,
                        )
                    ).data,
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)
        
class CreatePromocode(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = PromoCodeSerializer

    def get(self, request):

        code = request.GET['promocode']
        discount = request.GET['discount']

        try:
            return SecureResponse(
                request=request, 
                data=self.serializer_class(
                    instance=Promocode.create_promo(
                        code=code,
                        discount=discount
                        ),
                    many=True
                    ).data,
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)
        
class AddProductInCart(APIView): 
    
    permission_classes = []
    serializer_class = CartSerializer

    def get(self, request):

        product = Product.objects.get(id=request.GET['product_id'])

        try:
            quanity = request.GET['weight_quanity']
        except: quanity = 1

        try:
            return SecureResponse(
                request=request, 
                data=self.serializer_class(
                    instance=Cart.add_product_in_cart(
                        user=request.user,
                        product=product,
                        quanity=quanity
                        )
                    ).data,
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)
        
class GetAllPromotions(APIView): 
    
    permission_classes = [isAutorized]
    serializer_class = PromotionSerializer

    def get(self, request):

        try:
            return SecureResponse(
                request=request, 
                data=self.serializer_class(
                    instance=Promotion.get_all_promotions(),
                    many=True,
                    ).data,
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)
        
class GetPersonalDiscount(APIView): 
    
    permission_classes = [isAutorized]
    serializer_class = PersonalDiscountSerializer

    def get(self, request):

        try:
            return SecureResponse(
                request=request, 
                data=self.serializer_class(
                    instance=PersonalDiscount.get_user_personal_discount(request.user)
                    ).data,
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)

class GetUserCart(APIView): 
    
    permission_classes = [isAutorized]
    serializer_class = UserCartSerializer

    def get(self, request):

        try:
            return SecureResponse(
                request=request, 
                data=self.serializer_class(
                    instance=Cart.get_user_cart(request.user)
                    ).data,
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)
        
class GetPromocode(APIView): 
    
    permission_classes = [isAutorized]
    serializer_class = PromoCodeSerializer

    def get(self, request):

        try:
            return SecureResponse(
                request=request, 
                data=self.serializer_class(
                    instance=Promocode.get_promo(request.GET['promocode'])
                    ).data,
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)
        
class DeletePromotion(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = None

    def get(self, request):

        try:

            object = Promotion.objects.get(id=request.GET['id'])

            object.delete_promotion()

            return SecureResponse(
                request=request, 
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)
        
class DeletePersonalDiscount(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = None

    def get(self, request):

        try:

            object = PersonalDiscount.objects.get(id=request.GET['id'])

            object.delete_personal_discount()

            return SecureResponse(
                request=request, 
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)
        
class DeletePromocde(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = None

    def get(self, request):

        try:

            object = Promocode.objects.get(id=request.GET['id'])

            Promocode.DeletePromocde()

            return SecureResponse(
                request=request, 
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)
        
class RemoveProductInUserCart(APIView): 
    
    permission_classes = [isAutorized]
    serializer_class = None

    def get(self, request):

        try:

            object = Cart.objects.get(id=request.GET['id'], user=request.user)

            object.delete()

            return SecureResponse(
                request=request, 
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)
        
class RemoveUserCart(APIView): 
    
    permission_classes = [isAutorized]
    serializer_class = None

    def get(self, request):

        try:

            objects = Cart.objects.get(user=request.user)

            for x in objects: x.delete()

            return SecureResponse(
                request=request, 
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)
        
class GetCartCost(APIView): 
    
    permission_classes = [isAutorized]
    serializer_class = CartSerializer

    def get(self, request):

        try:
            return SecureResponse(
                request=request, 
                data={
                    "cost": Cart.calculate_base_cost(request.user)
                },
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)
        
class GetCartDiscount(APIView): 
    
    permission_classes = [isAutorized]
    serializer_class = CartSerializer

    def get(self, request):

        try:
            return SecureResponse(
                request=request, 
                data={
                    "discount":Cart.calculate_base_cost(request.user) - Cart.calculate_total(request.user)
                },
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)