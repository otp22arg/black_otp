from pytest import raises
from black_otp.transcript import Transcript, CannotRender, CannotParse


def matches(transcript, numbers, offset, otp_id):
    """assert that a Transcript has the given parameters.
    """
    assert transcript.numbers == numbers
    assert transcript.offset == offset
    assert transcript.otp_id == otp_id


class TestRender(object):

    def test_simple(self):
        transcript = Transcript(numbers=[65, 65], offset=999, otp_id="1")
        assert transcript.render() == "black otp 1 file start 65 65 offset 999"

    def test_no_otp_id(self):
        transcript = Transcript(numbers=[65, 65], offset=999, otp_id=None)
        with raises(CannotRender):
            transcript.render()

    def test_no_numbers(self):
        transcript = Transcript(numbers=[], offset=999, otp_id="1")
        assert transcript.render() == "black otp 1 file start offset 999"

    def test_no_offset(self):
        transcript = Transcript(numbers=[65, 65], offset=None, otp_id="1")
        assert transcript.render() == "black otp 1 file start 65 65"


class TestParse(object):

    def test_simple(self):
        text = "black otp 1 file start 65 65 offset 999"
        transcript = Transcript.parse(text)
        matches(transcript, numbers=[65, 65], offset=999, otp_id="1")

    def test_none(self):
        with raises(CannotParse):
            Transcript.parse(None)

    def test_empty(self):
        with raises(CannotParse):
            Transcript.parse("")

    def test_vacuous(self):
        with raises(CannotParse):
            Transcript.parse("black otp file start offset")

    def test_no_otp_id(self):
        with raises(CannotParse):
            Transcript.parse("black otp file start 65 65 offset 999")

    def test_no_numbers(self):
        transcript = Transcript.parse("black otp 1 file start offset 999")
        matches(transcript, numbers=[], otp_id="1", offset=999)

    def test_no_offset(self):
        transcript = Transcript.parse("black otp 1 file start 65 65")
        matches(transcript, numbers=[65, 65], otp_id="1", offset=None)

    def test_with_newlines(self):
        transcript = Transcript.parse(
            "black otp 1 file start\n65 65\noffset 999\n"
        )
        matches(transcript, numbers=[65, 65], otp_id="1", offset=999)
        transcript = Transcript.parse(
            "black otp 1\nfile start\n65 65\noffset 999"
        )
        matches(transcript, numbers=[65, 65], otp_id="1", offset=999)
