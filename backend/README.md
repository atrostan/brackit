

# Instructions

1) <s>install [conda](https://docs.conda.io/en/latest/)
2) `conda env create -f env.yml`
3) `conda activate flask_3004`
4) `python -m flask run`</s>

# UPDATE (using [`virtualenv`](https://virtualenv.pypa.io/en/latest/) for lighter environments)
1) Install [`virtualenv`](https://virtualenv.pypa.io/en/latest/installation.html)
2) `virtualenv venv`
3) `source venv/bin/activate`
4) `which pip`
    - make sure you're using `pip` from the activated virtual environment, and not your system's `pip`, or any other
    - should report something like `/home/alextrosta/Desktop/brackit/backend/venv/bin/pip`
5) `pip install -r requirements.txt`

# Update DB

1) `flask db migrate -m "commit message" `
2) `flask db upgrade`

- `alembic` should take care of copying everything over from one version of a table to another, 
but it usually breaks when running the above (e.g in the case when fields are renamed or added)  
- instead, erase the `app.db` and the scripts in `/migrations/versions`, and run the command above to create a new `db`
## TLDR:
```
rm ./migrations/versions/*.py
rm ./migrations/versions/__pycache__/*.pyc
rm ./app.db
flask db migrate -m "commit message"
flask db upgrade
```

# Populate DB

```
python mock_populate.py 
```

# Run
```
flask run
```

# Endpoints

- http://127.0.0.1:5000/user/1
- http://127.0.0.1:5000/tournament/1
- http://127.0.0.1:5000/bracket/1
- http://127.0.0.1:5000/round/1
- http://127.0.0.1:5000/match/1