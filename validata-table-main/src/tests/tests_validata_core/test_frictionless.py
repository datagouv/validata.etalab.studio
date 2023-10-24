import frictionless


def test_stats_rows_metrics():

    schema = {
        "fields": [{"name": "id"}, {"name": "value", "constraints": {"required": True}}]
    }

    # tabular data: 5000 empty lines on 10000
    tabular_data = [["id", "value"]] + [
        [i, "" if i % 2 == 0 else "a"] for i in range(1, 11001)
    ]

    report = frictionless.validate_resource(tabular_data, schema=schema)
    # stats.rows is the analyzed row count
    # analysed row count depends on errors count limit
    # as soon as max errors count is reached, parsing stops.
    #
    # So stats rows can't be used for source rows count
    assert report["tasks"][0]["resource"]["stats"]["rows"] == 0
