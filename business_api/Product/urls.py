from django.urls import path
from .views import *

urlpatterns = [
    path('api/product/get_products_category', GetProductsCategory.as_view()), 
    path('api/product/get_all_products', GetAllProducts.as_view()), 
    path('api/product/get_product', GetProduct.as_view()), 
    path('api/product/edit_product', UpdateProduct.as_view()), 
    path('api/product/create_promotion', CreateProduct.as_view()), 
    path('api/product/add_image_product', AddImageProduct.as_view()), 
    path('api/product/create_category', CreateCategory.as_view()), 
    path('api/product/edit_category', UpdateCategory.as_view()), 
    path('api/product/add_image_category', AddImageCategory.as_view()), 
    path('api/product/get_all_categorys', GetAllCategorys.as_view()), 
    path('api/product/create_promotion', CreatePromotion.as_view()), 
    path('api/product/create_personal_discount', CreatePersonalDiscount.as_view()), 
    path('api/product/create_prmotion', CreatePromocode.as_view()), 
    path('api/product/add_product_in_cart', AddProductInCart.as_view()), 
    path('api/product/get_all_promotions', GetAllPromotions.as_view()), 
    path('api/product/get_personal_discount', GetPersonalDiscount.as_view()), 
    path('api/product/get_user_cart', GetUserCart.as_view()), 
    path('api/product/delete_personal_discount', DeletePersonalDiscount.as_view()), 
    path('api/product/delete_promocode', DeletePromocde.as_view()), 
    path('api/product/delete_promotion', DeletePromotion.as_view()), 
    path('api/product/remove_product_in_cart', RemoveProductInUserCart.as_view()), 
    path('api/product/remove_user_cart', RemoveUserCart.as_view()), 

]