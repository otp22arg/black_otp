import os
from pytest import raises
from black_otp.xor import (
    xor_iterator, xor_list, xor_file, xor_path,
    InvalidOffset, PadExhausted
)
HERE = os.path.dirname(__file__)
WORLD = os.path.join(HERE, "_world")


class TestXorIterator(object):
    """Test the basic XOR decode implementation.

    This doesn't do bounds checking because that might not be possible,
    since xor_iterator consumes iterators.
    """

    def test_simple(self):
        """Trivial test and sanity check using truth table for logical XOR
        """
        assert list(xor_iterator([0, 0, 1, 1], [0, 1, 0, 1])) == [0, 1, 1, 0]

    def test_fancier(self):
        """Trivial exercise of bitwise operation on normal values
        """
        a = b"hello"
        b = b"world"
        assert list(xor_iterator(a, b)) == [31, 10, 30, 0, 11]

    def test_short_transcript(self):
        """All should be okay if less transcript data than pad data.
        """
        a = b"hello"
        b = b"world"
        assert list(xor_iterator(a[:-1], b)) == [31, 10, 30, 0]
        assert list(xor_iterator([], b)) == []


def TestXorList(object):

    def test_simple(self):
        assert xor_list(b"hello", b"world") == [31, 10, 30, 0, 11]

    def test_short_pad(self):
        """Complain loudly if pad data is exhausted.
        """
        a = b"hello"
        b = b"world"
        with raises(PadExhausted):
            list(xor_list(a, b[:-1]))


class TestXorFile(object):
    """
    This doesn't need to exercise lots of different values because those
    kinds of tests should be in TestXorIterator.
    """

    def test_simple(self):
        with open(WORLD, 'rb') as obj:
            it = xor_file(b"hello", obj, offset=0)
            assert list(it) == [31, 10, 30, 0, 11]

    def test_short_pad(self):
        with raises(PadExhausted):
            with open(WORLD, 'rb') as obj:
                xor_file(b"hello there", obj, offset=0)

    def test_negative_offset(self):
        with raises(InvalidOffset):
            with open(WORLD, 'rb') as obj:
                xor_file(b"whatever", obj, offset=-2)

    def test_non_int_offset(self):
        with raises(InvalidOffset):
            with open(WORLD, 'rb') as obj:
                xor_file(b"whatever", obj, offset=None)


class TestXorPath(object):
    """
    This doesn't need to exercise lots of different values because those
    kinds of tests should be in TestXorIterator.
    """

    def test_simple(self):
        it = xor_path(b"hello", WORLD, offset=0)
        assert list(it) == [31, 10, 30, 0, 11]

    def test_negative_offset(self):
        with raises(InvalidOffset):
            xor_path(b"whatever", WORLD, offset=-2)

    def test_non_int_offset(self):
        with raises(InvalidOffset):
            xor_path(b"whatever", WORLD, offset=None)
