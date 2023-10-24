import pytest
from validata_core.helpers import URLValidataResource, ValidataSourceError


def test_url_resource_without_meaningful_ext():
    url = "https://demo.data.gouv.fr/fr/datasets/r/d4d78089-f218-40b6-a86a-d7cc4e624b0c"
    validata_resource = URLValidataResource(url)
    with pytest.raises(ValidataSourceError) as vse:
        validata_resource.extract_tabular_data()
