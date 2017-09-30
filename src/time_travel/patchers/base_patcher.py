"""Base class for patching time modules."""


import mock


class BasePatcher(object):
    """Base class for patching time modules."""
    
    def __init__(self,
                 clock,
                 events_pool=None,
                 modules_to_patch=None,
                 **kwargs):
        """Create the patch."""
        self.clock = clock
        self.events_pool = events_pool
        
        if modules_to_patch is None:
            self.modules_to_patch = []
        elif isinstance(modules_to_patch, (list, tuple)):
            self.modules_to_patch = modules_to_patch
        else:
            self.modules_to_patch = [modules_to_patch]
        
    def get_patches_list(self, target, new):
        """Return a list of patches for each module to patch."""
        if self.modules_to_patch:
            return [mock.patch('.'.join([module, target]), new) for module in
                    self.modules_to_patch]
        else:
            return [mock.patch(target, new)]
        
    @classmethod
    def get_events_namespace(cls):
        """Return the namespace of the patcher's events."""
        return None
    
    @classmethod
    def get_events_types(cls):
        """Return Enum of the patcher's events types."""
        return None
    
    def get_patches(self):
        """Return generator containing all patches to do."""
        return None
                
    def start(self):
        """Start mocking datetime module."""
        self.patches = []
        for target, new in self.get_patches():
            self.patches += self.get_patches_list(target, new)
            
        for p in self.patches:
            p.start()
            
    def stop(self):
        """Stop mocking datetime module."""
        for p in self.patches:
            p.stop()
