from __future__ import print_function
import random
import math
import itertools


class Distribution(object):
    def __iter__(self):
        raise NotImplementedError

    def get_n(self, count):
        """
        Return `count` random points from the distribution

        :param count: number of points to generate
        :return: list of x, y coordinates
        :rtype: list[tuple[float, float]]
        """
        return list(itertools.islice(self, count))

    def get_density(self, density):
        """
        Return random points from the distribution with average density

        :param density: desired density of points, in points per square unit
        :return: list of x, y coordinates
        :rtype: list[tuple[float, float]]
        """
        raise NotImplementedError


class Circle2D(Distribution):
    """
    Create points on a 2D circle

    :param radius_center: average distance from center
    :type radius_center: float or None
    :param noise: width of distribution around `radius_center`
    :type noise: float
    """
    def __init__(self, radius_center=None, noise=0.1):
        self.radius_center = radius_center if radius_center is not None else 1.0 - noise
        self.noise = noise
        self._core_area = math.pi * ((radius_center + noise) ** 2 - (radius_center - noise) ** 2)

    def __iter__(self):
        radius_center, noise = self.radius_center, self.noise
        rnd_float, rnd_gauss, msin, mcos = random.random, random.gauss, math.sin, math.cos
        while True:
            angle = math.pi * 2 * rnd_float()
            radius = rnd_gauss(radius_center, noise)
            yield radius * msin(angle), radius * mcos(angle)

    def get_density(self, density):
        return self.get_n(int(density * self._core_area))
