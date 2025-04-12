from multiprocessing import Process
from functools import wraps

def context_process(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        def target():
            return func(*args, **kwargs)
        
        process = Process(
            target=target
        )

        process.start()

        return process
    
    return wrapper


