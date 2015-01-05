"""A black OTP message in the standard encoded form.
"""
import re


def _valid_number(number):
    return isinstance(number, int) and 0 <= number <= 255


def _valid_offset(offset):
    return offset is None or (isinstance(offset, int) and 0 <= offset)


def _is_iterable(obj):
    try:
        iter(obj)
    except TypeError:
        return False
    return True


def _valid_numbers(numbers):
    return all(_valid_number(number) for number in numbers)


def _valid_otp_id(otp_id):
    return isinstance(otp_id, (int, str))


class CannotRender(Exception):
    """Raised instead of rendering transcript if it's not safely printable
    in the standard format.
    """
    def __init__(self, transcript, defects):
        self.transcript = transcript
        self.defects = defects
        super(CannotRender, self).__init__()

    def __str__(self):
        return ", ".join(self.defects)


class CannotParse(Exception):
    """Raised when we couldn't parse text as a black otp transcript.
    """
    def __init__(self, text):
        self.text = text
        super(CannotParse, self).__init__()

    def __str__(self):
        return repr(self.text)


class Transcript(object):
    """A parsed transcript of the content of a black OTP message.
    """
    template = "black otp {otp_id} file start {numbers}offset {offset}"
    template_no_offset = "black otp {otp_id} file start {numbers}"
    pattern = r"""
    (?P<prefix>
        (black[ ]otp|otp[ ]black)[ ]+(?P<otp_id>\d*)[ \n]+
        file[ ]start[ \n]+
        )?
    (?P<digits>
        (?P<firstdigit>\d+)(?:[\n ]+\d+)*
        )?
    (?:[ \n]*
        (?P<postfix>offset[ ](?P<offset>.+))
        )?
    $
    """
    regex = re.compile(pattern, flags=re.IGNORECASE | re.VERBOSE)

    def __init__(self, numbers, offset=None, otp_id=""):
        self.numbers = numbers
        self.offset = offset
        self.otp_id = otp_id

    def defects(self):
        if not _valid_otp_id(self.otp_id):
            yield "invalid otp id {0!r}".format(self.otp_id)
        if not _valid_offset(self.offset):
            yield "invalid offset {0!r}".format(self.offset)
        if not _is_iterable(self.numbers):
            yield "numbers not iterable"
        if not _valid_numbers(self.numbers):
            yield "one or more invalid numbers"

    def render(self):
        defects = list(self.defects())
        if defects:
            raise CannotRender(self, defects)
        numbers = " ".join(str(number) for number in self.numbers)
        if numbers and self.offset is not None:
            numbers = numbers + " "
        if self.offset is None:
            return self.template_no_offset.format(
                otp_id=self.otp_id, numbers=numbers)
        return self.template.format(
            otp_id=self.otp_id, numbers=numbers, offset=self.offset)

    @classmethod
    def parse(cls, text):
        if not text:
            raise CannotParse(text)
        matched = cls.regex.match(text)
        if not matched:
            raise CannotParse(text)
        otp_id = matched.group("otp_id") or ""
        offset = matched.group("offset")
        offset = int(offset) if offset else None
        digits = matched.group("digits")
        numbers = [int(blob) for blob in digits.split()] if digits else []
        return cls(numbers, offset=offset, otp_id=otp_id)
