"""Base class for patching time modules."""

import sys
import mock
import importlib


class BasePatcher(object):
    """Base class for patching time modules."""
    
    def __init__(self,
                 clock,
                 events_pool=None,
                 modules_to_patch=None,
                 patcher_module=None):
        """Create the patch."""
        self.clock = clock
        self.events_pool = events_pool
        
        if modules_to_patch is None:
            self.modules_to_patch = []
        elif isinstance(modules_to_patch, (list, tuple)):
            self.modules_to_patch = modules_to_patch
        else:
            self.modules_to_patch = [modules_to_patch]
            
        self.patcher_module = importlib.import_module(patcher_module) if\
            patcher_module else None
        self._undo_set = set()
        
    @classmethod
    def get_events_namespace(cls):
        """Return the namespace of the patcher's events."""
        return None
    
    @classmethod
    def get_events_types(cls):
        """Return Enum of the patcher's events types."""
        return None
    
    def get_patched_module(self):
        """Do more stuff."""
        raise NotImplementedError()
        
    def get_patch_actions(self):
        """Do stuff."""
        raise NotImplementedError()
        
    def start_extra_actions(self):
        """Extra actions when starting the patcher."""
        pass
        
    def stop_extra_actions(self):
        """Extra actions when stoping the patcher."""
        pass
    
    def start(self):
        """Start the patcher."""
        patch_actions = list(self.get_patch_actions())
        
        local_names = [local_name for _, local_name, _, _ in patch_actions]
        real_id_to_fake = {id(real): fake for _, _, real, fake in
                           patch_actions}
        
        patched_module = self.get_patched_module()
        for real_name, _, real_attr, fake_attr in patch_actions:
            self._save_for_undo(patched_module, real_name, real_attr)
            setattr(patched_module, real_name, fake_attr)
            
        self.start_extra_actions()

        # Create the list of all modules to search for datetime and date
        # classes.
        if self.modules_to_patch:
            # If only a given list of modules is required to be patched
            modules = [sys.modules[name] for name in self.modules_to_patch] 
        else:
            # Patch on all loaded modules
            modules = [
                module for mod_name, module in sys.modules.items() if
                mod_name is not None and
                module is not None and
                hasattr(module, '__name__') and
                # Don't patch inside this module,
                # or inside the original module.
                module.__name__ not in ([patched_module, self.patcher_module,
                                         __name__]) 
            ]
        
        for module in modules:
            for attr in dir(module):
                try:
                    # Get any attribute loaded on the module.
                    attribute_value = getattr(module, attr)
                except (ValueError, AttributeError, ImportError):
                    # For some libraries, this happen.
                    continue
                
                # If the attribute is on this module - avoid recursion.
                # Do stuff only if the attribute is datetime or date classes.
                if id(attribute_value) not in real_id_to_fake.keys():
                    continue
                    
                # Find the relative mock object for the original class.
                fake = real_id_to_fake.get(id(attribute_value))
                # Change the class to the mocked one in the given module.
                setattr(module, attr, fake)
                # Save the original class for later - when stopping the patch.
                self._save_for_undo(module, attr, attribute_value)
                
    def stop(self):
        """Stop the patching of datetime module."""
        for module, attribute, original_value in self._undo_set:
            setattr(module, attribute, original_value)
            
        self._undo_set.clear()
        
        self.stop_extra_actions()
                
    def _save_for_undo(self, module, attribute, original_value):
        self._undo_set.add((module, attribute, original_value))
