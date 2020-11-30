# 🗄️  despinassy

Despinassy is a set of SQLAlchemy Database Schema collection made to be imported 
as a module by other python programs (see [erie](https://github.com/Sprtch/erie), 
[victoria](https://github.com/Sprtch/victoria), 
[huron](https://github.com/Sprtch/huron)).

This python package is made to be added to the `requirements.txt` of the other reposiories.

```txt
-e git+git://github.com/Sprtch/despinassy.git#egg=despinassy-pkg-tperale
```

Using this repository help to keep a centralized shared model between all the
application that implement testing.

## Testing

Run in a virtualenv `/venv/bin/pytest`.
