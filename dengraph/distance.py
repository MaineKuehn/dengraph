import dengraph.compat


class Distance(dengraph.compat.ABCBase):
    """
    A distance provides the interface for calculation on arbitrary *node* objects.

    All implementations of this ABC guarantee the following operators:

    .. describe:: __call__(x, y, *[, default])

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

    .. function:: min(iterable, *[, default])
                  min(arg1, arg2, *args[, default]

       Return the minimum distance in an iterable or the minimum distance of two or more arguments.

       If one positional argument is provided, it should be an :term:`iterable`.
       The minimum distance based on the given edge representation is returned. If two or more
       positional arguments are provided, the minimum distance of the given edges is returned.

       There is one optional keyword-only argument. The *default* argument specifies a distance to
       return if the provided iterable is empty. If the iterable is emtpy and *default* is not
       provided, a :exc:`ValueError` is raised.

    .. function:: max(iterable, *[, default])
                  max(arg1, arg2, *args[, default])

       Return the maximum distance in an iterable or the maximum distance of two or more arguments.

       If one positional argument is provided, it should be an :term:`iterable`.
       The maximum distance based on the given edge representations is returned. If two or more
       positional arguments are provided, the maximum distance of the given edges is returned.

       There is one optional keyword-only argument. The *default* argument specifies a distance to
       return if the provided iterable is empty. If the iterable is empty and *default* is not
       provided, a :exc:`ValueError` is raised.

    """
    def __call__(self, x, y, default=None):
        raise NotImplementedError

    def mean(self, *args, **kwargs):
        raise NotImplementedError

    def median(self, *args, **kwargs):
        raise NotImplementedError

    def max(self, *args, **kwargs):
        raise NotImplementedError

    def min(self, *args, **kwargs):
        raise NotImplementedError
