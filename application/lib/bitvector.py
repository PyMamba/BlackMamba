# -*- encoding: utf-8 -*-
# Copyright (c) 2013 - Oscar Campos <oscar.campos@member.fsf.org>

"""
.. module:: bitvector
    :platform: Unix, Windows
    :synopsis: Bitvector utility for BlackMamba

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>
"""

# constants
BV00 = 1 << 0
BV01 = 1 << 1
BV02 = 1 << 2
BV03 = 1 << 3
BV04 = 1 << 4
BV05 = 1 << 5
BV06 = 1 << 6
BV07 = 1 << 7
BV08 = 1 << 8
BV09 = 1 << 9
BV10 = 1 << 10
BV11 = 1 << 11
BV12 = 1 << 12
BV13 = 1 << 13
BV14 = 1 << 14
BV15 = 1 << 15
BV16 = 1 << 16
BV17 = 1 << 17
BV18 = 1 << 18
BV19 = 1 << 19
BV20 = 1 << 20
BV21 = 1 << 21
BV22 = 1 << 22
BV23 = 1 << 23
BV24 = 1 << 24
BV25 = 1 << 25
BV26 = 1 << 26
BV27 = 1 << 27
BV28 = 1 << 28
BV29 = 1 << 29
BV30 = 1 << 30
BV31 = 1 << 31


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
