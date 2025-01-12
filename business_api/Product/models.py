from django.db import models

class Category(models.Model):
    """Модель категори к которой относятся товары"""

    name = models.CharField(max_length=64)
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
    def create_category(): pass

    def update_category(self): pass

    def delete_category(self): pass

class Product(models.model):
    """Модель товара относящегося к категории"""

    name = models.CharField(max_length=64)
    description = models.TextField()
    price = models.FloatField()
    weight = models.FloatField(default=0)
    have_weight = models.BooleanField(default=False)
    image = models.CharField(max_length=256, default='')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

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
    def create_product(): pass

    def update_product(self): pass

    @staticmethod
    def get_products(category_name): pass

    def delete_product(self): pass