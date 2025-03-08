from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from Encryption.utils import Encryption
from BaseSecurity.utils import Key_Generator
from datetime import datetime

class UserManager(BaseUserManager):

    def create_user(self, username, password=None):
        user = self.model.register_user(login=username, password=password)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        user = self.create_user(username, password, **extra_fields)
        user.is_superuser = True
        user.get_user_api().name_key = "SuperApiKey"
        return user


class User(AbstractUser):   
    """Модель Пользователя, имеет базовые методы"""

    base_password = models.BinaryField()
    username = models.CharField(max_length=128, unique=True)
    email = models.CharField(null=True, max_length = 64)
    isAdministrator = models.BooleanField(default=False)
    isModerator = models.BooleanField(default=False)
    phone_number = models.CharField(default='', max_length = 18)
    addres = models.TextField(max_length=256)

    UserManager = UserManager

    class Meta:
        verbose_name = 'Пользователь'  # Имя модели в единственном числе
        verbose_name_plural = 'Пользователи'  # Имя модели во множественном числе

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

    def edit_profile(self, addres=None, first_name=None, last_name=None, old_pasword=None, password=None, email=None, phone_number=None) -> bool: 
        """Метод изменения данных пользователя, не имеет никаких проверок, просто изменяет данные"""

        if first_name != None: self.first_name = first_name
        if last_name != None: self.last_name = last_name
        if addres != None: self.addres = addres

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