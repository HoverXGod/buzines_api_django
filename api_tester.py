import requests
from random import choice
from time import time
from multiprocessing import Process

def test():
    web_app_host = 'http://localhost:8000/api'

    text = 'w,8,g,h,m,c,g,o,e,g,x,h,q,8,o,e,q,f,9,4,3,f,m,q,i,d,f,s,u,x,q,3,4,f,u,i,s,f,x,m,n,q,i,o,3,4,x,i,s,f,q,p,9,o,z,q,w,q,e,i,u,r,h,c,n,q,w,r,i,u,q,w,,e,y,w,e,u,q,y,i,q,z,q,z,f,i,u,y,q,w,e,g,r'
    text_list = text.split(",")
    product_list = [1,2]
    for x in range (1000):

        index = "".join([choice(text_list) for item in range(20)])

        t = time()

        login_data = {
            'login': f'testnikita_krasotkin{index}',
            'password': 'nikitak12r@',
            'email': f'testtestapi{index}@api.test'
        }

        requests.post(f"{web_app_host}/user/register", params=login_data)

        answer = requests.get(f"{web_app_host}/user/login", params=login_data)
        auth_header = {
            "JWTCloudeToken": answer.json()['JWTCloudeToken']
        }

        for y in range(5):

            for x in range(7):

                requests.get(f"{web_app_host}/product/get_product", headers=auth_header, params={
                    'product_id': choice(product_list)
                }) 

                requests.get(f"{web_app_host}/product/add_product_in_cart", headers=auth_header, params={
                    'product_id': choice(product_list)
                }) 

            requests.get(f"{web_app_host}/product/get_user_cart", headers=auth_header) 

            answer = requests.get(f"{web_app_host}/order/start_order", headers=auth_header, params={
                'method_name': 'YouKassa' 
            })

        print(answer.json()['id'])
        print(time() - t)

if __name__ == '__main__':
    Process(target=test).start()
    Process(target=test).start()
    Process(target=test).start()
    Process(target=test).start()