import pandas as pd
from flask_restful import Api, Resource
from resource.stock_tool.tool import createDB, generate_random_header
# from stock_tool.tool import createDB, generate_random_header
import datetime, schedule, requests, random, time
from io import StringIO
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout




# conn = createDB()
ses = None

def getToday( *args, **wargs):
  now_time = datetime.datetime.now().strftime('%Y%m%d')
  try:
    r = requests_post('https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date={}&type=ALLBUT0999'.format(now_time))
  except Exception as e:
    print('**WARRN: cannot get stock price at', now_time)
    print(e)
    return None
  
  content = r.text.replace('=', '')
  lines = content.split('\n')
  lines = list(filter(lambda l: len(l.split('",')) > 10, lines))
  content = "\n".join(lines)

  if content == '':
    return None
  
  df = pd.read_csv(StringIO(content))
  df = df.astype(str)
  df = df.apply(lambda s: s.str.replace(',', ''))
  df['date'] = pd.to_datetime(now_time)
  df = df.rename(columns={'證券代號':'stock_id'})
  df = df.set_index(['stock_id', 'date'])
  df = df.apply(lambda s:pd.to_numeric(s, errors='coerce'))
  df = df[df.columns[df.isnull().all() == False]]
  df = df[~df['收盤價'].isnull()]

  exist = table_exist(conn, 'price')
  ret = pd.read_sql('select * from price', conn, index_col=['stock_id', 'date']) if exist else pd.DataFrame()
  # add new df to the dataframe
  ret = ret.append(df)
  ret.reset_index(inplace=True)
  ret['stock_id'] = ret['stock_id'].astype(str)
  ret['date'] = pd.to_datetime(ret['date'])
  ret = ret.drop_duplicates(['stock_id', 'date'], keep='last')
  ret = ret.sort_values(['stock_id', 'date']).set_index(['stock_id', 'date'])
  # add the combined table
  ret.to_csv('backup.csv')
  try:
    ret.to_sql('price', conn, if_exists='replace')
    print("save success")
  except Exception as e:
    ret = pd.read_csv('backup.csv', parse_dates=['date'], dtype={'stock_id':str})
    ret['stock_id'] = ret['stock_id'].astype(str)
    ret.set_index(['stock_id', 'date'], inplace=True)
    ret.to_sql('price', conn, if_exists='replace')
    print(e)

def getRange( *args, **wargs):
  pass

def find_best_session():
  for i in range(10):
      try:
          print('獲取新的Session 第', i, '回合')
          headers = generate_random_header()
          ses = requests.Session()
          ses.get('https://www.twse.com.tw/zh/', headers=headers, timeout=10)
          ses.headers.update(headers)
          print('成功！')
          return ses
      except (ConnectionError, ReadTimeout) as error:
          print(error)
          print('失敗，10秒後重試')
          time.sleep(10)
          
  print('您的網頁IP已經被證交所封鎖，請更新IP來獲取解鎖')
  print("　手機：開啟飛航模式，再關閉，即可獲得新的IP")
  print("數據機：關閉然後重新打開數據機的電源")

def requests_post( *args1, **args2):
  
  # get current session
  if ses == None:
      ses = find_best_session()
      
  # download data
  i = 3
  while i >= 0:
      try:
          return ses.post(*args1, timeout=10, **args2)
      except (ConnectionError, ReadTimeout) as error:
          print(error)
          print('retry one more time after 60s', i, 'times left')
          time.sleep(60)
          ses = find_best_session()
          
      i -= 1
  return pd.DataFrame()

def add_to_sql():
  now_time = datetime.datetime.now().strftime('%Y%m%d')
  print('start crawl price from {}'.format(now_time))

  data = getToday()
  dfs = {}
  
  if data is None:
    print('fail, check if it is a holiday')
  elif isinstance(data, dict):
    if len(dfs) == 0:
      dfs = {i:pd.DataFrame() for i in data.keys()}
      for i, d in data.items():
        dfs[i] = dfs[i].append(d)
    else:
      df = df.append(data)
      print('success')

def table_exist( conn, table):
  return list(conn.execute("select count(*) from information_schema.tables where table_type='BASE TABLE' and table_name='{}'".format(table)))[0][0] == 1  

def start():
  schedule.every(5).seconds.do(start2)
  while True:
    schedule.run_pending()
    time.sleep(5)
  pass

def start2():
  print(datetime.datetime.now().strftime('%Y%m%d'))
