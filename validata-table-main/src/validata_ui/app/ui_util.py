"""Util UI functions."""
import threading

from flask import flash


def flash_error(msg):
    """Flash bootstrap error message."""
    flash(msg, "danger")


def flash_warning(msg):
    """Flash bootstrap warning message."""
    flash(msg, "warning")


def flash_success(msg):
    """Flash bootstrap success message."""
    flash(msg, "success")


def flash_info(msg):
    """Flash bootstrap info message."""
    flash(msg, "info")


class ThreadUpdater:
    """Fire last known value and update on background."""

    def __init__(self, func):
        # First time run to get an initial value
        self.val = func()

        self.func = func
        self.thread = None

    @property
    def value(self):
        self._background_update()
        return self.val

    def _background_update(self):
        # Don't run if an update is already running
        if self.thread is not None:
            return

        # Run func to update self.val and reset self.thread
        # to show that background update is done.
        def doIt():
            self.val = self.func()
            self.thread = None

        # Init and start thread
        self.thread = threading.Thread(target=doIt)
        self.thread.start()
