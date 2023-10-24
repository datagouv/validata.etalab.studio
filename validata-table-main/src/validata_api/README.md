# Validata Table API

Web API for Validata Table

## Usage

You can use the online instance of Validata Table API:

- API: https://api.validata.etalab.studio/
- API docs: https://api.validata.etalab.studio/apidocs

## Run in local development environment

### Serve

Start the docker development environment ...

```bash
make serve_dev
```
... then open http://localhost:5001/

### Try the API

- Go on http://localhost:5001/apidocs
- On `̀GET` part, Click on "Try it out"
- Fill the `schema` and `file` required fields with some given url examples below

#### Example of Deliberations Schema
Schema to use: https://gitlab.com/opendatafrance/scdl/deliberations/-/raw/master/schema.json?ref_type=heads

Example of valid file: https://gitlab.com/opendatafrance/scdl/deliberations/-/raw/master/examples/Deliberations_ok.csv?ref_type=heads


#### Example Infrastructures de recharge pour véhicules électriques
Schema: https://schema.data.gouv.fr/schemas/etalab/schema-irve-statique/2.2.0/schema-statique.json

Example of unvalid file: https://opendata.paris.fr/explore/dataset/belib-points-de-recharge-pour-vehicules-electriques-donnees-statiques/download?format=csv&timezone=Europe/Berlin&use_labels_for_header=false
