from rest_framework.response import Response

class SecureResponse(Response):
    
    def __init__(self, request, data=None, status=201, headers=None, content_type=None):

        if status != 201 and status != 200:
            if data == None or data == '' or data == ' ':
                data = 'ÍnteralApiError'
            elif status == 400:
                data = {"BadRequest": data}
            elif status == 403:
                data = {"PermissionError": data}
            elif status == 403 and not request.user.is_authenticated:
                data = 'User is not autorized'
                status = 401

        request.log.request_status = status

        return super().__init__(data=data, status=status, headers=headers, content_type=content_type)

class SessionManager: pass

    