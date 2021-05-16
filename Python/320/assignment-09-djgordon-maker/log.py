'''
Captures fatal errors for a given logger
'''


def logit(logger):
    '''
    Decorator
    '''
    def new_func(func):
        '''
        Modified function returned by decorator
        '''
        def wrapper(*args, **kwargs):
            '''
            Error captureing function
            '''
            try:
                return func(*args, **kwargs)
            except Exception as error:
                logger.exception(f'Error ocured within {func.__name__}\n')
                raise error
        return wrapper
    return new_func
