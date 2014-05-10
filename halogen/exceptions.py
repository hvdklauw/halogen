"""Halogen exceptions."""

import collections


class ValidationError(Exception):
    """It will be raised when validation will be failed."""

    def __init__(self, errors, attr=None):
        self.attr = attr
        if not isinstance(errors, collections.Iterable):
            self.errors = errors
        else:
            self.errors = [errors]

    def __str__(self):
        return '{}: {}'.format(self.attr, str([e.name for e in self.errors]))
