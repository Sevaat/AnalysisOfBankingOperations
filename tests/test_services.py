import json

import src.services as services


def test_simple_search(sample_operations):
    result = services.simple_search(sample_operations, "")
    assert json.loads(result) == sample_operations


def test_search_in_description(sample_operations):
    result = services.simple_search(sample_operations, "интернета")
    assert json.loads(result) == [sample_operations[1]]


def test_search_in_category(sample_operations):
    result = services.simple_search(sample_operations, "еда")
    assert json.loads(result) == [sample_operations[0]]


def test_case_insensitive(sample_operations):
    result = services.simple_search(sample_operations, "КИНО")
    assert json.loads(result) == [sample_operations[2]]


def test_no_matches(sample_operations):
    result = services.simple_search(sample_operations, "путешествие")
    assert json.loads(result) == []


def test_multiple_matches(sample_operations):
    operations = sample_operations + [{"id": 6, "Описание": "Ресторан", "Категория": "Еда", "amount": 2000}]
    result = services.simple_search(operations, "еда")
    assert len(json.loads(result)) == 2
    assert json.loads(result)[0]["id"] == 1
    assert json.loads(result)[1]["id"] == 6


def test_missing_fields(sample_operations):
    result = services.simple_search(sample_operations, "такси")
    assert json.loads(result) == [sample_operations[4]]


def test_english_fields_not_found(sample_operations):
    result = services.simple_search(sample_operations, "coffee")
    assert json.loads(result) == []


def test_duplicate_prevention(sample_operations):
    modified_ops = sample_operations.copy()
    modified_ops.append({"id": 7, "Описание": "Супермаркет", "Категория": "Супермаркет", "amount": 1000})
    result = services.simple_search(modified_ops, "супермаркет")
    assert len(json.loads(result)) == 1


def test_invalid_operations_data():
    invalid_data = [{"id": 1}, "not_a_dict", None]
    result = services.simple_search(invalid_data, "test")
    assert result == json.dumps(invalid_data)


def test_non_dict_operations():
    result = services.simple_search([1, 2, 3], "test")
    assert result == json.dumps([1, 2, 3])
