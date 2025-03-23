from django.db import models
from django.db.models import Max
from User.models import User, UserGroup, UserGroupItem

class Category(models.Model):
    """Модель категори к которой относятся товары"""

    name = models.CharField(max_length=64, unique=True)
    description = models.TextField()
    slug = models.SlugField(max_length=255, unique=True, null=True)
    image = models.CharField(max_length=256, default='', null=True)
    is_active = models.BooleanField(default=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    meta_title = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Категория'  # Имя модели в единственном числе
        verbose_name_plural = 'Категории'  # Имя модели во множественном числе

    def __str__(self): return self.name

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

class Product(models.Model):
    """Модель товара относящегося к категории"""

    name = models.CharField(max_length=64)
    description = models.TextField()
    price = models.FloatField()
    weight = models.FloatField(default=0)
    by_weight = models.BooleanField(default=False)
    image = models.CharField(max_length=256, default='', null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    weight_start = models.FloatField()
    weight_end = models.FloatField()

    sku = models.CharField(max_length=32, unique=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    slug = models.SlugField(max_length=255, unique=True, null=True)

    def __str__(self): return self.name

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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quanity = models.FloatField(default=1.0)
    time_add = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Коризна'  # Имя модели в единственном числе
        verbose_name_plural = 'Корзины'  # Имя модели во множественном числе


    @staticmethod
    def get_user_cart(user):
        """Возвращает полный перечень товаров пользователя"""

        try: 
             return Cart.objects.filter(user=user)
        except: return None

    @staticmethod
    def get_user_cart_id(user) -> str:
        """Возвращает полный перечень товаров пользователя в виде их id через запятую"""

        try: 
            cart = Cart.objects.filter(user=user)
        except: return None

        from .serializers import UserCartSerializer

        cart = UserCartSerializer(instance=cart, many=True).data
        
        temp_list = list()
        
        for x in cart: temp_list.append(str(x['product']['id']))
        
        return ",".join(temp_list)

    @staticmethod
    def add_product_in_cart(product, user, quanity): 
        """Добавляет товар в коризну и возваращет его"""

        Cart(product=product, user=user, quanity=quanity).save()
        return Cart.objects.last()

    @staticmethod
    def get_all_cart__product(product):
        """Возвращает полный перечень пользователей с этим товаром в корзине"""

        try: 
            return Cart.objects.filter(product=product)
        except: return None

    @staticmethod
    def delete_user_cart(user):
        """Удаление товаров в корзине пользователя"""
        
        Cart.objects.filter(user=user).delete()
        return True
    

    @staticmethod
    def calculate_base_cost(user):

        cart_items = Cart.objects.filter(user=user).select_related('product')
        
        if not cart_items.exists():
            return 0.0
        
        original_total = 0.0

        for item in cart_items:
            product = item.product
            quantity = item.quanity
            
            # Рассчитываем базовую стоимость в зависимости от типа товара
            if product.by_weight:
                base_price = product.price * quantity  # price за единицу веса
            else:
                base_price = product.price * quantity  # price за штуку
            
            original_total += base_price

        return original_total
    
    @staticmethod
    def calculate_total(user, promo_code=None):
        
        cart_items = Cart.objects.filter(user=user).select_related('product')

        if not cart_items.exists():
            return [0.0, []]
        product_ids = [item.product.id for item in cart_items]
        
        # Получаем максимальные скидки для всех продуктов в корзине
        promo_discounts = Promotion.objects.filter(
            product_id__in=product_ids,
            on_start=True
        ).values('product_id').annotate(max_discount=Max('discount'))
        
        personal_discounts = PersonalDiscount.objects.filter(
            user=user,
            product_id__in=product_ids,
            on_start=True
        ).values('product_id').annotate(max_discount=Max('discount'))

        group_discounts = GroupPromotion.objects.filter(
            user_group_id__in=UserGroup.get_user_groups__id(user),
            product_id__in=product_ids,
            on_start=True
        ).values('product_id').annotate(max_discount=Max('discount'))

        # Создаем словари для быстрого доступа
        promo_dict = {pd['product_id']: {"discount": pd['max_discount'], "promotion": pd['name']} for pd in promo_discounts}
        personal_dict = {pd['product_id']: {"discount": pd['max_discount'], "promotion": pd['name']} for pd in personal_discounts}
        group_dict = {pd['product_id']: {"discount": pd['max_discount'], "promotion": pd['name']} for pd in group_discounts}

        product_dict = dict()

        original_total = 0.0
        total_with_discounts = 0.0

        shag = 1

        for item in cart_items:
            product_dict[shag] = dict()
            shag += 1

            product = item.product
            quanity = item.quanity

            product_dict[shag]['product'] = product
            product_dict[shag]['quanity'] = quanity
            
            # Рассчитываем базовую стоимость в зависимости от типа товара
            if product.by_weight:
                base_price = product.price * quanity  # price за единицу веса
            else:
                base_price = product.price * quanity  # price за штуку
            
            original_total += base_price

            # Получаем максимальные скидки
            promo_disc = promo_dict.get(product.id, 0)
            personal_disc = personal_dict.get(product.id, 0)
            group_disc = group_dict.get(product.id, 0)
            max_disc = min(max(promo_disc['discount'], max(personal_disc['discount'], group_disc['discount'])), 50)  # Ограничение до 50%

            # Применяем скидку к товару
            discounted_price = base_price * (100 - max_disc) / 100
            total_with_discounts += discounted_price

            product_dict[shag]['promotion'] = "None"

            for x in promo_disc:
                if x['discount'] == max_disc:
                    product_dict[shag]['promotion'] = x['promotion']
            
            for x in group_disc:
                if x['discount'] == max_disc:
                    product_dict[shag]['promotion'] = x['promotion']

            for x in personal_disc:
                if x['discount'] == max_disc:
                    product_dict[shag]['promotion'] = x['promotion'] 

            product_dict[shag]['price'] = base_price
            product_dict[shag]['discount'] = base_price - discounted_price

        # Обработка промокода
        promo_discount = 0
        if promo_code:
            try:
                promo = Promocode.objects.get(code=promo_code)
                promo_discount = min(promo.discount, 100)
            except Promocode.DoesNotExist:
                pass

        # Применяем промокод к общей сумме
        if promo_discount > 0:
            total_after_promo = total_with_discounts * (100 - promo_discount) / 100
        else:
            total_after_promo = total_with_discounts

        # Проверяем общее ограничение в 50%
        if original_total > 0:
            total_discount = ((original_total - total_after_promo) / original_total) * 100
            if total_discount > 50:
                total_after_promo = original_total * 0.5

        return [round(total_after_promo, 2), product_dict]

class Promotion(models.Model):
    """Акции на товары"""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    discount = models.FloatField(max_length=100)
    description = models.TextField(max_length=512, default="Base")
    name = models.CharField(max_length=64, default="Base")
    on_start = models.BooleanField(default=False)

    start_date = models.DateTimeField(auto_now=True)
    end_date = models.DateTimeField(null=True)
    max_usage = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)

    def __str__(self): return self.name

    class Meta:
        verbose_name = 'Акция'  # Имя модели в единственном числе
        verbose_name_plural = 'Акции'  # Имя модели во множественном числе

    @staticmethod
    def create_promotion(product=None, discount=1, description="", name="User discount"):
        """Создание акции"""
        
        return Promotion(
            product=product,
            discount=discount,
            description=description,
            name=name
        ).save()
        
    @property
    def started(self): return self.on_start

    @property
    def created(self): return self.start_date

    @started.setter
    def started(self, value):
        self.on_start = value
        self.save()
        return self.on_start
        
    def delete_promotion(self):
        """Удаление акции"""

        self.delete()
        return True
    
    @staticmethod
    def get_all_promotions():
        """Получение всех активных акций"""

        return Promotion.objects.filter(on_start=True)

class PersonalDiscount(models.Model):
    """Персональные скидки пользователей"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    discount = models.FloatField(max_length=100)
    description = models.TextField(max_length=512, default="Base")
    name = models.CharField(max_length=64, default="Base")
    on_start = models.BooleanField(default=False)

    start_date = models.DateTimeField(auto_now=True)
    end_date = models.DateTimeField(null=True)
    max_usage = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)

    def __str__(self): return self.name

    class Meta:
        verbose_name = 'Персональная скидка'  # Имя модели в единственном числе
        verbose_name_plural = 'Персональные скидки'  # Имя модели во множественном числе

    @property
    def created(self): return self.start_date

    @staticmethod
    def create_personal_discount(user, product=None, discount=1, description="", name="User discount"):
        """Создание акции"""
        
        return PersonalDiscount(
            user=user,
            product=product,
            discount=discount,
            description=description,
            name=name
        ).save()
        
    @property
    def started(self): return self.on_start

    @started.setter
    def started(self, value):
        self.on_start = value
        self.save()
        return self.on_start
        
    def delete_personal_discount(self):
        """Удаление акции"""

        self.delete()
        return True
    
    @staticmethod
    def get_user_personal_discount(user):
        """Получение всех индвидуальных предложенй пользователя"""
        
        return PersonalDiscount.objects.filter(user=user, on_start=True)
    
class Promocode(models.Model):
    code = models.TextField(max_length=64)
    discount = models.IntegerField()

    class Meta:
        verbose_name = 'Промокод'  # Имя модели в единственном числе
        verbose_name_plural = 'Промокоды'  # Имя модели во множественном числе


    @staticmethod
    def create_promo(code, discount): 
        """Создание промокода"""
        
        return Promocode(
            code=code,
            discount=discount
        ).save()

    @staticmethod
    def get_promo(code): 
        """Получение промокода по коду"""

        try: return Promocode.objects.get(code=code).discount
        except: return -99

    def del_promo(self): 
        """Удаление промокода"""

        self.delete()
        return True
    
class GroupPromotion(models.Model):
    """Акции для групп пользователей"""

    user_group = models.ForeignKey(UserGroup, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    discount = models.FloatField(max_length=100)
    description = models.TextField(max_length=512, default="Base")
    name = models.CharField(max_length=64, default="Base")
    on_start = models.BooleanField(default=False)

    start_date = models.DateTimeField(auto_now=True)
    end_date = models.DateTimeField(null=True)
    max_usage = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)

    def __str__(self): return self.name

    class Meta:
        verbose_name = 'Акция для группы'  # Имя модели в единственном числе
        verbose_name_plural = 'Акции для групп'  # Имя модели во множественном числе

    @property
    def created(self): return self.start_date

    @staticmethod
    def get_user_personal_discount(user):
        """Возвращает акции пользовательской группы"""
        return GroupPromotion.objects.filter(
            user_group=UserGroup.get_user_groups__list(
                user
                )
            )