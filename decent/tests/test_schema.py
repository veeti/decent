import pytest
from pytest import mark

from decent.schema import *
from decent.error import *

## Helpers

def ok(x):
    return x

## Empty schema

def test_empty_schema_valid_value():
    schema = Schema({})
    assert schema({}) == {}

@mark.parametrize('value', [None, object(), [], 123, True, False, "Hello"])
def test_empty_schema_invalid_value(value):
    schema = Schema({})
    with pytest.raises(Invalid):
        schema(value)

## Invalid schema

@mark.parametrize('value', [None, object(), [{}], True, False, 123])
def test_invalid_schema(value):
    with pytest.raises(SchemaError):
        Schema(value)

@mark.parametrize('value', [None, object(), True, False, 123])
def test_invalid_schema_validators(value):
    with pytest.raises(SchemaError):
        Schema({
            'a': value,
        })

## Callables

def test_callable_transforms_value():
    schema = Schema({
        'test': lambda x: x + 1
    })

    assert schema({ 'test': 1 }) == { 'test': 2 }

def test_callable_error():
    def raiser(x):
        raise Error("Nope")
    schema = Schema({
        'test': raiser,
    })

    try:
        schema({ 'test': "abc" })
        raise AssertionError("Expected error.")
    except Invalid as e:
        assert len(e) == 1
        assert e.path == ['test']
        assert e.message == "Nope"

def test_callable_invalid():
    def raiser(x):
        first = Error("First")
        second = Error("Second")
        raise Invalid([first, second])
    schema = Schema({
        'test': raiser,
    })

    try:
        schema({ 'test': "abc" })
        raise AssertionError("Expected error.")
    except Invalid as e:
        assert len(e) == 2
        assert "First" in e.messages
        assert "Second" in e.messages

## Nested schemas

def test_nested_valid():
    schema = Schema({
        'test': Schema({
            'inner': lambda x: x + 1,
        })
    })
    assert schema({ 'test': { 'inner': 1 } }) == { 'test': { 'inner': 2 } }

def test_nested_error():
    def raiser(x):
        raise Error("Nope")
    schema = Schema({
        'test': Schema({
            'inner': raiser,
        })
    })

    try:
        schema({ 'test': { 'inner': 123 } })
        raise AssertionError("Expected error.")
    except Invalid as e:
        assert len(e) == 1
        assert e.path == ['test', 'inner']
        assert e.message == "Nope"

def test_nested_multiple_errors():
    def raiser(x):
        raise Error("Nope")
    schema = Schema({
        'will_fail': raiser,
        'nested': Schema({
            'inner': raiser,
            'another': ok,
        })
    })

    try:
        schema({
            'will_fail': "Hello",
            'nested': {
                'inner': 123
            }
        })
        raise AssertionError("Expected error.")
    except Invalid as e:
        assert len(e) == 3
        assert ['will_fail'] in e.paths
        assert ['nested', 'inner'] in e.paths
        assert ['nested', 'another'] in e.paths

## Missing keys

def test_fails_with_missing_key():
    schema = Schema({ 'a': ok })

    try:
        schema({})
        raise AssertionError("Expected error.")
    except Invalid as e:
        assert e.path == ['a']
        assert "required" in e.message

def test_fails_with_multiple_missing_keys():
    schema = Schema({ 'a': ok, 'b': ok, 'c': ok })

    try:
        schema({})
        raise AssertionError("Expected error.")
    except Invalid as e:
        assert len(e) == 3
        assert ['a'] in e.paths
        assert ['b'] in e.paths
        assert ['c'] in e.paths
        for message in e.messages:
            assert "required" in message

def test_fails_with_nested_missing_keys():
    schema = Schema({
        'nested': Schema({
            'a': ok,
            'b': ok,
            'c': ok,
        }),
    })

    try:
        schema({ 'nested': {} })
        raise AssertionError("Expected error.")
    except Invalid as e:
        assert len(e) == 3
        assert ['nested', 'a'] in e.paths
        assert ['nested', 'b'] in e.paths
        assert ['nested', 'c'] in e.paths
        for message in e.messages:
            assert "required" in message

def test_fails_missing_nested_schema():
    schema = Schema({
        'nested': Schema({
            'a': ok,
            'b': ok,
            'c': ok,
        }),
    })

    try:
        schema({})
        raise AssertionError("Expected error.")
    except Invalid as e:
        assert len(e) == 1
        assert e.path == ['nested']

def test_fails_missing_custom_message():
    schema = Schema({ 'a': ok }, required_error="Bla")

    try:
        schema({})
        raise AssertionError("Expected error.")
    except Invalid as e:
        assert len(e) == 1
        assert e.path == ['a']
        assert e.message == "Bla"

## Extra keys

def test_discards_unknown_keys():
    schema = Schema({ 'a': ok }, extra_keys=Schema.IGNORE)

    result = schema({ 'a': 123, 'b': 456 })
    assert 'a' in result
    assert 'b' not in result

def test_accepts_unknown_keys():
    schema = Schema({
        'a': ok,
    }, extra_keys=Schema.ACCEPT)

    result = schema({ 'a': 123, 'b': 456 })
    assert 'a' in result
    assert 'b' in result
    assert result['b'] == 456

def test_fails_unknown_keys():
    schema = Schema({
        'a': ok,
    }, extra_keys=Schema.REJECT)

    try:
        schema({ 'a': 123, 'b': 456 })
        raise AssertionError("Expected error.")
    except Invalid as e:
        assert len(e) == 1
        assert e.path == ['b']

## Optional keys

def test_optional_keys_missing():
    schema = Schema({
        'a': ok,
        Optional('b'): ok,
    })

    result = schema({ 'a': 123 })
    assert result['a'] == 123
    assert 'b' not in result

def test_optional_keys_accepted():
    schema = Schema({
        Optional('b'): ok,
    })

    result = schema({ 'b': 456 })
    assert result['b'] == 456

## Default values

def test_default_value():
    schema = Schema({
        Default('test', 123): ok,
    })

    assert schema({}) == { 'test': 123 }

def test_nested_default_value():
    schema = Schema({
        Default('test', {}): Schema({
            Default('inner', 123): ok,
        })
    })

    assert schema({}) == { 'test': { 'inner': 123 } }

## Validator on entire schema

def test_entire_validator_gets_all_data():
    called = []
    def entire(data):
        assert data['a'] == 'a'
        assert data['b'] == 'b'
        called.append(True)
    schema = Schema({ 'a': ok, 'b': ok }, entire=entire)

    schema({ 'a': 'a', 'b': 'b' })
    assert called

def test_entire_validator_mutates_data():
    def entire(data):
        data['a'], data['b'] = data['b'], data['a']
        return data
    schema = Schema({ 'a': ok, 'b': ok }, entire=entire)

    assert schema({ 'a': 'b', 'b': 'a' }) == { 'a': 'a', 'b': 'b' }

def test_entire_validator_called_with_failures():
    called = []
    def raiser(x):
        raise Error("Nope")
    def entire(data):
        called.append(1)
        assert data['a'] == 'a'
        # b failed before, so it shouldn't be included
        assert 'b' not in data
    schema = Schema({
        'a': ok,
        'b': raiser,
    }, entire=entire)

    try:
        schema({
            'a': 'a',
            'b': 123,
        })
        raise AssertionError("Expected error.")
    except Invalid as e:
        assert called

def test_entire_validator_raises_invalid():
    def entire(data):
        raise Error("Nope")
    schema = Schema({ 'a': ok }, entire=entire)

    try:
        schema({ 'a': 123 })
        raise AssertionError("Expected error.")
    except Invalid as e:
        assert len(e) == 1
        assert e.message == "Nope"

def test_entire_validator_raises_with_failures():
    def entire(data):
        raise Error("Entire")
    def raiser(x):
        raise Error("Nope")
    schema = Schema({ 'a': raiser }, entire=entire)

    try:
        schema({ 'a': 123 })
        raise AssertionError("Expected error.")
    except Invalid as e:
        assert len(e) == 2
        assert "Entire" in e.messages
        assert "Nope" in e.messages

## Markers

def test_marker_str():
    marker = Marker("Hello, world!")
    assert marker == "Hello, world!"
    assert str(marker) == "Hello, world!"
