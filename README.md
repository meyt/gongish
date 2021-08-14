# gongish

A simple and fast HTTP framework for Python.

```python
from gongish import Application

app = Application()

@app.route("/hello/:name")
def get(name: str):
    return f"Hello {name}"

```

## Installation

```
pip install gongish
```

## Usage

### Quickstart

Create a module (for example ` `main.py` `) and define your first application.

```python
from gongish import Application
app = Application()

@app.route('/')
def get():
    return 'Index'

@app.route('/about')
def get():
    return 'About'
```

now serve the `app` with:

```bash
gongish serve main:app -b :8080
```

### Configuration

YAML is the configuration format we use as global app config which powered by
`pymlconf` .

 `production.yaml`

```yaml
debug: False
redis:
    host: localhost
    port: port
```

 `main.py`

```python
from gongish import Application

app = Application()

@app.text('/')
def get():
    return f'Redis Address: {app.config.redis.host}{app.config.redis.port}'

app.configure('production.yaml')
```

You can use OS environment variables inside config file:

```yaml
sqlite:
    path: %(HOME)/myappdb.sqlite
```

### Routing

Python decorators are used to define routes and the wrapped function name
must match with expected HTTP verb.

for example we want to call `POST /user` , the route definition must be like:

```python
@app.route('/user')
def post():
    return 'User created!'
```

Methods for routing:

1. Exact path

    ```python
    @app.route('/')
    def get():
        return 'Index'

    @app.route('/about')
    def get():
        return 'About'
    ```

2. Positional arguments

    ```python
    @app.route('/user/:user_id')
    def get(user_id):
        return f'Hi {}'

    @app.route('/user/:id/book/:id')
    def get(user_id, book_id):
        return f'User #{user_id} and Book #{book_id}'
    ```

3. Wildcard
    ```python
    @app.json('/user/*')
    def get(*args):
        return args

    @app.json('/user/book/*')
    def get(*args):
        return args
    ```

### Formatters

When the response is ready, at final stage it will wrap by a formatter.

Available formatters: `text` , `json` , `binary`

```python
from gongish import Application
app = Application()

@app.text('/')
def get():
    return 'Index'

@app.json('/user')
def get():
    return dict(name='John')
```

the `text` formatter used as default, but you can change it:

```python
from gongish import Application

class MyApp(Application):
    __default_formatter__ = Application.format_json

app = MyApp()

@app.route('/user')
def get():
    return dict(name='John')
```

or in very special cases:

```python
import yaml
from gongish import Application

app = Application()

def format_yaml(request, response):
    response.type = 'text/x-yaml'
    response.body = yaml.dump(response.body)

@app.route('/user', formatter=format_yaml)
def get():
    return dict(name='John')
```

### Exceptions

```python
from gongish import Application, HTTPNotFound, HTTPNoContent, HTTPFound

app = Application()

@app.route('/user/:id')
def get(user_id):
    if user_id == '0':
        raise HTTPNotFound

    return dict(name='John')

@app.route('/user/:id')
def put(user_id):
    raise HTTPNoContent

@app.route('/redirectme')
def get():
    raise HTTPFound('https://github.com')
```

Complete list available in `gongish/exceptions.py` .

### Streaming

You can use Python Generators as route handler:

```python
@app.route('/')
def get():
    yield 'First'
    yield 'Second'
```

with HTTP chunked data transfer:

```python
@app.binary('/')
@app.chunked
def get():
    yield b'First'
    yield b'Second'
```

### Static Server

You can serve static files inside a directory like:

```python
from gongish import Application

app = Application()
app.add_static('/public', '/var/www')
app.add_static('/another/public', '/var/www', default_document='index.html5')
```

> Note: Static file handler designed for some limited use cases. for large projects use web servers like `nginx` instead.


## Credits
- [rehttp](https://github.com/pylover/rehttp)
- [nanohttp](https://github.com/pylover/nanohttp)
- [pymlconf](https://github.com/pylover/pymlconf)
- [flask](https://github.com/pallets/flask)
