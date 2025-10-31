from threading import Thread
from functools import wraps

def context_thread(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        
        thread = Thread(
            target=func,
            args=args,
            kwargs=kwargs
        )

        thread.start()

        return thread
    
    return wrapper

