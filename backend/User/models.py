from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from Encryption.utils import Encryption
from BaseSecurity.utils import Key_Generator
from datetime import datetime

class User(AbstractUser):   
    """Модель Пользователя, имеет базовые методы"""

    USER_TYPE_CHOICES = (
        ('customer', 'Покупатель'),
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
    )

    base_password = models.BinaryField()
    username = models.CharField(max_length=128, unique=True)
    email = models.CharField(null=True, max_length = 64)
    isAdministrator = models.BooleanField(default=False)
    isModerator = models.BooleanField(default=False)
    phone_number = models.CharField(default='', max_length = 18)
    address = models.TextField(max_length=256, default='')
    currency = models.CharField(max_length=3, default='RUB')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    acquisition_source = models.CharField(max_length=64, default='unknown')

    class Meta:
        verbose_name = 'Пользователь'  # Имя модели в единственном числе
        verbose_name_plural = 'Пользователи'  # Имя модели во множественном числе

    @property
    def default_currency(self): return self.currency

    def short_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return f"{self.username}: {self.first_name} {self.last_name}"

    def set_password(self, raw_password): 
        self.password = Encryption.encrypt_data(data=raw_password)
        self.save

    def get_user_api(self):
        """Получение последнего апи ключа пользователя"""
        from Api_Keys.models import Api_key

        return Api_key.objects.filter(user=self).last()

    @property
    def password(self) -> str: 
        return Encryption.decrypt_data(User.objects.get(id=self.id).base_password)
    
    @password.setter
    def password(self, value):
        self.base_password = Encryption.encrypt_data(value)
        self.save()

    def __isStaff(self, value: bool) -> bool:
        isStaff = value

        if isStaff: return True

        count_T = 0

        if self.isModerator: 
            count_T += 1
            isStaff = True
        if self.isAdministrator:  
            count_T += 1
            isStaff = True
        if self.is_superuser: 
            count_T += 1
            isStaff = True

        if value == False:
            if count_T <= 1: isStaff = False
            else: isStaff = True

        return isStaff
    
    @property
    def is_authenticated(self): return True
    
    @property
    def is_anonymous(self): return False

    @property
    def super_user(self) -> bool: return self.is_superuser 

    @super_user.setter
    def super_user(self, value): 
        self.is_superuser = value
        self.is_staff = self.__isStaff(value=value)
        self.save()

    @property
    def is_admin(self) -> bool: return self.isAdministrator 

    @is_admin.setter
    def is_admin(self, value): 
        self.isAdministrator = value
        self.is_staff = self.__isStaff(value=value)
        self.save()

    @property
    def is_moder(self) -> bool: return self.isModerator

    @is_moder.setter
    def is_moder(self, value): 
        self.isModerator = value
        self.is_staff = self.__isStaff(value=value)
        self.save()


    def del_user(self) -> bool: 
        """Метод удаления пользователя, ничего сложного, не имеет никаких проверок"""
        from Api_Keys.models import Api_key

        apis = Api_key.objects.filter(user=self)

        for a in apis:
            a.del_key()

        self.delete()

        return True

    def edit_profile(self, address=None, first_name=None, last_name=None, old_pasword=None, password=None, email=None, phone_number=None) -> bool: 
        """Метод изменения данных пользователя, не имеет никаких проверок, просто изменяет данные"""

        if first_name != None: self.first_name = first_name
        if last_name != None: self.last_name = last_name
        if address != None: self.address = address

        if password != None:
            if old_pasword != None:
                if Encryption.decrypt_data(password) == old_pasword:
                    self.base_password = Encryption.encrypt_data(old_pasword)
                else: return False
            else: return False

        if email != None:
            try: 
                User.objects.get(email=email)
                return False
            except: self.email = email

        if phone_number != None:
            try: 
                User.phone_number.get(phone_number=phone_number)
                return False
            except: self.phone_number = phone_number

        self.save()

        return True

    @staticmethod
    def register_user(login, password, first_name='User'): 
        """Метод для регистрации пользователя, возвращает User или None в зависимости от результата,
        принимает в себя логин, пароль и почту, не имеет никаких проверок"""

        try: 
            User.objects.get(username=login)
            return None
        except: pass

        user = User(
                username = login,
                base_password = Encryption.encrypt_data(password),
                first_name = first_name
            )

        try: user.save()
        except: return None
        
        user = User.objects.last()

        Key_Generator.generate_user_api_key(user=user)

        return user

    @staticmethod
    def login_user_by_password(request, login, password) -> str: 
        """Метод для авторизации пользователя по паролю, возвращает объект JWT Токен или None в зависимости от результата,
        принимает в себя почту и пароль"""

        from Encryption.utils import Encryption
        from BaseSecurity.utils import JWT_auth

        try: 
            user = User.objects.get(username=login)
        except: 
            return None
        
        user_acc_password = Encryption.decrypt_data(user.base_password)

        if user_acc_password != password: return None

        jwt_token = JWT_auth.compile_jwt_token(user) 

        user.last_login = datetime.now().__str__()
        user.save()

        return jwt_token
    
class UserGroup(models.Model): 
    name = models.CharField(max_length=32)
    description = models.TextField(max_length=512)
    permissions = models.TextField(max_length=512, default="0")

    def __str__(self): return self.name

    class Meta:
        verbose_name = 'Группа пользователей'  # Имя модели в единственном числе
        verbose_name_plural = 'Группы пользователей'  # Имя модели во множественном числе

    @property
    def permissions_list(self) -> list:
        return self.permissions.split(",")

    @permissions_list.setter
    def permissions_list(self, value:list):
        return ",".join(value)
    
    @permissions_list.getter
    def permissions_list(self) -> list:
        return self.permissions.split(",")
    
    @staticmethod
    def get_user_groups__id(user):
        """Возвращает список Айдишников групп пользователя"""

        items = UserGroupItem.objects.filter(user=user)
        items__group = [group_obj.group.id for group_obj in items]
        return_list = list()

        for item in items__group:
            if item not in return_list:
                return_list.append(item)

        return return_list
    
    @staticmethod
    def get_user_groups__list(user):
        """Возвращает список Групп групп пользователя"""

        items = UserGroupItem.objects.filter(user=user)
        items__group = [group_obj.group for group_obj in items]
        return_list = list()

        for item in items__group:
            if item not in return_list:
                return_list.append(item)

        return return_list

class UserGroupItem(models.Model):
    group = models.ForeignKey(UserGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_add = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Элемент группы'  # Имя модели в единственном числе
        verbose_name_plural = 'Элементы групп'  # Имя модели во множественном числе