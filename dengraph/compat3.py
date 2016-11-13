"""
Compatibility for different python versions using python 3 syntax
"""
# pylint: disable=invalid-name,undefined-variable,redefined-builtin
import abc as _abc


try:
    ABCBase = _abc.ABC
except AttributeError:
    class ABCBase(metaclass=_abc.ABCMeta):
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

        @classmethod
        def register(cls, subclass):
            """
            Register *subclass* as a "virtual subclass" of this ABC.

            .. versionchanged:: 3.3
               Returns the registered subclass, to allow usage as a class decorator.
            """
            cls.__class__.register(cls, subclass)
            return cls
