import mock

class Patcher(object):
    
    def __enter__(self):
        self.patcher = mock.patch('module_a.foo',
                                  mock.Mock(return_value=15))
        
        self.patcher.start()
        
    def __exit__(self, *args):
        self.patcher.stop()
