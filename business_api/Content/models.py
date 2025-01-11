from django.db import models
from User.models import User
from datetime import datetime

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
    def create_post(text='', author=None, images='', title=''):
        """Создание поста"""
         
        date = datetime.now().date().__str__()
        post = Post(
            text=text,
            author=author,
            images=images,
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

    class Meta: pass

    @staticmethod
    def get_page_text(index, page_name): pass

    @staticmethod
    def create_page_text(): pass

    def update_page_text(self): pass