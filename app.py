from flask import Flask
import schedule, time
from flask_apscheduler import APScheduler
from resource.stockDB import start2
from flask_restful import Api



app = Flask(__name__) # 建立application 物件
api = Api(app)
aps = APScheduler()

class schedulerConfig(object):
    JOBS = [
      {
          'id': 'job1',
          'func': 'resource.stockDB:start2',
          'args': (),
          'trigger': 'interval',
          'seconds': 5
      }
    ]
    SCHEDULER_API_ENABLED = True

@app.route("/")
def index():
  return "hello world"

if __name__ == "__main__":
  app.debug = True
  app.config.from_object(schedulerConfig())
  aps.init_app(app)
  aps.start()
  app.run(host='0.0.0.0', port=80)