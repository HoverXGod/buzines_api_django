from django.db import models
from User.models import User
from datetime import datetime
from .services import ImagesManager
from Product.models import Product
from core.cache import cache_method

class Post(models.Model):
    """Модель поста, имеющая базовые методы, ключ привязан к пользователю"""

    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateField()
    updated_at = models.DateField()
    images = models.CharField(max_length=256, default="")
    title = models.CharField(max_length=64)
    
    class Meta: 
        verbose_name = 'Пост'  # Имя модели в единственном числе
        verbose_name_plural = 'Посты'  # Имя модели во множественном числе

    @staticmethod
    def create_post(text='', author=None, images=None, title=''):
        """Создание поста"""
         
        date = datetime.now().date().__str__()
        post = Post(
            text=text,
            author=author,
            images=ImagesManager.set_objects_images(images),
            title=title,
            created_at=date,
            updated_at=date
        )

        post.save()

        return Post

    def update_post(self, text='', title=''):
        """Изменения заголовка или текста поста"""

        if text != '': self.text = text
        if title != '': self.title = title

        if text != '' or title != '': 
            self.updated_at = datetime.now().date().__str__()
            self.save()

        return self
    
    def update_image(self, image=''):
        """Изменение/добавление изображений"""
        
        if image != '': 
            self.images = image
            self.save()

        return self
    def del_post(self):
        """Удаление поста"""
        self.delete()

class PageText(models.Model):
    """Текст контента на страницах"""

    index = models.CharField(max_length=64)
    text = models.TextField()
    page_name = models.CharField(max_length=64)
    template_id = models.IntegerField(null=True)

    class Meta: 
        verbose_name = 'Текст страницы'  # Имя модели в единственном числе
        verbose_name_plural = 'Тексты страниц'  # Имя модели во множественном числе

    @cache_method(use_models=['Content.PageText'])
    @staticmethod
    def get_page_texts(page_name): 
        """Возвращает текст станицы по индексу"""
        
        try:
            return PageText.objects.filter(page_name=page_name)
        except: return None


    @staticmethod
    def create_page_text(index, text, page_name): 
        """Создаём текст и сохраняем его с индексом и именем страницы"""

        text = PageText(index=index, text=text, page_name=page_name)
        
        try: 
            PageText.objects.get(index=index, page_name=page_name)
            return None
        except: text.save()
        
        return PageText.objects.all().last()

    @staticmethod
    def update_page_text(index, text, page_name): 
        """Обновляем текст по имени страницы и индексу"""

        try: text_obj = PageText.objects.get(index=index, page_name=page_name)
        except: return None

        text_obj.text = text
        text_obj.save()

        return text_obj
    
    @staticmethod
    def delete_page(page_name):
        """Удаление всего текста привязанного к странице"""

        try: texts = PageText.objects.filter(page_name=page_name)
        except: return None

        texts_bufer = texts

        for t in texts: t.delete()

        return texts_bufer

    @staticmethod
    def delete_page_text(page_name, index):
        """Удаление текста по имени страницы и индексу"""
        
        try: text = PageText.objects.get(index=index, page_name=page_name)
        except: return None

        text_bufer = text

        text.delete()

        return text_bufer

class PageColor(models.Model):
    index = models.IntegerField()
    page_name = models.CharField(max_length=64)
    color = models.CharField(max_length=12)

    class Meta:
        verbose_name = 'Цвет на странице'  # Имя модели в единственном числе
        verbose_name_plural = 'Цвета на страницах'  # Имя модели во множественном числе

class Buttons(models.Model):
    index = models.IntegerField()
    template_id = models.IntegerField()
    action = models.CharField(max_length=64)

    class Meta:
        verbose_name = 'Кнопка на странице'  # Имя модели в единственном числе
        verbose_name_plural = 'Кнопки на страницах'  # Имя модели во множественном числе

class ProductCard(models.Model):
    template_id = models.IntegerField()
    product_id = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='card')

    class Meta:
        verbose_name = 'Карточка товара'  # Имя модели в единственном числе
        verbose_name_plural = 'Карточки товаров'  # Имя модели во множественном числе

class NavBarSettings(models.Model):
    pages = models.JSONField()
    template_id = models.IntegerField()
    buttons = models.JSONField()

    class Meta:
        verbose_name = 'Настройки навигационной панели'  # Имя модели в единственном числе

class FooterSettings(models.Model):
    data = models.JSONField()
    template_id = models.IntegerField()
    buttons = models.JSONField()

    class Meta:
        verbose_name = 'Настройки футера'  # Имя модели в единственном числе
