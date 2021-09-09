from .WorkBook import UPWorkBook

def load(excel_path: str, mode: str = 'a') -> UPWorkBook:
    return UPWorkBook(excel_path, mode)
