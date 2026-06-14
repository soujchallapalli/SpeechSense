import pytest
from speechsense.data.base_mongo import BaseMongoRepository


@pytest.fixture(autouse=True)
def testing_db():
    # Setup: Create a new instance of BaseMongoRepository for testing
    DB = BaseMongoRepository("testingDB")

    # Ensure the collection is empty before each test
    DB.empty_collection()

    # This is where the testing happens
    yield DB

    # Teardown: Clean up after the test
    DB.empty_collection()


# return none if there is no row with the given id
def test_get_row_none(testing_db):
    get_row = testing_db.get_by_id(1)
    assert get_row is None


# return the row if it exists
def test_get_row_exists(testing_db):
    testing_db.insert(1, {"name": "SpeechSenseUnitTest", "description": "A test row for unit testing."})
    get_row = testing_db.get_by_id(1)
    assert get_row == {"_id": 1, "name": "SpeechSenseUnitTest", "description": "A test row for unit testing."}


# return empty list if the DB is empty without failing
def test_get_all_rows_empty(testing_db):
    get_all_rows = testing_db.get_all()
    assert get_all_rows == []


# return all rows if the DB has data
def test_get_all_rows(testing_db):
    testing_db.insert(1, {"name": "SpeechSenseUnitTest", "description": "A test row for unit testing."})
    testing_db.insert(2, {"name": "AnotherTest", "description": "Another test row."})
    get_all_rows = testing_db.get_all()
    assert get_all_rows == [
        {"_id": 1, "name": "SpeechSenseUnitTest", "description": "A test row for unit testing."},
        {"_id": 2, "name": "AnotherTest", "description": "Another test row."},
    ]


# test insert row
def test_insert_row(testing_db):
    inserted_id = testing_db.insert(1, {"name": "SpeechSenseUnitTest", "description": "A test row for unit testing."})
    assert inserted_id == 1
    get_row = testing_db.get_by_id(1)
    assert get_row == {"_id": 1, "name": "SpeechSenseUnitTest", "description": "A test row for unit testing."}


# test update row
def test_update_row(testing_db):
    testing_db.insert(1, {"name": "SpeechSenseUnitTest", "description": "A test row for unit testing."})
    modified_count = testing_db.update(1, {"name": "UpdatedName", "description": "An updated test row."})
    assert modified_count == 1
    get_row = testing_db.get_by_id(1)
    assert get_row == {"_id": 1, "name": "UpdatedName", "description": "An updated test row."}


# test delete row
def test_delete_row(testing_db):
    testing_db.insert(1, {"name": "SpeechSenseUnitTest", "description": "A test row for unit testing."})
    deleted_count = testing_db.delete(1)
    assert deleted_count == 1
    get_row = testing_db.get_by_id(1)
    assert get_row is None


def test_empty_collection(testing_db):
    testing_db.insert(1, {"name": "SpeechSenseUnitTest", "description": "A test row for unit testing."})
    testing_db.insert(2, {"name": "AnotherTest", "description": "Another test row."})
    testing_db.empty_collection()
    get_all_rows = testing_db.get_all()
    assert get_all_rows == []
