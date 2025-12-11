from rest_framework.views import APIView
from .utils import db_exists
from BaseSecurity.services import SecureResponse

class DataBaseReady(APIView):

    permission_classes = []

    def post(self, request):
        db_name = request.POST.get("db_name", None)
        if db_name:
            if db_exists(db_name):
                return SecureResponse(request=request, data=f"{db_name}: 200", status=201)
            else:
                return SecureResponse(request=request, data=f"{db_name}: 500", status=201)
        else:
            return SecureResponse(request=request, status=500)