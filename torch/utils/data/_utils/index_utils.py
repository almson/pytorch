from math import sqrt, floor


class Range:
    size: int

    # for slicing
    start: int
    stop: int
    step: int

    # for iterating
    index: int

    def __init__(self, size, start=None, stop=None, step=None):
        self.size = size
        self.start = start if start is not None else 0
        self.stop = stop if stop is not None else size
        self.step = step if step is not None else 1
        assert 0 <= self.start <= self.stop
        # assert self.stop <= self.size  # Allow wrap-around
        assert 0 < self.step

    def __len__(self):
        if self.start == self.stop:
            return 0
        return (self.stop - self.start - 1) // self.step + 1

    def __getitem__(self, index):
        if isinstance(index, slice):
            sl = slice(index.start if index.start is not None else 0,
                       index.stop if index.stop is not None else len(self),
                       index.step if index.step is not None else 1)
            if not (0 <= sl.start <= len(self) and sl.start <= sl.stop <= len(self) and 0 < sl.step):
                raise IndexError
            return self._slice(sl)

        if not 0 <= index < len(self):
            raise IndexError

        abs_index = (self.start + index * self.step) % self.size

        return self._get(abs_index)

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index == len(self):
            raise StopIteration
        next = self[self.index]
        self.index = self.index + 1
        return next

    def _get(self, index):
        return index

    def _slice(self, sl):
        return Range(self.size,
                     self.start + sl.start * self.step,
                     self.start + sl.stop * self.step,
                     self.step * sl.step)


# Should use a faster method
def _is_prime(n):
    if n == 2:
        return True
    if n == 1 or n % 2 == 0:
        return False

    for d in range(3, floor(sqrt(n)) + 1, 2):  # can use isqrt in Python 3.8
        if n % d == 0:
            return False

    return True


class Permutation(Range):
    """
    Generates a random permutation of integers from 0 up to size.
    Inspired by https://preshing.com/20121224/how-to-generate-a-sequence-of-unique-random-integers/
    """

    prime: int
    seed: int

    def __init__(self, size, seed, start=None, stop=None, step=None, _prime=None, _seed=None):
        super().__init__(size, start, stop, step)
        self.prime = self._get_prime(size) if _prime is None else _prime
        self.seed = self._get_seed(seed) if _seed is None else _seed

    def _get(self, index):
        x = self._map(index)

        if x < self.size:
            return x
        else:
            # _map(x) for x >= self.size returns values < self.size, as guaranteed by _gen_seed
            # and these values fall into the "holes" left by x for which _map(x) >= self.size
            return self._map(x)

    def _slice(self, sl):
        return Permutation(self.size,
                           self.seed,
                           self.start + sl.start * self.step,
                           self.start + sl.stop * self.step,
                           self.step * sl.step,
                           self.prime,
                           self.seed)

    @staticmethod
    def _get_prime(size):
        """
        Returns the prime number >= size which has the form (4n-1)
        """
        n = size + (3 - size % 4)
        while not _is_prime(n):
            n = n + 4
        return n

    def _get_seed(self, seed):
        for a in range(self.size, self.prime):
            if self._map(a, seed) >= self.size:
                return self._get_seed(seed + 1)
        return seed

    def _map(self, index, seed=None):
        if seed is None:
            seed = self.seed
        a = self._permute_qpr(index)
        b = (a + seed) % self.prime
        c = self._permute_qpr(b)
        return c

    def _permute_qpr(self, x):
        residue = pow(x, 2, self.prime)

        if x * 2 < self.prime:
            return residue
        else:
            return self.prime - residue
