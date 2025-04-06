from rest_framework.views import APIView
from BaseSecurity.permissions import isSuperUser
from BaseSecurity.services import SecureResponse
from Content.serializers import PageTextSerializers
from Content.models import PageText
from Content.services import ImagesManager


class CreatePageText(APIView): 

    serializer_class = PageTextSerializers    
    permission_classes = [isSuperUser]

    def get(self, request):
        page_name = request.GET['page_name']
        text = request.GET['text']
        index = request.GET['index']

        text = PageText.create_page_text(text=text, page_name=page_name, index=index)

        if text != None: return SecureResponse(request=request, data=self.serializer_class(instance=text).data, status=200)
        else: return SecureResponse(request=request, data='', status=400) 

class UpdatePageText(APIView): 
    
    serializer_class = PageTextSerializers    
    permission_classes = [isSuperUser]

    def get(self, request):
        page_name = request.GET['page_name']
        text = request.GET['text']
        index = request.GET['index']

        text = PageText.update_page_text(text=text, page_name=page_name, index=index)

        if text != None: return SecureResponse(request=request, data=self.serializer_class(instance=text).data, status=200)
        else: return SecureResponse(request=request, data='', status=400) 

class GetPageTexts(APIView): 
    
    serializer_class = PageTextSerializers    
    permission_classes = [isSuperUser]

    def get(self, request): 
        page_name = request.GET['page_name']
        
        texts = PageText.get_page_texts(page_name=page_name)

        if texts != None: return SecureResponse(request=request, data=self.serializer_class(instance=texts, many=True).data, status=200)
        else: return SecureResponse(request=request, data='', status=400) 

class DeletePageText(APIView): 
    
    serializer_class = PageTextSerializers    
    permission_classes = [isSuperUser]

    def get(self, request):
        page_name = request.GET['page_name']
        index = request.GET['index']

        text = PageText.delete_page_text(index=index, page_name=page_name)

        if text != None: return SecureResponse(request=request, data=self.serializer_class(instance=text).data, status=200)
        else: return SecureResponse(request=request, data='', status=400) 

class DeletePageTexts(APIView): 
    
    serializer_class = PageTextSerializers    
    permission_classes = [isSuperUser]

    def get(self, request):
        page_name = request.GET['page_name']
        
        texts = PageText.delete_page(page_name=page_name)

        if texts != None: return SecureResponse(request=request, data=self.serializer_class(instance=texts, many=True).data, status=200)
        else: return SecureResponse(request=request, data='', status=400) 

class AddImage(APIView): 
       
    permission_classes = [isSuperUser]

    def get(self, request):
        ImagesManager.load_img(request=request)

        return SecureResponse(request=request, status=200) 
    
class DelImage(APIView): 
       
    permission_classes = [isSuperUser]

    def get(self, request):
        try:
            ImagesManager.del_img(request=request)
        except:  return SecureResponse(request=request, status=404) 

        return SecureResponse(request=request, status=200) 