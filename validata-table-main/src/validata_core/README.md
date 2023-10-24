# Validata_core

`validara_core` is a subpackage of `validata-table`, built over 
[frictionless-py](https://github.com/frictionlessdata/frictionless-py) which provides tabular data validation with:

- French error messages (see [ERRORS](./ERRORS.md))
- Custom checks to handle french specifics (see [CUSTOM CHECKS](validata_core/custom_checks/README.md))

`validara_core` is used by the subpackages `validata_ui` and `validata_api`.

It offers a command line tool `validata`


## Try validata command line tool

Start the docker development environment ...
```bash
make serve_dev
```
... and run:
  ``` bash
  docker exec -it validata-table bash
  validata --help
  ```

A complete list of error messages can be found in [ERRORS.md](./ERRORS.md)
