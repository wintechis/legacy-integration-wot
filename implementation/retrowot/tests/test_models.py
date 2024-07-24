from retrowot.thing_description.models import (
    Form,
    InteractionAffordance,
    ThingDescription,
)


def test_form_to_dict():
    form_data = {
        "contentType": "application/json",
        "href": "https://example.com/api",
        "operation": "readproperty",
        "parameters": {"param1": "value1", "param2": "value2"},
    }
    form = Form(**form_data)
    expected_result = {
        "contentType": "application/json",
        "href": "https://example.com/api",
        "operation": "readproperty",
        "parameters": {},
    }
    
    print(form.to_dict({})
    assert form.to_dict({}) == expected_result


def test_form_to_dict_with_instance_parameters():
    form_data = {
        "contentType": "application/json",
        "href": "https://example.com/api",
        "operation": "readproperty",
        "parameters": {"param1": "value1", "param2": "value2"},
    }
    form = Form(**form_data)
    instance_parameters = {"param1": "new_value1", "param3": "value3"}
    expected_result = {
        "contentType": "application/json",
        "href": "https://example.com/api",
        "operation": "readproperty",
        "parameters": {"param1": "new_value1", "param2": "value2", "param3": "value3"},
    }
    assert form.to_dict(instance_parameters) == expected_result


def test_form_to_dict_with_empty_parameters():
    form_data = {
        "contentType": "application/json",
        "href": "https://example.com/api",
        "operation": "readproperty",
        "parameters": {},
    }
    form = Form(**form_data)
    instance_parameters = {"param1": "value1", "param2": "value2"}
    expected_result = {
        "contentType": "application/json",
        "href": "https://example.com/api",
        "operation": "readproperty",
        "parameters": {"param1": "value1", "param2": "value2"},
    }
    assert form.to_dict(instance_parameters) == expected_result


def test_form_to_dict_with_no_instance_parameters():
    form_data = {
        "contentType": "application/json",
        "href": "https://example.com/api",
        "operation": "readproperty",
        "parameters": {"param1": "value1", "param2": "value2"},
    }
    form = Form(**form_data)
    expected_result = {
        "contentType": "application/json",
        "href": "https://example.com/api",
        "operation": "readproperty",
        "parameters": {"param1": "value1", "param2": "value2"},
    }
    assert form.to_dict({}) == expected_result
