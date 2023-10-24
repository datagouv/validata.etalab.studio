# Errors

## frictionless errors by code

Validata transforms english frictionless error messages into
detailed french messages

- `blank-header-error`: one header name is missing
- `blank-row-error`: blank row detected
- `extra-cell-error`: supernumerary cell detected
- `type-error`: cell value doesn't conform to declared type - Validata provides
  a detailed message depending on the type to ease error fix)
- `constraint-error`: cell value doesn't conform to one or many defined [constraints](https://specs.frictionlessdata.io/table-schema/#constraints)
  - Validata provides a detailed message based on the infriged constraint(s)
  - in case of `pattern` constraint, error message content use schema field description

## Validata warnings and errors

In order to provide a better experience to tabular file providers, Validata use `sync_schema` frictionless option to ignore all errors relative to missing, misordered ou extranumerary columns.

These type of errors are reported as warnings by Validata:

- `missing-header-warn`: a column defined in the schema is not found in tabular data
- `extra-header-warn`: a column not defined in the schema is found in tabular data
- `disordered-header-warn`: column list doesn't follow schema order
  - this error is not emitted while there still missing or extra header warns

Validata handles a specific error when a missing header has a `required` contraint. In
this case, a `missing-required-header` error is reported.

### Custom checks

Validata extends frictionless, bringing additional checks (located in [custom-checks](custom-checks folder). Each check comes with or or more specific errors named as custom checks names.

For more information see [CUSTOM CHECKS](validata_core/custom_checks/README.md)
