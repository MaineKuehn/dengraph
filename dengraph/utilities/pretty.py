# -*- coding: utf-8 -*-
from __future__ import absolute_import, division
import dengraph.compat


def repr_container(container, max_elements=1, max_chars=10):
    """
    Get a shortened representation of a container, showing only limited elements

    :param container: an iterable container
    :param max_elements: maximum number of elements to display
    :type max_elements: int
    :param max_chars: maximum number of characters to show if container is a string
    :type max_chars: int or None

    If `max_chars is None`, it defaults to `max_elements`.
    """
    max_chars = max_elements if max_chars is None else max_chars
    if len(container) <= max_elements:
        return repr(container)
    if isinstance(container, str):
        if len(container) <= max_chars:
            return repr(container)
        return '"%s...[+%d]"' % (container[:max_chars], len(container) - max_chars)
    elif isinstance(container, (dict, dengraph.compat.collections_abc.Mapping)):
        citer = iter(container)
        item_repr = ', '.join('%r: %r' % (key, container[key]) for key in (next(citer) for _ in range(max_elements)))
    else:  # elif isinstance(container, (set, frozenset, list, tuple)):
        citer = iter(container)
        item_repr = ', '.join(repr(next(citer)) for _ in range(max_elements))
    start, stop = CONTAINER_SYMBOLS.get(type(container), '<>')
    return start + item_repr + ', <%d elements>' % (len(container) - max_elements) + stop

CONTAINER_SYMBOLS = {
    list: '[]',
    tuple: '()',
    dict: '{}',
    set: '{}',
    frozenset: ('f{', '}'),
}


def str_time(seconds):
    """
    Format time in seconds to a three-digit + unit format

    :param seconds: time in seconds
    :return: `str` representation in appropriate unit
    """
    if seconds is None:
        return '---  s'
    if seconds == 0:
        return '0.0  s'
    e_power = 18
    for t_power, prefix in enumerate(u'EPTGMk mμnpfa'):
        power = e_power - t_power * 3
        p_num = seconds / (10 ** power)
        if 1E3 > p_num > 1.0:
            if p_num > 100:
                return '%3.0f %ss' % (p_num, prefix)
            if p_num > 10:
                return '%2.0f. %ss' % (p_num, prefix)
            return '%3.1f %ss' % (p_num, prefix)
