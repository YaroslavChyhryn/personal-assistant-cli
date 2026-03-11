# TODO: implement validation helpers for phone, email, birthday

from collections.abc import Callable
from application import contacts_service



def input_error(func) -> Callable: 
    """decorator function to handle input errors, it wraps the original function and catches exceptions such as 
    ValueError, IndexError, KeyError, and PhoneFormatInvalid, returning appropriate error messages"""


    def inner(*args, **kwargs) -> str:
        """inner function that executes the original function and handles exceptions, 
        it returns error messages based on the type of exception caught"""

        try:
            return func(*args, **kwargs)
        
        except ValueError as e:
            return str(e) if str(e) else "Give me name and phone please."
        
        except IndexError:
            return "Not enough arguments provided. Check: " + contacts_service.get_help()
        
        except KeyError:
            return "Contact not found. Use 'all' to see existing contacts."
        
        except PhoneFormatInvalid as e:
            return str(e)
    
    return inner