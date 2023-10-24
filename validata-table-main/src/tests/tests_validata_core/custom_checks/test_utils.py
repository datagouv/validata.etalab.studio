from frictionless import Detector, errors, validate_resource
from validata_core.custom_checks.utils import CustomCheckSingleColumn, \
    CustomCheckMultipleColumns


def _schema_custom_check_test():
    return {
        "$schema": "https://frictionlessdata.io/schemas/table-schema.json",
        "fields": [
            {"name": "A", "type": "integer"},
            {"name": "B", "type": "integer"}
        ],
        "custom_checks": [
            {
                "name": "custom-check-single-column-test",
                "params": {"column": "A"}
            }
        ],
    }


class MockCustomCheckSingleColumn(CustomCheckSingleColumn):
    """ CustomCheckTest expects only `1` values"""

    code = "custom-check-single-column-test"

    def _validate_start(self):
        return []

    def _validate_row(self, cell_value, row):
        if cell_value != 1:
            yield errors.CellError.from_row(row, note="custom_check_single_column_test_error",
                                            field_name=self.get('column'))


def test_custom_check_single_column():
    schema = _schema_custom_check_test()

    # Test case: None value in column "A" -> ignore custom-check-single-column-test applied -> valid report
    source_valid = [["A", "B"], [None, 2]]
    report = validate_resource(source_valid, schema=schema,
                               checks=[MockCustomCheckSingleColumn(schema["custom_checks"][0]["params"])])
    assert report.valid

    # Test case: Correct value in column "A" -> do not ignore custom-check-single-column-test applied -> valid report
    source_valid = [["A", "B"], [1, 3]]
    report = validate_resource(source_valid, schema=schema,
                               checks=[MockCustomCheckSingleColumn(schema["custom_checks"][0]["params"])])
    assert report.valid

    # Test case: Incorrect value in column "A" ->  do not ignore custom-check-single-column-test applied -> invalid report
    source_invalid = [["A", "B"], [2, 3]]
    report = validate_resource(source_invalid, schema=schema,
                               checks=[MockCustomCheckSingleColumn(schema["custom_checks"][0]["params"])])
    assert not report.valid
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "cell-error"
    assert report["tasks"][0]["errors"][0]["note"] == "custom_check_single_column_test_error"


class MockCustomCheckMultipleColumn(CustomCheckMultipleColumns):
    """ CustomCheckTest expects only `2` as sum of all values columns"""

    code = "custom-check-multiple-columns-test"

    def _validate_start(self, all_columns):
        for col in all_columns:
            if col not in self.resource.schema.field_names:
                note = f"La colonne {col} n'est pas trouvée."
                yield errors.CheckError(note=f"{self.code}: {note}")

    def _validate_row(self, cell_values, row):
        if sum(cell_values) != 2:
            yield errors.CellError.from_row(row, note="custom_check_multiple_columns_test_error", field_name="A")


def test_custom_check_multiple_columns_validate_row1():
    # The custom check defined in the schema includes two columns : column and column2
    schema = _schema_custom_check_test()
    schema["custom_checks"][0]["name"] = "custom-check-multiple-columns-test"
    schema["custom_checks"][0]["params"]["column2"] = "B"

    # Test case: None value on column "A" or column "B" -> ignore custom-check-multiple-columns-test -> report valid
    sources = [
        [["A", "B"], [None, 3]],
        [["A", "B"], [3, None]]
    ]
    for source in sources:
        report = validate_resource(source, schema=schema,
                                   checks=[MockCustomCheckMultipleColumn(schema["custom_checks"][0]["params"])])
        assert report.valid

    # Test case: Incorrect values on column "A" and "B" -> custom-check-multiple-columns-test is applied -> invalid report
    sources = [
        [["A", "B"], [3, 1]],
        [["A", "B"], [1, 3]]
    ]
    for source in sources:
        report = validate_resource(source, schema=schema,
                                   checks=[MockCustomCheckMultipleColumn(schema["custom_checks"][0]["params"])])
        assert not report.valid
        assert len(report["tasks"][0]["errors"]) == 1
        assert report["tasks"][0]["errors"][0]["code"] == "cell-error"
        assert report["tasks"][0]["errors"][0]["note"] == "custom_check_multiple_columns_test_error"

    # Test case: Correct values on column "A" and "B" -> custom-check-multiple-columns-test is applied -> valid report
    source = [["A", "B"], [1, 1]]
    report = validate_resource(source, schema=schema,
                               checks=[MockCustomCheckMultipleColumn(schema["custom_checks"][0]["params"])])
    assert report.valid


def test_custom_check_multiple_columns_validate_row2():
    # The custom check defined in the schema includes more than two columns : column and other_columns
    schema = _schema_custom_check_test()
    schema["fields"].append({"name": "C", "type": "integer"})
    schema["custom_checks"][0]["name"] = "custom-check-multiple-columns-test"
    schema["custom_checks"][0]["params"]["othercolumns"] = ["B", "C"]

    # Test case: None value on column "A" or column "B" or column "C -> ignore custom-check-multiple-columns-test
    # -> report valid
    sources = [
        [["A", "B", "C"], [3, 1, None]],
        [["A", "B", "C"], [None, 1, None]],
        [["A", "B", "C"], [None, None, 3]],
    ]
    for source in sources:
        report = validate_resource(source, schema=schema,
                                   checks=[MockCustomCheckMultipleColumn(schema["custom_checks"][0]["params"])])
        assert report.valid

    # Test case: Incorrect values on columns "A", "B" and "C" -> custom-check-multiple-columns-test is applied
    # -> invalid report
    source = [["A", "B", "C"], [3, 1, 1]]
    report = validate_resource(source, schema=schema,
                               checks=[MockCustomCheckMultipleColumn(schema["custom_checks"][0]["params"])])
    assert not report.valid
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "cell-error"
    assert report["tasks"][0]["errors"][0]["note"] == "custom_check_multiple_columns_test_error"

    # Test case: Correct values on columns "A" and "B" and "C" -> custom-check-multiple-columns-test is applied -> valid report
    source = [["A", "B", "C"], [1, 1, 0]]
    report = validate_resource(source, schema=schema,
                               checks=[MockCustomCheckMultipleColumn(schema["custom_checks"][0]["params"])])
    assert report.valid


def test_custom_check_multiple_columns_validate_start1():
    schema = _schema_custom_check_test()
    schema["custom_checks"][0]["name"] = "custom-check-multiple-columns-test"
    schema["custom_checks"][0]["params"]["column2"] = "B"

    # Test case: wrong name on column "A" related to custom check
    source = [["aA", "B"], [3, 1]]
    report = validate_resource(source, schema=schema,
                               checks=[MockCustomCheckMultipleColumn(schema["custom_checks"][0]["params"])],
                               detector=Detector(schema_sync=True))
    assert not report.valid
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "check-error"
    assert "La colonne A n'est pas trouvée." in report["tasks"][0]["errors"][0]["note"]

    # Test case: wrong name on column "B" related to custom check
    source = [["A", "bB"], [3, 1]]
    report = validate_resource(source, schema=schema,
                               checks=[MockCustomCheckMultipleColumn(schema["custom_checks"][0]["params"])],
                               detector=Detector(schema_sync=True))
    assert not report.valid
    assert len(report["tasks"][0]["errors"]) == 1
    assert report["tasks"][0]["errors"][0]["code"] == "check-error"
    assert "La colonne B n'est pas trouvée." in report["tasks"][0]["errors"][0]["note"]

