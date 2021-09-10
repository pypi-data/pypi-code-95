__all__ = ['AistaError']


class AistaError(Exception):
    
    def __init__(self, cls_name, method_name):
        super().__init__(f'Cannot create class {cls_name}. Please implement the {method_name} method.')
