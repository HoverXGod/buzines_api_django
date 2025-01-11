from rest_framework.response import Response


class SecureResponse(Response):
    
    def __init__(self, request, data=None, status=201, headers=None, content_type=None):

        request.log.request_status = status
        return super().__init__(data=data, status=status, headers=headers, content_type=content_type)

    