""""""
class time_module_patcher(object):
    
    def __init__(self, start_time=0):
        self.time = start_time
        
    def start(self):
        raise NotImplementedError()
    