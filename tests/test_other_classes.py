import pytest
from pyjo.exceptions import RequiredFieldError

from pyjo_mdl import pyjo_model_from_structure, FullErrorValidation
from pyjo_mdl.exceptions import InstanceValidationError

__author__ = 'xelhark'


def test_full_error_validation():
    Model = pyjo_model_from_structure({
        'numero_1': {
            'type': 'integer',
            'min_value': 1,
            'max_value': 1,
        },
        'numero_2': {
            'type': 'integer',
            'min_value': 2,
            'max_value': 2,
        }
    }, base_class=FullErrorValidation)

    instance = Model(numero_1=1, numero_2=2)
    assert instance.numero_1 == 1

    with pytest.raises(InstanceValidationError) as err:
        Model(numero_1=2, numero_2=3)

    assert str(err.value) == 'Error validating instance.'
    assert len(err.value.errors_list) == 2
    assert str(err.value.errors_list[0]) == 'Error validating field \'numero_1\': Value is bigger than max value: 2 > 1'
    assert str(err.value.errors_list[1]) == 'Error validating field \'numero_2\': Value is bigger than max value: 3 > 2'


def test_full_error_validation_embedded_strings():
    Model = pyjo_model_from_structure({
        "muscle": {
            "type": "embedded",
            "model": {
                "name": {
                    "type": "string",
                },
                "group": {
                    "type": "string",
                    "values": [
                        "legs", "core", "arms", "pistulin"
                    ]
                }
            }
        },
    }, base_class=FullErrorValidation)
    # Make sure a valid model allows valid instances

    valid = Model(muscle={
        "name": "Bicipite",
        "group": "arms",
    })

    with pytest.raises(RequiredFieldError):
        Model()

    with pytest.raises(InstanceValidationError) as err:
        Model(muscle={"name": "Bicipite", "group": "brarms"})
    assert str(err.value.errors_list[0]) == 'Error validating field \'group\':' \
                                            ' Value brarms does not match any value' \
                                            ' in the enum list [legs, core, arms, pistulin]'


def test_type_error_array_of_strings():
    Model = pyjo_model_from_structure({
        "value": {
            "type": "array",
            "element": {
                "type": "integer"
            }
        }
    }, base_class=FullErrorValidation)

    # Make sure a valid model allows valid instances
    Model(value=[1, 2, 3])

    with pytest.raises(InstanceValidationError):
        Model.validate(dict())

    with pytest.raises(InstanceValidationError) as err:
        Model.validate(dict(value=[{'foo': "bar"}]))
    assert str(err.value) == 'Error validating instance.'
    assert str(err.value.errors_list[0]) == 'Error validating field \'value\':' \
                                            ' value inner field value is not of type int, given "{\'foo\': \'bar\'}"'
