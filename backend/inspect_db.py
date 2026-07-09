from backend.src.config.database import engine
from sqlalchemy import inspect

insp = inspect(engine)
print('Tables:', insp.get_table_names())
if 'users' in insp.get_table_names():
    cols = insp.get_columns('users')
    for c in cols:
        print(c)
else:
    print('No users table')
