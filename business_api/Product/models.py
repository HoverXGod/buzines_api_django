from django.db import models
from User.models import User
from .serializers import UserCartSerializer, ProductCartSerializer

class Category(models.Model):
    """Модель категори к которой относятся товары"""

    name = models.CharField(max_length=64, unique=True)
    description = models.TextField()
    image = models.CharField(max_length=256, default='')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Категория'  # Имя модели в единственном числе
        verbose_name_plural = 'Категории'  # Имя модели во множественном числе

    @property
    def active(self): return self.active

    @active.setter
    def active(self, value): 
        self.active = value
        self.save()

    @staticmethod
    def create_category(name, description): 
        """Создание категории по имени и описанию"""

        try:
            category = Category(
                name=name,
                description=description
            )
            category.save()
        except: return None
        
        return category

    def update_category(self, name=None, description=None, image=None): 
        """Обновление категории, а именно имени, описания и изображения"""

        try:
            if name != None: self.name = name
            if image != None: self.image = image
            if description != None: self.description = description

            self.save()
        except: return None
        return self


    def delete_category(self): 
        """Удаление категории"""

        bufer = self
        self.delete()
        return bufer

class Product(models.model):
    """Модель товара относящегося к категории"""

    name = models.CharField(max_length=64)
    description = models.TextField()
    price = models.FloatField()
    weight = models.FloatField(default=0)
    by_weight = models.BooleanField(default=False)
    image = models.CharField(max_length=256, default='')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    weight_start = models.FloatField()
    weight_end = models.FloatField()

    class Meta:
        verbose_name = 'Продукт'  # Имя модели в единственном числе
        verbose_name_plural = 'Продукты'  # Имя модели во множественном числе

    @property
    def active(self): return self.active

    @active.setter
    def active(self, value): 
        self.active = value
        self.save()
    
    @staticmethod
    def create_product(name, description, price, category, weight=0, weight_start=0, weight_end=0):
        """Создание продукта и прикрепление его к категории"""
        
        if weight != 0:
            by_weight = True
        else: by_weight = False
        
        try:
            pr = Product(
                name=name,
                description=description,
                category=category,
                price=price,
                by_weight=by_weight,
                weight=weight,
                weight_start=weight_start,
                weight_end=weight_end
            ) 
            pr.save()
        except: return None
        return pr
        

    def update_product(self, image=None, name=None, description=None, price=None): 
        """Обновление данных продукта и добавление изображения к товару"""
        
        try:
            if name != None: self.name = name
            if description != None: self.description = description
            if price != None: self.price = price
            if image != None: self.image = image
        except: return None
        
        self.save()
        return self

        

    @staticmethod
    def get_products(category_name): 
        """Вовзращает все активные продукты в категории по ее имени"""

        try: return Product.objects.filter(
            category=Category.objects.get(name=category_name),
            is_active=True
            )
        except: return None

    def delete_product(self): 
        """Удаление продукта, возвращает данные об удалённом продукте"""


        bufer = self
        self.delete()
        return bufer
    
class Cart(models.Model):
    """Хранение товаров пользователей"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    time_add = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Коризна'  # Имя модели в единственном числе
        verbose_name_plural = 'Корзины'  # Имя модели во множественном числе


    @staticmethod
    def get_user_cart(user):
        """Возвращает полный перечень товаров пользователя"""

        try: 
             return Cart.objects.all(user=user)
        except: return None

    @staticmethod
    def get_user_cart_id(user) -> str:
        """Возвращает полный перечень товаров пользователя в виде их id через запятую"""

        try: 
            cart = Cart.objects.all(user=user)
        except: return None

        cart = UserCartSerializer(instance=cart).data
        
        temp_list = list()
        
        for x in cart: temp_list.append(x['id'])
        
        return ",".join(temp_list)


    @staticmethod
    def clear_user_cart(user): return

    @staticmethod
    def add_product_in_cart(product, user): return

    @staticmethod
    def get_all_cart__product(product):
        """Возвращает полный перечень пользователей с этим товаром в корзине"""

        try: 
            return Cart.objects.all(product=product)
        except: return None

class Promotion(models.model):
    """"""
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    discount = models.FloatField(max_length=100)
    description = models.TextField(max_length=512, default="Base")
    name = models.CharField(max_length=64, default="Base")

    class Meta:
        verbose_name = 'Акция'  # Имя модели в единственном числе
        verbose_name_plural = 'Акции'  # Имя модели во множественном числе


    ...

class PersonalDiscount(models.model):
    """"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    discount = models.FloatField(max_length=100)
    description = models.TextField(max_length=512, default="Base")
    name = models.CharField(max_length=64, default="Base")

    class Meta:
        verbose_name = 'Персональная скидка'  # Имя модели в единственном числе
        verbose_name_plural = 'Персональные скидки'  # Имя модели во множественном числе


    ...