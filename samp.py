
class sample():
    def __init__(self):
        '''
        main use is to keep track of sample measurements and current sample id
        '''
        
        self.id:str = ""
        
        self.insts = {
            'fourpp': False,
            "nearir": False,
            "rdt": False,
            "hall": False,
        }
        self.test = False

    def check(self) -> bool:
        if self.test: return True
        
        
        for key in self.insts.keys():
            if not self.insts[key]:
                return False
        return True
    
    
    
if __name__ == "__main__":
    samp1 = sample()
    samp2 = sample()
    
    samp1.id = "123"
    samp2.id = "456"
    
    print(samp1.id)
    print(samp2.id) 
    
    samps = [samp1, samp2]
    
    for samp in samps:
        samp.id = "1"
    print(samps[0].id)