# Instructions

1) install [conda](https://docs.conda.io/en/latest/)
2) `$ conda env create -f env.yml`
3) `$ conda activate flask_3004`
4) `$ python -m flask run`

# Update DB

1) `$ python -m flask db migrate -m "commit message" `
2) `$ python -m flask db upgrade`

- `alembic` should take care of copying everything over from one version of a table to another, 
but it usually breaks when running the above (e.g in the case when fields are renamed or added)  
- instead, erase the `app.db` and the scripts in `/migrations/versions`, and run the command above to create a new `db`