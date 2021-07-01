from __future__ import print_function, division
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
        self._core_area = math.pi * (
            (self.radius_center + self.noise) ** 2
            - (self.radius_center - self.noise) ** 2
        )

    def __iter__(self):
        radius_center, noise = self.radius_center, self.noise
        rnd_float, rnd_gauss, msin, mcos = (
            random.random,
            random.gauss,
            math.sin,
            math.cos,
        )
        while True:
            angle = math.pi * 2 * rnd_float()
            radius = rnd_gauss(radius_center, noise)
            yield radius * msin(angle), radius * mcos(angle)

    def get_density(self, density):
        return self.get_n(int(density * 1 / (0.6827 ** 2) * self._core_area))


class Moon(Distribution):
    """
    Create points on an open 2D circle

    :param radius_center: average distance from center
    :type radius_center: float or None
    :param noise: width of distribution around `radius_center`
    :type noise: float
    """

    def __init__(
        self,
        radius_center=None,
        noise=0.1,
        angular_center=0,
        angular_noise=0.5 * math.pi,
        center=(0.0, 0.0),
    ):
        self.radius_center = radius_center if radius_center is not None else 1.0 - noise
        self.noise = noise
        self.angular_center = angular_center
        self.angular_noise = angular_noise
        self.center = center
        self._core_area = angular_noise * (
            (self.radius_center + self.noise) ** 2
            - (self.radius_center - self.noise) ** 2
        )

    def __iter__(self):
        radius_center, noise = self.radius_center, self.noise
        angular_center, angular_noise = self.angular_center, self.angular_noise
        center_x, center_y = self.center
        rnd_gauss, msin, mcos = random.gauss, math.sin, math.cos
        while True:
            angle = rnd_gauss(angular_center, angular_noise)
            radius = rnd_gauss(radius_center, noise)
            yield radius * msin(angle) + center_x, radius * mcos(angle) + center_y

    def get_density(self, density):
        return self.get_n(int(density * 1 / (0.6827 ** 2) * self._core_area))


class Square(Distribution):
    """
    Create points on a square

    :param length: length of edges in `(X, Y)`
    :type length: tuple[float, float]
    :param center: center in `(X, Y)`
    :type center: tuple[float, float]
    """

    def __init__(self, length=(1.0, 1.0), center=(0.0, 0.0)):
        self.length = length
        self.center = center

    def __iter__(self):
        length_x, length_y = self.length
        offset_x, offset_y = (
            self.center[0] - length_x / 2,
            self.center[1] - length_y / 2,
        )
        rnd_float = random.random
        while True:
            yield rnd_float() * length_x + offset_x, rnd_float() * length_y + offset_y

    def get_density(self, density):
        return self.get_n(int(density * self.length[0] * self.length[1]))


class Checkers(Distribution):
    """
    Create points on multiple squares

    :param length: length of enclosing edges in `(X, Y)`
    :type length: tuple[float, float]
    :param count: number of squares per `(X, Y)`
    :type count: tuple[int, int]
    :param border: relative border size between squares
    :type border: float
    """

    def __init__(self, length=(1.0, 1.0), count=(8, 8), border=0.2):
        self.length = length
        self.count = count
        self.border = border

    def __iter__(self):
        x_length, y_length = (
            self.length[0] / self.count[0],
            self.length[1] / self.count[1],
        )
        squares = [
            iter(
                Square(
                    length=(x_length * (1 - self.border), y_length * (1 - self.border)),
                    center=(
                        x_length * (x_idx + 0.5 - self.count[0] / 2.0),
                        y_length * (y_idx + 0.5 - self.count[1] / 2.0),
                    ),
                )
            )
            for x_idx in range(self.count[0])
            for y_idx in range(self.count[1])
            if (x_idx + y_idx) % 2 == 0
        ]
        while True:
            for sqr in squares:
                yield next(sqr)

    def get_density(self, density):
        return self.get_n(int(0.5 * density * self.length[0] * self.length[1]))


class Gaussian(Distribution):
    """
    Create points of a gaussian

    :param length: length of edges in `(X, Y)`
    :type center: tuple[float, float]
    :param deviation: width in `(X, Y)`
    :type deviation: tuple[float, float]
    """

    def __init__(self, center=(0, 0), deviation=(0.075, 0.075)):
        self.center = center
        self.deviation = deviation
        self._core_area = 0.5 * math.pi * (sum(deviation) / len(deviation))

    def __iter__(self):
        mu_x, mu_y = self.center
        sigma_x, sigma_y = self.deviation
        rnd_gauss = random.gauss
        while True:
            yield rnd_gauss(mu_x, sigma_x), rnd_gauss(mu_y, sigma_y)

    def get_density(self, density):
        return self.get_n(int(density * self._core_area))
