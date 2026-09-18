import csv
import os
import tempfile

import pytest

from src.database import Database


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.remove(path)  # let Database create it fresh
    db = Database(db_path=path)
    yield db
    if os.path.exists(path):
        os.remove(path)


def test_insert_and_retrieve_detection(temp_db):
    record_id = temp_db.insert_detection("MP09AB1234", 87.5, "car1.jpg")
    assert record_id == 1

    records = temp_db.all_records()
    assert len(records) == 1
    assert records[0].plate_text == "MP09AB1234"
    assert records[0].confidence == 87.5


def test_query_between_filters_by_date(temp_db):
    temp_db.insert_detection("MP09AB1234", 90.0, "car1.jpg")
    today = temp_db.all_records()[0].detected_at[:10]

    in_range = temp_db.query_between(today, today)
    out_of_range = temp_db.query_between("2000-01-01", "2000-01-02")

    assert len(in_range) == 1
    assert len(out_of_range) == 0


def test_export_to_csv_writes_expected_rows(temp_db):
    temp_db.insert_detection("DL5CAB9999", 75.0, "car2.jpg")
    records = temp_db.all_records()

    with tempfile.TemporaryDirectory() as tmp_dir:
        csv_path = os.path.join(tmp_dir, "out.csv")
        Database.export_to_csv(records, csv_path)

        with open(csv_path) as f:
            rows = list(csv.reader(f))
        assert rows[0] == ["id", "plate_text", "confidence", "source_file", "detected_at"]
        assert rows[1][1] == "DL5CAB9999"
