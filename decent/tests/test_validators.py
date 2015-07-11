import six
import pytest

from decent.validators import *
from decent.error import Error

## All

def test_all():
    def add_one(x):
        return x + 1
    all = All(add_one, add_one, add_one)

    assert all(0) == 3

def test_all_error():
    def raiser(x):
        raise Error("No")
    all = All(lambda x: x, lambda y: y, raiser)

    try:
        all(123)
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "No"

## Any

def test_any_first():
    def ok(x):
        return x
    def other(x):
        return x + 1
    any = Any(ok, other)

    assert any(123) == 123

def test_any_second():
    def not_ok(x):
        raise Error("Nope")
    def ok(x):
        return x + 1
    any = Any(not_ok, ok)

    assert any(123) == 124

def test_any_error():
    def not_ok(x):
        raise Error("Nope")
    any = Any(not_ok)

    try:
        any(123)
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Nope"

def test_any_returns_last_error():
    def not_ok(x):
        raise Error("No")
    def really_not_ok(x):
        raise Error("No!")
    any = Any(not_ok, really_not_ok)

    try:
        any(123)
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "No!"

def test_any_raises_other_exceptions_instantly():
    def first(x):
        raise Exception("No")
    def second(x):
        raise Exception("No!")
    any = Any(first, second)

    try:
        any(123)
        raise AssertionError("Expected error.")
    except Exception as e:
        assert str(e) == "No"

## Maybe

def test_maybe_none():
    def raiser():
        raise Error("Not supposed to be called")
    maybe = Maybe(raiser)
    assert maybe(None) == None

def test_maybe():
    maybe = Maybe(lambda x: x + 1)
    assert maybe(1) == 2

## Msg

def test_msg_valid():
    msg = Msg(lambda x: x, "Error message")

    assert msg(123) == 123

def test_msg_mutates_single_error():
    def error(x):
        raise Error("Not this message")
    msg = Msg(error, "This message")

    try:
        msg(123)
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "This message"

## Default

def test_default():
    default = Default(123)
    assert default(None) == 123
    assert default(0) == 0
    assert default(False) == False
    assert default(124) == 124

## Eq

def test_eq_valid():
    eq = Eq(123)

    assert eq(123) == 123

def test_eq_invalid():
    eq = Eq(123)

    try:
        eq(None)
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Not equal to 123"

def test_eq_invalid_custom_message():
    eq = Eq(123, "Custom message {!r}")

    try:
        eq(None)
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Custom message " + str(repr(123))

## Type

def test_type_valid():
    typ = Type(int)

    assert typ(123) == 123

def test_type_invalid():
    typ = Type(bool)

    try:
        typ(123)
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Not of type bool"

def test_type_invalid_custom_message():
    typ = Type(int, "Custom message")

    try:
        typ(None)
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Custom message"

## Instance

def test_instance_valid():
    instance = Instance(int)

    assert instance(123) == 123

def test_instance_subclass_valid():
    class Base(object):
        pass
    class Child(Base):
        pass
    instance = Instance(Base)
    base = Base()
    child = Child()

    assert instance(base) is base
    assert instance(child) is child

def test_instance_invalid():
    class Class(object):
        pass
    instance = Instance(Class)

    try:
        instance(object())
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Not an instance of Class"

def test_instance_invalid_custom_message():
    class Class(object):
        pass
    instance = Instance(Class, "Custom message")

    try:
        instance(object())
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Custom message"

## Coerce

def test_coerce_valid():
    coerce = Coerce(int)

    assert coerce("123") == 123

def test_coerce_invalid():
    coerce = Coerce(int)

    try:
        coerce("asd")
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Not a valid int value"

def test_coerce_invalid_custom_message():
    coerce = Coerce(int, message="Custom message")

    try:
        coerce("asd")
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Custom message"

## List

def test_list_mutates():
    list = List(lambda x: x + 1)
    assert list([1, 2, 3]) == [2, 3, 4]

def test_list_fails():
    def fun(x):
        if x % 2 == 0:
            raise Error("Even numbers not welcome here")
        return x
    list = List(fun)

    try:
        list([1, 2, 3, 4]) # 2 and 4 will fail
        raise AssertionError("Expected error.")
    except Invalid as e:
        assert len(e) == 2
        assert [1] in e.paths
        assert [3] in e.paths
        for e in e:
            assert e.message == "Even numbers not welcome here"

def test_list_invalid_fails():
    def fail(x):
        raise Invalid([Error("One"), Error("Two")])
    list = List(fail)

    try:
        list([1, 2, 3])
        raise AssertionError("Expected error.")
    except Invalid as e:
        assert len(e) == 6
        assert [0] in e.paths
        assert [1] in e.paths
        assert [2] in e.paths

def test_list_preserves_failed_path():
    def fail(x):
        if x == 1:
            raise Error("No", ['one', 'two'])
        return x
    list = List(fail)

    try:
        list([0, 1])
        raise AssertionError("Expected error.")
    except Invalid as e:
        assert [1, 'one', 'two'] in e.paths

def test_list_not_iterable():
    list = List(lambda x: x)

    try:
        list(object())
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Must be a list"

## Boolean

@pytest.mark.parametrize('input, output', [
    (True, True),
    (False, False),
    (None, False),
    (0, False),
    (1, True),
    (-1, True),
    (123, True),
    ('y', True),
    ('Y', True),
    ('yes', True),
    ('YES', True),
    ('n', False),
    ('N', False),
    ('no', False),
    ('NO', False),
    ('t', True),
    ('T', True),
    ('true', True),
    ('TRUE', True),
    ('f', False),
    ('F', False),
    ('false', False),
    ('FALSE', False),
])
def test_boolean(input, output):
    assert Boolean()(input) == output

@pytest.mark.parametrize('input', [
    123.456,
    "asdfghjkl",
    object(),
    { 'a': 'b' },
    [123, 456, 789],
])
def test_boolean_invalid(input):
    with pytest.raises(Error):
        Boolean()(input)

## Range

def test_range_valid_min():
    range = Range(min=1)
    assert range(1) == 1
    assert range(2) == 2
    assert range(2.0) == 2.0

def test_range_valid_max():
    range = Range(max=2)
    assert range(2) == 2
    assert range(1) == 1
    assert range(1.0) == 1.0

def test_range_valid_min_max():
    _range = Range(min=0, max=10)
    for i in range(0, 11):
        assert _range(i) == i

def test_range_invalid_min():
    range = Range(min=100)
    try:
        range(99)
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Must be at least 100"

def test_range_invalid_max():
    range = Range(max=100)
    try:
        range(101)
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Must be at most 100"

@pytest.mark.parametrize('input', [-1, 101])
def test_range_invalid_min_max(input):
    range = Range(min=0, max=100)
    try:
        range(input)
        raise AssertionError("Expected error.")
    except Error as e:
        pass

def test_range_invalid_min_message():
    range = Range(min=0, min_message="Fail")

    try:
        range(-1)
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Fail"

def test_range_invalid_max_message():
    range = Range(max=0, max_message="Fail")

    try:
        range(1)
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Fail"

@pytest.mark.parametrize('input', [object(), "asd", True, False, {}, []])
def test_range_invalid_nan(input):
    range = Range(min=0, max=100)
    try:
        range(input)
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Not a number"

## Length

def test_length_valid_min():
    length = Length(min=1)
    assert length("Hello") == "Hello"

def test_length_valid_max():
    length = Length(max=2)
    assert length(".") == "."

def test_length_invalid_min():
    length = Length(min=2)
    try:
        length([])
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Must have a length of at least 2"

def test_length_invalid_max():
    length = Length(max=2)
    try:
        length([1, 2, 3])
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Must have a length of at most 2"

def test_length_invalid_input():
    length = Length(min=1, max=10)
    try:
        length(object())
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Does not have a length"

## Lower

def test_lower():
    assert Lower()("HELLO WORLD") == "hello world"

def test_lower_invalid():
    try:
        Lower()(None)
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Must be a string"

## Upper

def test_upper():
    assert Upper()("hello world") == "HELLO WORLD"

def test_upper_invalid():
    try:
        Upper()(None)
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Must be a string"

## Strip

def test_strip():
    assert Strip()("  hello world  ") == "hello world"

def test_strip_invalid():
    try:
        Strip()(None)
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Must be a string"

## NotEmpty

def test_not_empty():
    assert NotEmpty()("Hello") == "Hello"
    assert NotEmpty()(" ") == " "

@pytest.mark.parametrize('input', ["", None])
def test_not_empty_invalid(input):
    try:
        NotEmpty()(input)
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Must not be empty"

## UUID

def test_uuid():
    import uuid
    validator = Uuid()

    result = validator("ecc9194a-26e2-11e5-b012-cba0faa68d69")
    assert isinstance(result, uuid.UUID)
    assert str(result) == "ecc9194a-26e2-11e5-b012-cba0faa68d69"

def test_uuid_no_conversion():
    validator = Uuid(to_uuid=False)

    result = validator("ecc9194a-26e2-11e5-b012-cba0faa68d69")
    assert isinstance(result, six.string_types)
    assert result == "ecc9194a-26e2-11e5-b012-cba0faa68d69"

def test_uuid_already_uuid():
    import uuid
    input = uuid.uuid4()
    validator = Uuid()

    assert validator(input) is input

@pytest.mark.parametrize('input', [None, 123, 'asd'])
def test_uuid_invalid(input):
    validator = Uuid()
    try:
        validator(input)
        raise AssertionError("Expected error.")
    except Error as e:
        assert e.message == "Not a valid UUID"
