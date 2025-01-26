from django.http import HttpRequest

class ImagesManager: 
    
    @staticmethod
    def load_img(request: HttpRequest): 
        img = request.GET['image']
        img_path = str()
        return img_path

    @staticmethod
    def del_img(request: HttpRequest): 
        image_name = request.GET['image_name']