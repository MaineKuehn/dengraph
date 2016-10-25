"""
Compatibility for different python versions
"""
# pylint: disable=invalid-name,undefined-variable
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
        """
        __metaclass__ = _abc.ABCMeta

# limit names we export to not expose implementation details
__all__ = [
    'compat_version',
    'collections_abc', 'ABCBase'
]