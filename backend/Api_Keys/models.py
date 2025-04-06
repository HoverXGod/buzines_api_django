from Encryption.utils import Encryption
from BaseSecurity.utils import Key_Generator
from datetime import datetime
from django.db import models
from User.models import User

class Api_key(models.Model):
    """Модель апи ключей для взаимодействия пользователей с нашим API"""

    key_name = models.CharField(max_length=32)
    key_value = models.BinaryField (max_length=32)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    help_text = models.CharField(max_length=128)
    is_active = models.BooleanField()
    created_at = models.DateField()
    updated_at = models.DateField()

    class Meta:
        verbose_name = 'Ключ API'  # Имя модели в единственном числе
        verbose_name_plural = 'Ключи API'  # Имя модели во множественном числе

    def __str__(self): 
        """Данные о имени ключа и его владельца"""
        
        return f"{self.key_name} for {self.user.username}"

    def save(self, *args, **kwargs):
        """Переопределяем метод Save() для автоматического шифрования ключа"""
        
        if self.key_value: 
            self.key_value = Encryption.encrypt_data(self.key_value)
        
        super().save(*args, **kwargs)

    @property
    def name_key(self): return self.key_name

    @name_key.setter
    def name_key(self, value): 
        self.key_name = value
        self.save()

    @property
    def key(self):
        """Получение расшифрованного ключа"""
        
        return Encryption.decrypt_data(self.key_value)

    @key.setter
    def key(self, value):
        """Обновляет и шифрует ключ"""
        
        self.update_key(value)

    def del_key(self):
        """Удаление ключа"""
        
        return self.delete()
    
    def update_key_random(self): 
        """Обновление ключа на рандомный другой"""
        
        key = Key_Generator.generate_base_api_key()
        self.key_value = key
        self.updated_at = datetime.now().__str__()
        self.save()

    def update_key(self, value):
        """Обновление ключа на выше значение"""
        
        self.key_value = value
        self.updated_at = datetime.now().__str__()
        self.save()

    def _generate_jat(self) -> str:
        """Метод для генерации JAT Токена , нужен только внутри системы, никуда не передаётся"""
        from BaseSecurity.utils import JWT_auth

        try: return JWT_auth.compile_jwt_token(self.user)
        except: return None