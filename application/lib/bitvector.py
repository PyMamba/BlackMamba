# -*- encoding: utf-8 -*-
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>

"""
.. module:: bitvector
    :platform: Unix, Windows
    :synopsis: Bitvector utility for BlackMamba

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

# constants
for i in range(32):
    globals()['BV{}'.format(i)] = 1 << i


class BitVector(object):
    """BitVector class.

    This class is used to create bitvector states.
    """

    def __init__(self, vector=0):
        self.vector = vector

    def is_set(self, bit):
        """Return True if the bit is set in the vector

        :param bit: the bit to check
        :type bit: int
        :return: bool
        """

        return (self.vector & (bit)) > 0

    def set(self, bit):
        """Set the given bit to the given var as 1 (turn on)

        :param bit: the bit to set
        :type bit: int
        """

        self.vector |= (bit)

    def unset(self, bit):
        """Unset the given bit to the given var (turn off)

        :param bit: the bit to unset
        :type bit: int
        """

        self.vector &= ~(bit)

    def toggle(self, bit):
        """Togle the given bit for the given var. If the bit is on turn it off
        if the bit is off, turn it on

        :param bit: the bit to be toggled
        :type bit: int
        """

        self.vector ^= (bit)
