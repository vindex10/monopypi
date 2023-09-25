# MonoPyPi

Spawn a Flask-based PyPi repo, which builds and serves local packages before falling back to pypi.org.


## Usage

```
# Install
pip install git+https://github.com/vindex10/monopypi

# Run assuming you are in the root of your monorepo
FLASK_APP="monopypi.app:app" flask run --port 8000
```

Install packages

```
pip install --index-url=http://127.0.0.1:8000 name-of-package
```


## Editable installs of the local packages

Run with an additional flag:

```
EDITABLE=true FLASK_APP="monopypi.app:app" flask run --port 8000
```

Install packages as before:

```
pip install --index-url=http://127.0.0.1:8000 name-of-package
```

Editable installs are based on pth files, similarly to what [pfmore/editables](https://github.com/pfmoore/editables) does.
In case of MonoPyPi we always assume `src/` project structure. This may be improved in future.


## Other arguments

```
# root of the monorepo, defaults to current workdir
ROOT_DIR="."

# cache dir contains built artifacts
CACHE_DIR=dist/
```
