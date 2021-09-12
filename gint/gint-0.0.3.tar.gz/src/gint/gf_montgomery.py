def GF(p):
    if p == (1<<(p.bit_length()-1)):
        return GF_all_2(p)
    if p&1:
        return GF_no_2(p)
    else:
        raise ValueError("Gallois field not implemented for this number")

class gint_all_2:
    pass
    
class GF_all_2:
    def __init__(p):
        if p != (1<<(p.bit_length()-1)):
            raise ValueError("p must be power of 2")
        self.p = p

    

