from django.core.files.storage import default_storage

class ImagesManager: 

    @staticmethod 
    def get_objects_images(images):
        return images.split(",")
    
    def set_objects_images(images):
        return ",".join(images)
    
    @staticmethod
    def load_img(request): 
        img = request.FILES['image']

        file_path = default_storage.save(f'images/{img.name}', img)

        return f'images/{img.name}'
    
    @staticmethod
    def get_all_images(request): 
        folder, files = default_storage.listdir('images/')
        return files

    @staticmethod
    def get_image(request, file_name): 
        with default_storage.open(f'images/{file_name}', 'rb') as f:
            return f

    @staticmethod
    def del_img(request): 
        file_name = request.DELETE['image_name']
        default_storage.open(f'images/{file_name}', 'rb')