class BaseMethod:

    name = "BaseMethod"
    id = None

    def __init__(self, id=None): pass
    
    def create_payment(self, products, cost, request): return

    def check_status(self): return
    
    def cancel_payment(self): return

class YouKassa(BaseMethod): pass

def get_method(method_name, id=None):
    if method_name == "youkassa": return YouKassa(id)
