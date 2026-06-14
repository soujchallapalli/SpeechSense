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
    testing_db.insert({"_id": 1, "name": "SpeechSenseUnitTest"})
    get_row = testing_db.get_by_id(1)
    assert get_row == {"_id": 1, "name": "SpeechSenseUnitTest"}


# return empty list if the DB is empty without failing
def test_get_all_rows_empty(testing_db):
    testing_db.empty_collection()  # Ensure the collection is empty before the test
    get_all_rows = testing_db.get_all()
    assert get_all_rows == []


# return all rows if the DB has data
def test_get_all_rows(testing_db):
    testing_db.empty_collection()  # Ensure the collection is empty before the test
    testing_db.insert({"_id": 1, "name": "SpeechSenseUnitTest"})
    testing_db.insert({"_id": 2, "name": "AnotherTest"})
    get_all_rows = testing_db.get_all()
    assert get_all_rows == [{"_id": 1, "name": "SpeechSenseUnitTest"}, {"_id": 2, "name": "AnotherTest"}]


# test insert row
def test_insert_row(testing_db):
    inserted_id = testing_db.insert({"_id": 1, "name": "SpeechSenseUnitTest"})
    assert inserted_id == 1
    get_row = testing_db.get_by_id(1)
    assert get_row == {"_id": 1, "name": "SpeechSenseUnitTest"}


# test update row
def test_update_row(testing_db):
    testing_db.empty_collection()  # Ensure the collection is empty before the test
    testing_db.insert({"_id": 1, "name": "SpeechSenseUnitTest"})
    modified_count = testing_db.update(1, {"name": "UpdatedName"})
    assert modified_count == 1
    get_row = testing_db.get_by_id(1)
    assert get_row == {"_id": 1, "name": "UpdatedName"}


# test delete row
def test_delete_row(testing_db):
    testing_db.insert({"_id": 1, "name": "SpeechSenseUnitTest"})
    deleted_count = testing_db.delete(1)
    assert deleted_count == 1
    get_row = testing_db.get_by_id(1)
    assert get_row is None


def test_empty_collection(testing_db):
    testing_db.insert({"_id": 1, "name": "SpeechSenseUnitTest"})
    testing_db.insert({"_id": 2, "name": "AnotherTest"})
    testing_db.empty_collection()
    get_all_rows = testing_db.get_all()
    assert get_all_rows == []
