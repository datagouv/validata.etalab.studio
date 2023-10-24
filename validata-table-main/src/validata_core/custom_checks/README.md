# Custom checks

Validata provides a validation service for tabular (csv, xsl, xslx) files against a [Table Schema](https://specs.frictionlessdata.io/table-schema/).
Standard checks allow to validate cell values against field schema definition:

- type: _string_, _number_, ...
- format: _email_, _uri_, _uuid_, ...
- constraints: _minimumLength_, _unicity_, _regexp_, ...

Some checks can't be expressed using current field properties, e.g. :

- is the cell value a valid phone number?
- is the cell value a valid french SIRET?
- ...

For these special cases, the [frictionless-py](https://github.com/frictionlessdata/frictionless-py/) library used by Validata allows to create [_custom checks_](https://v4.framework.frictionlessdata.io/docs/guides/validation-guide#custom-checks). Validata provides some _custom checks_ that can be added to the table schema using `custom_checks` property with the list of _custom check_ to apply.

```json
  "custom_checks": [
    {
      "name": "french-siret-value",
      "params": {
        "column": "idAttribuant"
      }
    },
    {
      "name": "french-siret-value",
      "params": {
        "column": "idBeneficiaire"
      }
    }
  ]
```

Excerpt from the [Subventions](https://gitlab.com/opendatafrance/scdl/schema-subventions/-/blob/master/schema.json) tableschema. _french-siret-value_ custom check is applied on two fields: `idAttribuant` and `idBeneficiaire`.

- a _custom check_ is referred by its id (`name` property)
- a _custom check_ is (generally) applied to one field (`column` property) to check cell values for this field
- a _custom check_ related to one field is automatically skipped if the column does not exist. For a multi-column custom check,
the check is automatically skipped if all the columns relatives to the custom check don't exist, except when explicitly mentioned otherwise. 
The validation behavior for missing columns is then left to the discretion of the `required` schema instruction. 
- a _custom check_ related to one field is automatically skipped on empty cells. For a multi-column custom check, 
the check is automatically skipped if any of the columns has an empty cell, except when explicitly mentioned otherwise. 
The validation behavior for empty cells is then left to the discretion of the `required` schema instruction. 

Custom checks are dynamically loaded by Validata core at the validation process starts, only custom checks used in schema are loaded.

## Available custom checks

Validata offer several ready-to-use custom checks. Most of them are already used in different schemas.

### `cohesive-column-values`

This custom check insures that, on a row, all cell belonging to a set of columns are all set or are all empty.

E.g. in [deliberations schema](https://gitlab.com/opendatafrance/scdl/deliberations/-/blob/master/schema.json):

```json
{
  "name": "cohesive-columns-value",
  "params": {
    "column": "BUDGET_ANNEE",
    "othercolumns": [
      "BUDGET_NOM"
    ]
  }
},
```

See custom check [source code](cohesive_columns_value.py).

### `compare_columns_value`

This custom check allows to compare cell values belonging to two different columns using one operator among operator among `<`, `<=`, `==`, `>=` and `>`.

E.g. in [deliberations schema](https://gitlab.com/opendatafrance/scdl/deliberations/-/blob/master/schema.json) to ensure that the deliberation registration date (`PREF_DATE`) is later than the date of approval (`DELIB_DATE`):

```json
{
  "name": "compare-columns-value",
  "params": {
    "column": "PREF_DATE",
    "op": ">=",
    "column2": "DELIB_DATE"
  }
}
```
If all the columns relative to this custom check are missing, then this custom check is ignored. 
If an empty cell occurs in one or both of the two columns related to this custom check, then this custom check is ignored.

See custom check [source code](compare_columns_value.py). It uses the [`simpleeval`](https://pypi.org/project/simpleeval/) library.

### `french_gps_coordinates`

This custom check ensures that the cell value is a valid pair of coordinates matching a
location in France (metropolitan, Guadeloupe, Martinique, Mayotte, Guyane, la Réunion).
This checks uses bounding boxes and therefore may yield false positives in regions close
to the border that are not in France.
Coordinates must be decimal numbers (with a dot as decimal separator) in the WGS84
system and format [lon,lat].
Two errors may be raised:
- ReversedFrenchGPSCoordinatesError if the coordinates appear in France but in the incorrect order [lat, lon].
- FrenchGPSCoordinatesError if the coordinates are not in France, no matter in which order.

E.g. in [IRVE schema](https://github.com/etalab/schema-irve/blob/master/schema.json) to
ensure that the `coordonneesXY` column contains valid coordinates located in France:

```json
{
  "name": "french-gps-coordinates",
  "params": {
    "column": "coordonneesXY"
  }
}
```

See custom check [source code](french_gps_coordinates.py)

### `french-siren-value`

This custom check insures that the cell value is a valid french [SIREN](https://www.insee.fr/fr/metadonnees/definition/c2047) number.

E.g. in [DAE schema](https://gitlab.com/arsante/atlasante/schema-dae/-/blob/master/schema.json) to ensure that 3 columns (`expt_siren`, `mt_siren` and `fab_siren`) contain only valid SIREN values:

```json
{
  "name":"french-siren-value",
  "params":{
    "column":"expt_siren"
  }
},
{
  "name":"french-siren-value",
  "params":{
    "column":"mnt_siren"
  }
},
{
  "name":"french-siren-value",
  "params":{
    "column":"fab_siren"
  }
}
```

See custom check [source code](french_siren_value.py). It uses the [`python-stdnum`](https://pypi.org/project/python-stdnum/) library.

### `french-siret-value`

This custom check insures that the cell value is a valid french [SIRET](https://www.insee.fr/fr/metadonnees/definition/c1841) number.

E.g. in [marchés publics schema](https://gitlab.com/opendatafrance/scdl/marches-publics/-/blob/master/schema.json):

```json
{
  "name": "french-siret-value",
  "params": {
    "column": "ACHETEURS_ID"
  }
}
```

See custom check [source code](french_siret_value.py). It uses the [`python-stdnum`](https://pypi.org/project/python-stdnum/) library.

### `nomenclature-actes-value`

This custom check insures that the cell value is a valid _acte de nomenclature_ as defined in this [spec document](http://www.moselle.gouv.fr/content/download/1107/7994/file/nomenclature.pdf).

E.g. in [deliberations schema](https://gitlab.com/opendatafrance/scdl/deliberations/-/blob/master/schema.json):

```json
{
  "name": "nomenclature-actes-value",
  "params": {
    "column": "DELIB_MATIERE_NOM"
  }
}
```

See custom check [source code](nomenclatures_actes_value.py).

### `opening-hours-value`

This custom cheks insures that the cell value is a valid _opening hours definition_ expression as specified by [OpenStreetMap](https://wiki.openstreetmap.org/wiki/Key:opening_hours).

See custom check [source code](opening_hours_value.py). It uses the [`opening_hours`](https://pypi.org/project/opening_hours/) library.

### `phone-number-value`

This custom check insures the cell value is a valid french or international formatted phone number.

See custom check [source code](phone_number_value.py). It uses the [`phonenumbers`](https://pypi.org/project/phonenumbers/) library.

### `sum-columns-value`

This custom check insures that a cell value is equals to the sum of other cell values.

E.g. in [deliberations schema](https://gitlab.com/opendatafrance/scdl/deliberations/-/blob/master/schema.json) to ensure that the effective vote number (`VOTE_REEL`) is the sum of the vote for (`VOTE_POUR`), vote against (`VOTE_CONTRE`) and abstain (`VOTE_ABSTENTION`)

```json
{
  "name": "sum-columns-value",
  "params": {
    "column": "VOTE_REEL",
    "columns": ["VOTE_POUR", "VOTE_CONTRE", "VOTE_ABSTENTION"]
  }
}
```

If all the columns relative to this custom check are missing, then this custom check is ignored. 
If an empty cell occurs in one or many of the columns related to this custom check, then this custom check is ignored. 

See custom check [source code](sum_columns_value.py).

### `year-interval-value`

This custom check insures that a cell value contains a year or a valid year interval (formatted `YYYY` or `YYYY/YYYY` respectively).
In case of a year interval, the second year must be greater than the first year.

E.g. in [deliberations schema](https://gitlab.com/opendatafrance/scdl/deliberations/-/blob/master/schema.json) to ensure that the budget year (`BUDGET_ANNEE`) is a valid year or year interval

```json
{
  "name": "year-interval-value",
  "params": {
    "column": "BUDGET_ANNEE",
    "allow-year-only": "yes"
  }
}
```

See custom check [source code](year_interval_value.py).

### `one-of-required`

This custom check ensures that for each row and for two given columns, at least one should be non-empty.
Both columns could contain values.
If one column is missing, then any missing value in the other one raises a validation error. 
If both columns are missing, then the validation fails with a "format-error".

E.g. in [subventions schema](https://gitlab.com/opendatafrance/scdl/schema-subventions/-/blob/master/schema.json) to ensure that 
the SIRET number (`idBeneficiaire`) or the RNA number (`RNABeneficiaire`) is filled.

```json
{
  "name": "one-of-required",
  "params": {
    "column": "idBeneficiaire",
    "column2": "RNABeneficiaire"
  }
}
```

See custom check [source code](one_of_required.py).



## Implement a new custom check

### Custom check related to one field

Custom checks related to one field are defined as new classes inherited from `CustomCheckSingleColumn(Check)` 
parent class. By default, the custom check is skipped on empty cells, and the custom check is skipped if the column 
relative to the custom check is missing.

To implement a new custom check related to one field, you can use `validata_core/custom_checks/french_siren_value.py` 
file as a template and adapt it to the expected custom check.

- Define a new class `NewCustomError` inherited the `errors.CellError` from frictionless, corresponding to a custom error related to this new custom check
- Define a new class `NewCustomCheck`  inherited from the `ValidataCustomChecksSingleColumn(Check)` parent class with:
  - class attributes:
    - `code` a string corresponding to the name of the new custom check which will be used in schemas
    - `possible_Errors` a list of `NewCustomError` classes
  - methods:
    - `_validate_start_(self)` inherited from the _validate_start() `CustomCheckSingleColumn` class method
    - `_validate_row(self, cell_value, row)`  inherited the _validate_row() `CustomCheckSingleColumn` class method


###  Custom check related to many fields

Custom checks related to many fields are defined as new classes inherited from the `CustomCheckkMultipleColumns(Check)` 
parent class. By default, the custom check is skipped on empty cells. To not skip custom check on empty cells,
a specific constructor and specific methods should be implemented (cf below).

- Define a new class `NewCustomError` inherited the `errors.CellError` from frictionless, corresponding to a custom error related to this new custom check
- Define a new class `NewCustomCheck`  inherited the `CustomCheckMultipleColumns(Check)` parent class with:
  - class attributes:
    - `code` a string corresponding to the name of the new custom check which will be used in schemas
    - `possible_Errors` a list of `NewCustomError` classes
  - constructor:
    - depends on the custom check
  - methods:
    - depends on the expected behavior with skip the custom check on empty cells

- Implement methods:
  - `_validate_start(self)` inherited from the _validate_start() method from `CustomCheckMultipleColumn` class
  - `_validate_row(self, cell_values, row)` inherited from the _validate_row() method from `CustomCheckMultipleColumn` class

- Optional: implement constructor
  - In some cases, it is needed to implement a constructor to define private instance attributes which will be used in the 
  implementation of the validate method for this specific custom check (ex: attribute `op` for `compare_columns_values` custom check)


#### Do not skip custom check on empty cell or missing columns

By default, custom check on multiple columns will be skipped on empty cells, and custom check will be skipped if all the columns relative to the custom check are missing.
If you want another behavior, tou will have to:

- Implement constructor
``` 
def __init__(self, descriptor=None):
  super().__init__(descriptor)
  self.__skip_empty_cells = False  # required
  self.__other_attributes = self.get('other_attributes') # optional attributes potentially used in methods below
```

- Implement methods:
  - `validate_start(self)` which overwrites the validate_start() method from `CustomCheckMultipleColumn` class
  - `validate_row(self, row)` which overwrites the validate_row() method from `CustomCheckMultipleColumn` class
