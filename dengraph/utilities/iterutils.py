def iteritems(iterable):
    """Generate all key, value pairs of an indexable iterable"""
    try:
        # py2.6 dict
        return iterable.iteritems()
    except AttributeError:
        try:
            # dic
            return iterable.items()
        except AttributeError:
            # list, tuple, ...
            return enumerate(iterable)
