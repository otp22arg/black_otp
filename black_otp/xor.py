"""Routines for XOR decoding against a one-time pad in various forms.
"""


class InvalidOffset(Exception):
    """Raised when API consumer passes a negative or non-int offset value.
    """
    def __init__(self, value):
        self.value = value
        super(Exception, self).__init__()


class PadExhausted(Exception):
    """Raised when trying to decode numbers without enough pad data.
    """
    def __init__(self, pad_path=None, pad_file=None):
        self.pad_path = pad_path
        self.pad_file = pad_file
        super(PadExhausted, self).__init__()


def xor_iterator(transcript_numbers, pad_numbers):
    return (
        pad_number ^ transcript_number
        for pad_number, transcript_number
        in zip(pad_numbers, transcript_numbers)
    )


def xor_list(transcript_numbers, pad_numbers):
    """
    Raises PadExhausted if pad is too short.
    """
    if len(pad_numbers) < len(transcript_numbers):
        raise PadExhausted()
    return list(xor_iterator(transcript_numbers, pad_numbers))


def xor_file(transcript_numbers, pad_file, offset):
    """XOR the given numbers against numbers from given file at given offset.

    pad_file must be a file-like object with a seek method.

    Raises PadExhausted if pad is too short.

    This intentionally does NOT close the given stream, so that a stream can be
    reused without reopening if desired. If you want a one-shot that handles
    the closing, use xor_path instead.
    """
    if not isinstance(offset, int) or offset < 0:
        raise InvalidOffset(offset)
    pad_file.seek(offset)
    pad_bytes = pad_file.read(len(transcript_numbers))
    if len(pad_bytes) < len(transcript_numbers):
        raise PadExhausted(pad_file=pad_file)
    return xor_iterator(transcript_numbers, pad_bytes)


def xor_path(transcript_numbers, path, offset):
    """XOR the given numbers against numbers from given file at given offset.

    path should be a valid path to a pad file.

    Raises PadExhausted if pad is too short.
    """
    if not isinstance(offset, int) or offset < 0:
        raise InvalidOffset(offset)
    with open(path, 'rb') as stream:
        # preflight so we don't have to waste time on bad offsets
        stream.seek(0, 2)
        length = stream.tell()
        if offset > length:
            raise PadExhausted(pad_path=path)
        return xor_file(transcript_numbers, stream, offset=offset)
