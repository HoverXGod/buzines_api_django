from random import choice

def gen_id():
    chars = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'T', 'Y']
    nums = [str(x + 1) for x in range(9)]

    chars = [chars, nums]

    id = str()

    for y in range(4):
        for x in range(4): id += choice(choice(chars))
        id += "-"

    return id


class BaseMethod:

    name = "Base"

    def __init__(self, id=None): 
        self.id = id
    
    def create_payment(self, *args, **kwargs): 
        self.id = gen_id()

    def check_status(self): return "completed"
    
    def cancel_payment(self): return

class YouKassa(BaseMethod): 
    
    name = 'YouKassa'

def get_method(method_name, id=None):
    if method_name == "Base": 
        return BaseMethod(id)
    if method_name == "YouKassa": 
        return YouKassa(id)
