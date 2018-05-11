import pytest
from pyjo.exceptions import FieldTypeError

from pyjo_mdl import pyjo_model_from_structure, BASE_FIELD_PROPERTIES
from pyjo_mdl.exceptions import InstanceValidationError

__author__ = 'xelhark'


def test_simple_int():
    Model = pyjo_model_from_structure({
        'numero': {
            'type': 'integer',
            'min_value': 4,
            'max_value': 10,
        }
    })

    with pytest.raises(InstanceValidationError) as err:
        Model(numero=3)
    assert str(err.value) == "Value is smaller than min value: 3 < 4"

    valid = Model(numero=4)
    assert valid.numero == 4


def test_can_validate_string_number():
    Model = pyjo_model_from_structure({
        'numero': {
            'type': 'integer',
            'min_value': 4,
            'max_value': 10,
        }
    })

    valid = Model(numero="5")
    assert valid.numero == 5


def test_simple_string():
    Model = pyjo_model_from_structure({
        'numero': {
            'type': 'string',
            'max_length': 5
        }
    })

    instance = Model(numero='3')
    assert instance.numero == '3'
    assert instance.to_dict() == {'numero': '3'}

    with pytest.raises(InstanceValidationError) as err:
        Model(numero='Supercaligragilistichespiralidoso')

    assert str(err.value) == "Value Supercaligragilistichespiralidoso is longer than max allowed length (5)"


def test_float():
    Model = pyjo_model_from_structure({
        'numero': {
            'type': 'float',
            'min_value': 4.2,
            'max_value': 10.0,
        }
    })

    with pytest.raises(InstanceValidationError) as err:
        Model(numero=4.1)
    assert str(err.value) == "Value is smaller than min value: 4.1 < 4.2"

    instance = Model(numero=4.6)
    assert instance.numero == 4.6
    assert instance.to_dict() == {'numero': 4.6}


def test_boolean():
    Model = pyjo_model_from_structure({
        'buleano': {
            'type': 'boolean',
        }
    })

    with pytest.raises(ValueError) as err:
        Model(buleano='Ha!')
    assert str(err.value) == "Boolean value expected. Got \"Ha!\" instead"

    instance = Model(buleano='true')
    assert instance.buleano is True
    assert instance.to_dict() == {'buleano': True}

    instance = Model(buleano='false')
    assert instance.buleano is False

    instance = Model(buleano=False)
    assert instance.buleano is False

    instance = Model(buleano=0)
    assert instance.buleano is False

    instance = Model(buleano=1)
    assert instance.buleano is True

    instance = Model(buleano=5)
    assert instance.buleano is True

    instance = Model(buleano=-5)
    assert instance.buleano is False

    instance = Model(buleano=True)
    assert instance.buleano is True


def test_url():
    Model = pyjo_model_from_structure({
        'uerreelle': {
            'type': 'url',
        }
    })

    with pytest.raises(ValueError) as err:
        Model(uerreelle='Ha!')
    assert str(err.value) == "Ha! is not a valid URL."

    instance = Model(uerreelle='http://www.google.com')
    assert instance.uerreelle == 'http://www.google.com'
    assert instance.to_dict() == {'uerreelle': 'http://www.google.com'}


def test_array_simple():
    Model = pyjo_model_from_structure({
        'lista': {
            'type': 'array',
            'element': {
                'type': 'integer'
            }
        }
    })

    with pytest.raises(FieldTypeError) as err:
        Model(lista='asd')
    assert str(err.value) == "lista value is not of type list, given \"asd\""

    instance = Model(lista=[1, 2, 3])
    assert instance.lista == [1, 2, 3]
    assert instance.to_dict() == {'lista': [1, 2, 3]}


def test_array_cast_from_string():
    def array_cast(value):
        if isinstance(value, str):
            return value.split(',')
        return value

    array_field_props = BASE_FIELD_PROPERTIES['array']
    array_field_props['cast'] = array_cast
    integer_field_props = BASE_FIELD_PROPERTIES['integer']
    integer_field_props['cast'] = int  # Force cast to all int fields

    Model = pyjo_model_from_structure({
        'lista': {
            'type': 'array',
            'element': {
                'type': 'integer'
            }
        }
    }, fields_properties=dict(
        array=array_field_props,
        integer=integer_field_props,
    ))

    instance = Model(lista='1,2,3')
    assert instance.lista == [1, 2, 3]
    assert instance.to_dict() == {'lista': [1, 2, 3]}


def test_embedded():
    Model = pyjo_model_from_structure({
        'embeddato': {
            'type': 'embedded',
            'model': {
                'numero': {
                    'type': 'integer',
                    'max_value': 5,
                }
            }
        }
    })

    instance = Model(embeddato=dict(numero=3))
    assert instance.embeddato['numero'] == 3
    assert instance.to_dict() == {'embeddato': {'numero': 3}}

    with pytest.raises(InstanceValidationError) as err:
        Model(embeddato=dict(numero=11))

    assert str(err.value) == 'Value is bigger than max value: 11 > 5'
