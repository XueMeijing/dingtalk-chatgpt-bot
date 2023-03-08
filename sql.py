import sqlite3

DATABASE = 'database.db'

# 查询结果元组转字典
def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
      d[col[0]] = row[idx]
  return d

def init_db():
  db = sqlite3.connect(DATABASE, check_same_thread=False)
  cursor = db.cursor()
  create_table_query = '''  CREATE TABLE IF NOT EXISTS user(
                            id                TEXT PRIMARY KEY     NOT NULL,
                            name              TEXT                        ,
                            conversation_id   TEXT                 NOT NULL,
                            parent_id         TEXT                 NOT NULL,
                            create_at          timestamp            NOT NULL); '''
  cursor.execute(create_table_query)
  cursor.close()
  db.close()
  print('数据库初始化成功')

def get_db():
  db = sqlite3.connect(DATABASE, check_same_thread=False)
  db.row_factory = dict_factory
  return db

def query_db(query, args=(), one=False):
  db = get_db()
  cur = db.cursor()
  cur.execute(query, args)
  rv = cur.fetchall()
  db.commit()
  cur.close()
  db.close()
  return (rv[0] if rv else None) if one else rv

__all__ = [
  init_db,
  query_db
]