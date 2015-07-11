from decent.error import *

def test_error_str():
    error = Error("Hello, world!")
    assert str(error) == "Hello, world!"

def test_error_messages():
    error = Error("Hello")
    assert error.messages == ["Hello"]

def test_error_paths():
    error = Error("Hello", [1, 2, 3])
    assert error.paths == [[1, 2, 3]]

def test_error_as_dict():
    error = Error("Hello, world!", ['hello', 'world'])
    assert error.as_dict() == { "hello.world": "Hello, world!" }
    assert error.as_dict('/') == { "hello/world": "Hello, world!" }

def test_error_non_str_path_as_dict():
    error = Error("Hello, world!", [0, 1, '2'])
    assert error.as_dict() == { "0.1.2": "Hello, world!" }

def test_error_no_path_as_dict():
    error = Error("Hello, world!")
    assert error.as_dict() == { "": "Hello, world!" }

def test_invalid_as_dict():
    error = Invalid([Error("First", [0, 'first']), Error("Second", ['second', 'third'])])
    assert error.as_dict() == {
        '0.first': "First",
        'second.third': "Second",
    }
    assert error.as_dict('/') == {
        '0/first': "First",
        'second/third': "Second",
    }

def test_invalid_str():
    error = Invalid([Error("One"), Error("Two")])
    assert str(error) == "One, Two"
