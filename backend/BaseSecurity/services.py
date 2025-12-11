from rest_framework.response import Response
from django.http import HttpRequest

class SecureResponse(Response):
    
    def __init__(self, request = None, data=None, status=200, headers=None, content_type=None):

        if status != 201 and status != 200:
            if data == None or data == '' or data == ' ' or status == 500:
                data = 'Interal-Api-Error'
            elif status == 400:
                data = {"Bad-Request": data}
            elif status == 403:
                data = {"Permission-Error": data}
            elif status == 403 and not request.user.is_authenticated:
                data = 'Authorizing-Error'
                status = 401

        if request:
            request.log.request_status = status

        self.data = data
        self.status = status

        super().__init__(data=data,
                         status=status,
                         headers=headers,
                         content_type=content_type)

class SessionManager: 

    __instance = None

    def __init__(self, request: HttpRequest): 
        self.request = request

    def __new__(cls, *args, **kwargs):
        if cls.__instance == None:
            cls.__instance = super().__new__(cls)
 
        return cls.__instance

    def __del__(cls, *args, **kwargs):
        cls.__instance = None   
 
        return cls.__instance

    def __is_user(self):
        if self.request.method == "GET":
            if "JWTCloudeToken" in self.request.GET:
                return True, "GET", self.request.GET['JWTCloudeToken']
            
        elif self.request.method == "POST":
            if "JWTCloudeToken" in self.request.POST:
                return True, "POST", self.request.POST['JWTCloudeToken']
            
        if "JWTCloudeToken" in dict(self.request.session.items()):
            return True, "session", self.request.session['JWTCloudeToken']

        return False, None, None
    
    def auth__session(self) -> bool:
        is_jwt, jwt_path, jwt_token = self.__is_user()

        if is_jwt and jwt_path != "session": 
            self.request.session['JWTCloudeToken'] = jwt_token
        else: return False

        return True
    
    def auth__user(self, user) -> bool:
        self.request.user = user
        
        return True
    
    def auth__token(self, token: str | None):
        self.request.token = token
        
        return True

    
    def get_request(self) -> HttpRequest: return self.request
            
        