#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `asynciotimemachine` package."""

from asyncio import new_event_loop

import pytest

from asynciotimemachine import TimeMachine


class TestTimeMachine:
    """Tests for `TimeMachine`."""

    @pytest.fixture
    def event_loop(self):
        loop = new_event_loop()
        try:
            yield loop
        finally:
            loop.close()

    @pytest.fixture
    def time_machine(self, event_loop):
        """Return the time machine fixture."""
        return TimeMachine(event_loop=event_loop)

    @pytest.mark.parametrize('amount', [0, 0.1, 1, 60, 3600, 86400])
    def test_advance_by(self, time_machine, event_loop, amount):
        """Test `TimeMachine.advance_by()` fast-forwards timestamp."""
        time1 = event_loop.time()
        time_machine.advance_by(amount)
        time2 = event_loop.time()
        assert time2 - time1 == pytest.approx(amount, abs=0.01)

    @pytest.mark.parametrize('amount', [0.1, 1, 60, 3600, 86400])
    def test_advance_to(self, time_machine, event_loop, amount):
        """Test `TimeMachine.advance_to()` fast-forwards timestamp."""
        time1 = event_loop.time()
        time_machine.advance_to(time1 + amount)
        time2 = event_loop.time()
        assert time2 - time1 == pytest.approx(amount, abs=0.01)

    @pytest.mark.parametrize('amount', [-0.1, -1, -60, -3600, -86400])
    def test_advance_by_backward(self, time_machine, amount):
        """Test ``advance_by()`` raises `ValueError` for backward amount."""
        with pytest.raises(ValueError):
            time_machine.advance_by(amount)

    @pytest.mark.parametrize('amount', [-0.1, -1, -60, -3600, -86400])
    def test_advance_to_past(self, time_machine, event_loop, amount):
        """Test ``advance_to()`` raises `ValueError` for travel into past."""
        with pytest.raises(ValueError):
            time_machine.advance_to(event_loop.time() + amount)
