"""A patch to the select.epoll object."""

from .poll_patcher import PollPatcher

import select as select_lib


class EpollPatcher(PollPatcher):
    """Patcher for select.epoll."""

    def get_patch_actions(self):
        """Return generator containing all patches to do."""
        return [('epoll', select_lib.epoll, self._mock_poll)]
