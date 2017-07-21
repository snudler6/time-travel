"""Base class for patching time modules."""


class BasicPatcher(object):
    """Base class for patching time modules."""
    
    def __init__(self, clock, events_pool=None):
        """Create the patch."""
        self.clock = clock
        self.events_pool = events_pool
        
        self.patches = []
                

        
    def start(self):
        """Start mocking datetime module."""
        for p in self.patches:
            p.start()
            
    def stop(self):
        """Stop mocking datetime module."""
        for p in self.patches:
                p.stop()
