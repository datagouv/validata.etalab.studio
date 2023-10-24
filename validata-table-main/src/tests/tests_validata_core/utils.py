def check_invalid_report_with_one_single_error(report):
    errors = report["tasks"][0]["errors"]
    assert not report.valid
    assert len(errors) == 1
    assert report["stats"]["errors"] == 1
    assert report["stats"]["tasks"] == 1

    return errors[0]
