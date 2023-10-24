# Validata Table

Validata Table is python package used as a tabular data validation service.

It includes four subpackages, where you can find their respective documentations :
- [`validata_core`](src/validata_core/README.md)
- [`validata_ui`](src/validata_ui/README.md)
- [`validata_api`](src/validata_api/README.md)
- `tests` used for testing the project

To keep track of the project's history, [Validata Table](https://gitlab.com/validata-table/validata-table) 
comes from the merge of four gitlab repositories :
- [Validata core](https://gitlab.com/validata-table/validata-core)
- [Validata UI](https://gitlab.com/validata-table/validata-ui)
- [Validata API](https://gitlab.com/validata-table/validata-api)
- [Validata Docker](https://gitlab.com/validata-table/validata-docker)

# Development

This project is based on [Docker](https://docs.docker.com) to use a local environement developement.

This project includes a Makefile, which allows you to run predefined actions 
by running specific commands.

Dependency management tool used : [Poetry version 1.6.1](https://python-poetry.org/docs/)

### Requirements

First install [Docker](https://docs.docker.com/install/) and [docker-compose](https://docs.docker.com/compose/) if not already done.


### Run on development local environment

Configuration is done by editing environment variables in `.env`, 
(see `.env.example` file to set `.env` file)

Warning: Docker env files do not support using quotes around variable values!

Launch the development local environment, thanks to the makefile command:
```bash
# in validata-table/
make serve_dev
```
This launches two docker containers:
- validata-api-dev
- validata-ui-dev

### Validata Table API (using `validata-api-dev` docker container)
To access to the API of Validata Table click on http://localhost:5000/

[Try Validata Table API](src/validata_api/README.md)

### Validata Table UI (using `validata-ui-dev` docker container)
To access to the API of Validata Table click on http://localhost:5001/

### Validata Table command line tool (using `validata-api-dev` docker container)
To use validata command line tool in the docker development environment, run:
  ```
  docker exec -it validata-api-dev bash
  validata --help
  ```

### Test
To launch tests in the development environment, run:
  ```make test```

# Run on preproduction

Configuration is done by editing environment variables in `.env`, 
(see `.env.example` file to set `.env` file)

Warning: Docker env files do not support using quotes around variable values !

Launch the production environment, thanks to the makefile command:
```bash
# in validata-table/
make serve_preprod
```


# Continuous Integration

The continuous integration is configured in `.gitlab-ci.yml` file

## Release a new version

On master branch :
- Update version in [pyproject.toml](pyproject.toml) and [CHANGELOG.md](CHANGELOG.md) files
- Commit changes using `Release` as commit message
- Create git tag (starting with "v" for the release) `git tag -a`
- Git push: `git push && git push --tags`
- Check that pypi package is created and container images for validata_ui and validata_api are well-built 
([validata-table pipelines](https://gitlab.com/validata-table/validata-table/-/pipelines))

Creating and pushing a new release will trigger the pipeline in order to automatically publish 
a new version of `validata-table` package and build a new container image.

This pipeline runs when a new tag under the format 'vX.X.X' is pushed.

# Run on production

Configuration is done by editing environment variables in `.env`, 
(see `.env.example` file to set `.env` file)

Warning: Docker env files do not support using quotes around variable values !

Launch the production environment, thanks to the makefile command:
```bash
# in validata-table/
make serve_prod
```

# Deploy
This project uses Docker to deploy it.

## Deploy to production
Not yet available
