"""Test the wait_and_respond function."""

import mock
import pytest

from time_travel import TimeTravel

from .wait_and_respond import wait_and_respond


def test_basic_behaviour():
    with TimeTravel() as t:
        socket = mock.MagicMock()

        t.add_future_event(2, socket, t.event_types.select.READ)
        t.add_future_event(3, socket, t.event_types.select.WRITE)

        wait_and_respond(socket)

        from datetime import datetime
        socket.send.assert_called_once_with(
            str(datetime.fromtimestamp(t.clock.time)))


def test_really_long_wait():
    with TimeTravel() as t:
        socket = mock.MagicMock()

        t.add_future_event(49 * 60, socket, t.event_types.select.READ)
        t.add_future_event(49 * 60 + 2, socket, t.event_types.select.WRITE)

        wait_and_respond(socket)

        from datetime import datetime
        socket.send.assert_called_once_with(
            str(datetime.fromtimestamp(t.clock.time)))


def test_wait_timeout():
    with TimeTravel() as t:
        socket = mock.MagicMock()

        t.add_future_event(50 * 60 + 1, socket, t.event_types.select.READ)

        with pytest.raises(ValueError):
            wait_and_respond(socket)
