from rest_framework.views import APIView
from BaseSecurity.permissions import isSuperUser, isAutorized
from BaseSecurity.services import SecureResponse
from .serializers import *
from .models import *
from Analytics.models import SalesFunnel
from BaseSecurity.utils import get_client_ip
from django.core.management import call_command
from Analytics.models import CustomerBehavior
from core.cache import cache_api_view
from django.utils.decorators import method_decorator

class GetProductsCategory(APIView):
    
    permission_classes = []
    serializer_class = ProductSerializer

    @method_decorator(cache_api_view(use_models=[Category]))
    def get(self, request):
        category_name = request.GET['category_name']

        if request.user.is_authenticated:
            try:
                CustomerBehavior.objects.get(user = request.user).add_view()
            except: pass
        try:    
            return SecureResponse(
                request=request,
                data=self.serializer_class(
                    instance=Product.objects.filter(
                        is_active=True,
                        category=Category.objects.get(name=category_name)
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

    @method_decorator(cache_api_view(use_models=[Product]))
    def get(self, request):

        if request.user.is_authenticated:
            try:
                CustomerBehavior.objects.get(user = request.user).add_view()
            except: pass
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

    @method_decorator(cache_api_view(use_models=[Product]))
    def get(self, request):
        product_id = request.GET['product_id']
        if request.user.is_authenticated:
            CustomerBehavior.objects.get(user = request.user).add_view()

        try: item = Product.objects.get(
                        id=product_id
                        )
        except: return SecureResponse(request=request, status=400)

        item.add_view()

        try:
            if request.user.is_authenticated:
                user_agent = request.user_agent

                # Проверяем тип устройства
                if user_agent.is_mobile:
                    device_type = "mobile"
                elif user_agent.is_tablet:
                    device_type = "tablet"
                elif user_agent.is_pc:
                    device_type = "desktop"
                else: device_type = None

                SalesFunnel.objects.add_entry(
                    user=request.user,
                    product=item,
                    stage='view',
                    device_type=device_type,
                    session_data={
                        'ip': get_client_ip(request),
                    }
                    )
        except: pass

        return SecureResponse(
            request=request, data=self.serializer_class(instance=item).data, status=200)

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

            call_command('init_performance')
        except: return SecureResponse(request=request, status=400)
        
        return SecureResponse(request=request,data=self.serializer_class(instance=pr).data, status=200)   

class AddImageProduct(APIView): 
    
    permission_classes = [isSuperUser]
    serializer_class = ProductSerializer

    def get(self, request):
        return SecureResponse(request=request) # TODO: Доделать

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

    @method_decorator(cache_api_view(use_models=[Category]))
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
    
    permission_classes = [isAutorized]
    serializer_class = CartSerializer

    def get(self, request):

        product = Product.objects.get(id=request.GET['product_id'])

        product.add_cart()

        try:
            CustomerBehavior.objects.get(user = request.user).cart_action()
        except: pass

        try:
            quanity = request.GET['weight_quanity']
        except: quanity = 1

        try:

            try:
                if request.user.is_authenticated:
                    user_agent = request.user_agent

                    # Проверяем тип устройства
                    if user_agent.is_mobile:
                        device_type = "mobile"
                    elif user_agent.is_tablet:
                        device_type = "tablet"
                    elif user_agent.is_pc:
                        device_type = "desktop"
                    else: device_type = None

                    SalesFunnel.objects.add_entry(
                        user=request.user,
                        product=product,
                        stage='cart',
                        device_type=device_type,
                        session_data={
                            'ip': get_client_ip(request),
                        }
                        )
            except : pass

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

    @method_decorator(cache_api_view(use_models=[Promotion]))
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
    serializer_classes = [PersonalDiscountSerializer, GroupPromotionSerializer]

    @method_decorator(cache_api_view(use_models=[PersonalDiscount, GroupPromotion]))
    def get(self, request):

        try:
            return SecureResponse(
                request=request, 
                data={
                    "Personal": self.serializer_classes[0](
                        instance=PersonalDiscount.get_user_personal_discount(request.user.id),
                        many=True
                        ).data,
                    "Group": self.serializer_classes[1](
                        instance=GroupPromotion.get_user_personal_discount(request.user.id),
                        many=True
                        ).data},
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)

class GetUserCart(APIView):
    
    permission_classes = [isAutorized]
    serializer_class = UserCartSerializer

    @method_decorator(cache_api_view(use_models=[Cart]))
    def get(self, request):

        try:
            return SecureResponse(
                request=request, 
                data=self.serializer_class(
                    instance=request.user.cart.all(),
                    many=True
                    ).data,
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)
        

class GetPromocode(APIView):
    
    permission_classes = [isAutorized]
    serializer_class = PromoCodeSerializer

    @method_decorator(cache_api_view(use_models=[Promocode]))
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

        CustomerBehavior.objects.get(user = request.user).cart_action()

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

            CustomerBehavior.objects.get(user = request.user).cart_action()

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

    @method_decorator(cache_api_view(use_models=[Cart]))
    def get(self, request):

        try:
            return SecureResponse(
                request=request, 
                data={
                    "cost": Cart.calculate_base_cost(request.user.id)
                },
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)

class GetCartDiscount(APIView):
    
    permission_classes = [isAutorized]
    serializer_class = CartSerializer

    @method_decorator(cache_api_view(use_models=[Cart]))
    def get(self, request):

        try:
            return SecureResponse(
                request=request, 
                data={
                    "discount":Cart.calculate_base_cost(request.user.id) - Cart.calculate_total(request.user.id)
                },
                status=200
                )
        except: 
            return SecureResponse(request=request, status=400)