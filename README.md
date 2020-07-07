# gongish


An artistic HTTP router for Python


```python
from gongish import Application

app = Application()


@app.route('/hello/:name')
def get(name: str):
    return f'Hello {name}'

```

---

<center> <i>under construction</i> </center>
