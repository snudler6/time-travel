"""Base class for patching time and I/O modules."""

import sys
import inspect


class BasePatcher(object):
    """Base class for patching time and I/O modules."""

    # These modules will not be patched by default, unless explicitly specified
    # in `modules_to_patch`.
    # This is done to prevent time-travel from interfering with the timing of
    # the actual test environment.
    UNPATCHED_MODULES = ['pytest', '_pytest', 'unittest', 'mock', 'threading']

    def __init__(self,
                 clock,
                 event_pool,
                 modules_to_patch=None,
                 patcher_module=None):
        """Create the patch."""
        self.clock = clock
        self.event_pool = event_pool

        if modules_to_patch is None:
            self.modules_to_patch = []
        elif isinstance(modules_to_patch, (list, tuple)):
            self.modules_to_patch = modules_to_patch
        else:
            self.modules_to_patch = [modules_to_patch]

        self.patcher_module = patcher_module if patcher_module else None
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
        """Return the actual module obect to be patched."""
        raise NotImplementedError()

    def get_patch_actions(self):
        """Return list of the patches to do.

        The list structure is tuples containing:
            (real_object_name,
             the_real_object,
             fake_object)
        """
        raise NotImplementedError()

    def start(self):
        """Start the patcher.

        The logic to the patchers start is based on the work done by:
        spulec/freezegun
        under
        https://github.com/spulec/freezegun

        Copyright (C) 2017 spulec/freezegun

        Licensed under the Apache License, Version 2.0 (the "License"); you may
        not use this file except in compliance with the License. You may obtain
        a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

        Unless required by applicable law or agreed to in writing,
        software distributed under the License is distributed on an
        "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
        KIND, either express or implied.  See the License for the
        specific language governing permissions and limitations
        under the License.

        Modifications:

        Modifications to the file was to leave the inner change of the loaded
        modules and removing any other related logic to a specific module.
        """
        patch_actions = self.get_patch_actions()

        real_id_to_fake = {id(real): fake for _, real, fake in patch_actions}

        patched_module = self.get_patched_module()

        # Change modules for later imports.
        for obj_name, real_obj, fake_obj in patch_actions:
            self._save_for_undo(patched_module, obj_name, real_obj)
            setattr(patched_module, obj_name, fake_obj)

        if self.modules_to_patch:
            # If only a given list of modules is required to be patched
            modules = [sys.modules[name] for name in self.modules_to_patch]
        else:
            # not given a specific module to patch on.
            # Create the list of all modules to search for the patched objects.
            # Patch on all loaded modules.
            modules = [
                module for mod_name, module in sys.modules.items() if
                (inspect.ismodule(module)
                 and hasattr(module, '__name__')
                 # Don't patch inside the original module, this (the patcher)
                 # module, or the unpatched modules.
                 and module.__name__ not in ([patched_module,
                                              self.patcher_module,
                                              __name__]
                                             + self.UNPATCHED_MODULES
                                             )
                 )
            ]

        # Search in all modules for the object to patch.
        for module in modules:
            for attr in dir(module):
                try:
                    # Get any attribute loaded on the module.
                    attribute_value = getattr(module, attr)
                except (ValueError, AttributeError, ImportError):
                    # For some libraries, this happen.
                    # e.g. attr=dbm_gnu, module=pkg_resources._vendor.six.moves
                    continue

                # If the attribute is on this module - avoid recursion.
                # Do stuff only if the attribute is the object to patch.
                if id(attribute_value) not in real_id_to_fake.keys():
                    continue

                # Find the relative mock object for the original class.
                fake_obj = real_id_to_fake.get(id(attribute_value))
                # Change the class to the mocked one in the given module.
                setattr(module, attr, fake_obj)
                # Save the original class for later - when stopping the patch.
                self._save_for_undo(module, attr, attribute_value)

    def stop(self):
        """Stop the patching."""
        for module, attribute, original_value in self._undo_set:
            setattr(module, attribute, original_value)

        self._undo_set.clear()

    def _save_for_undo(self, module, attribute, original_value):
        self._undo_set.add((module, attribute, original_value))
