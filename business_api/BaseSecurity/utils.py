from Encryption.utils import Encryption

class Key_Generator:

    @staticmethod
    def generate_base_api_key():
        """Генерирует апи ключ для пользователя"""
        from Encryption.utils import Encryption
        return Encryption.fernet.generate_key().decode()

    @staticmethod
    def generate_user_api_key(user, help_text='UserApiKey', key_name='API_KEY'):
        """Создает апи ключ для пользователя"""
        from Api_Keys.models import Api_key
        from datetime import datetime
        
        Key = Key_Generator.generate_base_api_key()
        current_date = datetime.now().date().__str__()

        Api_Key = Api_key(
            key_name = key_name,
            key_value = Key,
            user = user,
            help_text = help_text,
            is_active = True,
            created_at = current_date,
            updated_at = current_date
        )

        Api_Key.save()

        return Api_key
    
    
class JWT_auth:
    
    @staticmethod
    def compile_jwt_form(User) -> str:
        from datetime import datetime
        """Компиляция JWT формы, это не зашифрованная версия токена без подписи"""

        name = User.username + ";"
        password = User.base_password.decode() + ";"
        user_id = str(User.pk) + ";"
        date = datetime.now().__str__() + ";"
        
        roles_string = ""
        if User.is_superuser:
            roles_string += "super;"
        if User.isAdministrator:
            roles_string += "admin;"
        if User.isModerator:
            roles_string += "moder;"

        jwt_form = user_id + name + password + roles_string + date
        
        return jwt_form
    
    @staticmethod
    def compile_jwt_token(User) -> str: 
        """Компиляция JWT Токена"""

        sign = Encryption.sign
        return Encryption.encrypt_data(JWT_auth.compile_jwt_form(User).encode()+sign).decode()

    @staticmethod
    def _decompile_jwt_token_str(jwt_token: str) -> str: 
        """Декомпиляция JWT Токена в виде строки"""

        return Encryption.decrypt_data(jwt_token.encode())
    
    @staticmethod
    def _decompile_jwt_token_list(jwt_token: str) -> list: 
        """Декомпиляция JWT Токена в виде строки"""

        return JWT_auth._decompile_jwt_token_str(jwt_token).split(";")

    @staticmethod
    def verify_jwt_token(jwt_token: str) -> bool: 
        """Проверка соответсвия подписи нашей"""

        baseJWT = JWT_auth._decompile_jwt_token_str(jwt_token).split(";")
        return baseJWT[::-1][0] == Encryption.sign.decode()
    
    @staticmethod
    def get_user_permissions(jwt_token: str) -> list:
        """Получаем права пользователя из JWT Токена"""

        jwt_list = JWT_auth._decompile_jwt_token_list(jwt_token=jwt_token)
        permission_list = []

        for j in jwt_list:
            if j == "super": permission_list.append("super")
            elif j == "moder": permission_list.append("moder")
            elif j == "admin": permission_list.append("admin")

        return permission_list
    
    @staticmethod
    def verify_super_jwt(jwt_token: str) -> bool:
        """Проверям сходство пользователя с базой данных"""
        
        from User.models import User

        jwt_list = JWT_auth._decompile_jwt_token_list(jwt_token=jwt_token)
        user_id = jwt_list[0]
        user = User.objects.get(id=user_id)

        jwt_form = JWT_auth.compile_jwt_form(user).split(";")[:-2]
        jwt_list = jwt_list[:-2]

        if len(jwt_list) != len(jwt_form): return False

        count_form = len(jwt_form)
        count_jwt_accept = 0

        for j in jwt_form:
            if j in jwt_list: 
                count_jwt_accept += 1

        return count_jwt_accept == count_form
    
    @staticmethod
    def jwt_to_user(jwt_token):
        """По JWT токену ищет пользователя в базе данных и возваращет его"""
        from User.models import User

        jwt = JWT_auth._decompile_jwt_token_list(jwt_token=jwt_token)
        user_id = jwt[0]

        user = None

        try:
            user = User.objects.get(id=user_id)
        except: pass

        return user

    @staticmethod 
    def get_jwt(request) -> str:
        """Получение JWT или JAT токена из request"""


        try: return request.session['JsonWebToken']
        except:
            try: return request.GET['JsonWebToken']
            except: 
                try:
                    from Api_Keys.utils import ApiManager
                    return ApiManager.get_api_key(api_key=request.GET['api_key'])._generate_jat()
                except: return None

    @staticmethod 
    def get_jwt_super(request) -> str:
        """Получение JWT super или JAT super токена из request"""

        try:
            return request.session['JsonWebToken']
        except:
            try: 
                return request.GET['JsonWebToken']
            except: 
                try:
                    from Api_Keys.utils import ApiManager
                    return ApiManager.get_super_api_key(api_key=request.GET['api_key'])._generate_jat()
                except: return None
