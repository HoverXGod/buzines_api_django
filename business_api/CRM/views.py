from rest_framework.views import APIView
from BaseSecurity.permissions import isSuperUser
from BaseSecurity.services import SecureResponse
from Content.serializers import PageTextSerializers
from Content.models import PageText


class CreatePageText(APIView): pass

class UpdatePageText(APIView): pass

class GetPageText(APIView): pass

class GetPageTexts(APIView): pass
