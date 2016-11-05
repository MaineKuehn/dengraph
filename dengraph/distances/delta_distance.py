from __future__ import absolute_import

from dengraph import distance


class DeltaDistance(distance.Distance):
    def __call__(self, x, y, default=None):
        return abs(x - y)

    def mean(self, *args, **kwargs):
        if len(args) == 1:
            args = args[0]
        try:
            return sum(args) / float(len(args))
        except ZeroDivisionError:
            if "default" in kwargs:
                return kwargs.get("default")
            raise ValueError()

    def median(self, *args, **kwargs):
        if len(args) == 1:
            args = args[0]
        try:
            return sorted(args)[int(len(args) / 2)]
        except IndexError:
            if "default" in kwargs:
                return kwargs.get("default")
            raise ValueError()
