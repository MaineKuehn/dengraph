from __future__ import absolute_import

import dengraph.compat


class NoDistanceSupport(Exception):
    pass


class Distance(dengraph.compat.ABCBase):
    """
    A distance provides the interface for calculation on arbitrary *node* objects.

    All implementations of this ABC guarantee the following operators:

    .. describe:: __call__(first, second, *[, default])

       Return the distance between node representations *x* and *y*.

       There is one optional keyword-only argument. The *default* argument specifies a distance
       to return if the distance for the given objects can not be determined. If the distance can
       not be returned and *default* is not provided, a :exc:`ValueError` is raised.

    .. function:: mean(iterable, *[, default])
                  mean(arg1, arg2, *args[, default])

       Return the mean representation of an iterable or the mean representation of two or more
       arguments.

       If one positional argument is provided, it should be an :term:`iterable`.
       The mean representation based on the given node representation is returned. If two or more
       positional arguments are provided, the mean representation of the given nodes is returned.

       There is one optional keyword-only argument. The *default* argument specifies a mean
       representation to return if the provided iterable is empty. If the iterable is empty and
       *default* is not provided, a :exc:`ValueError` is raised.

       Return the mean node representation between node representations `a` and `b`, if any.

    .. function:: median(iterable, *[, default])
                  median(arg1, arg2, *args[, default])

       Return the median representation of an iterable or the median representation of two or more
       arguments.

       If one positional argument is provided, it should be an :term:`iterable`.
       The median representation based on the given node representation is returned. If two or more
       positional arguments are provided, the median representation of the given nodes is returned.

       There is one optional keyword-only argument. The *default* argument specifies a median
       representation to return if the provided iterable is empty. If the iterable is empty and
       *default* is not provided, a :exc:`ValueError` is raised.

    """
    is_symmetric = True

    def __call__(self, first, second, default=None):
        raise NotImplementedError

    def mean(self, *args, **kwargs):
        raise NotImplementedError

    def median(self, *args, **kwargs):
        raise NotImplementedError


class IncrementalDistance(Distance):
    """
    An incremental distance provides the interface to efficiently calculate the distance between
    two given objects. One of the objects is treated as a dynamic object. The distance therefore
    builds upon a sequence of changes that are considered for updating the current distance value
    based on the given changes.

    .. function:: update(first, second, *[, base_distance, default])

       Return the updated distance between node representations *first* and applied changes for
       *second*.

       There are two optional keyword-only argument. The *base_distance* is taken to apply the
       distance changes to. If it is not given, a distance of 0 is considered. The *default*
       argument specifies a distance to return if the distance for the given objects can not be
       determined. If the distance can not be returned and *default* is not provided,
       a :exc:`ValueError` is raised.

    """
    def __call__(self, first, second, default=None):
        raise NotImplementedError

    def mean(self, *args, **kwargs):
        raise NotImplementedError

    def median(self, *args, **kwargs):
        raise NotImplementedError

    def update(self, first, second, base_distance=0, default=None):
        raise NotImplementedError
