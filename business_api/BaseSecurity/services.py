from rest_framework.response import Response


class SecureResponse(Response):
    
    def __init__(self, request, data=None, status=201, headers=None, content_type=None):

        request.log.request_status = status

        if status != 201 and status != 200:
            if data == None:
                data = 'ÍnteralApiError'

        return super().__init__(data=data, status=status, headers=headers, content_type=content_type)

    