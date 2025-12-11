from Encryption.utils import Encryption

class ApiManager:

    @staticmethod
    def get_api_key(api_key) -> any:
        """Получение\поиск api ключа"""

        keys = Api_key.objects.all()

        for key in keys:
            if api_key == Encryption.decrypt_data(key.key_value): 
                return key 
        
        return None
    
    @staticmethod
    def get_super_api_key(api_key) -> any:
        """Получение\поиск Super Api ключа"""
        from .models import Api_key

        keys = Api_key.objects.filter(key_name="SuperApiKey")

        for key in keys:
            if api_key == Encryption.decrypt_data(key.key_value): 
                return key 
        
        return None
    
    @staticmethod
    def get_jat_from_key(api_key) -> str:
        """Получение\поиск JAT токена из api ключа"""
        from .models import Api_key

        keys = Api_key.objects.all()

        for key in keys:
            if api_key == Encryption.decrypt_data(key.key_value): 
                return key._generate_jat()
        
        return None
        