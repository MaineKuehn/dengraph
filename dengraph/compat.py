"""
Compatibility for different python versions
"""
# pylint: disable=invalid-name,undefined-variable,redefined-builtin
from __future__ import absolute_import
import sys
import abc as _abc

#: python version this module has been finalized for
compat_version = sys.version_info

try:
    import collections.abc as collections_abc
except ImportError:
    import collections as collections_abc

try:
    ABCBase = _abc.ABC
except AttributeError:
    try:
        from .compat3 import ABCBase
    except SyntaxError:
        class ABCBase(object):
            """
            Helper class that provides a standard way to create an ABC using inheritance.

            A helper class that has :class:`ABCMeta` as its metaclass.  With this class,
            an abstract base class can be created by simply deriving from :class:`ABC`,
            avoiding sometimes confusing metaclass usage.

            Note that the type of :class:`ABC` is still :class:`ABCMeta`, therefore
            inheriting from :class:`ABC` requires the usual precautions regarding metaclass
            usage, as multiple inheritance may lead to metaclass conflicts.

            .. versionadded:: 3.4

            .. versionchanged:: 3.3
               Subclasses can use :py:meth:`register` as a Decorator.
            """
            __metaclass__ = _abc.ABCMeta

            @classmethod
            def register(cls, subclass):
                """
                Register *subclass* as a "virtual subclass" of this ABC.

                .. versionchanged:: 3.3
                   Returns the registered subclass, to allow usage as a class decorator.
                """
                cls.__metaclass__.register(cls, subclass)
                return cls


if sys.version_info < (3, 3):
    import backports.range  # py2.X requires range backport
    range = backports.range.range
else:
    import builtins
    range = builtins.range


def viewkeys(mapping):
    """
    Get a key view to a mapping

    :type mapping: dict
    """
    try:
        return mapping.viewkeys()
    except AttributeError:
        return mapping.keys()


def viewvalues(mapping):
    """
    Get a value view to a mapping

    :type mapping: dict
    """
    try:
        return mapping.viewvalues()
    except AttributeError:
        return mapping.values()


def viewitems(mapping):
    """
    Get an item view to a mapping

    :type mapping: dict
    """
    try:
        return mapping.viewitems()
    except AttributeError:
        return mapping.items()


# limit names we export to not expose implementation details
__all__ = [
    'compat_version',
    'collections_abc', 'ABCBase',
    'range',
    'viewkeys', 'viewvalues', 'viewitems',
]