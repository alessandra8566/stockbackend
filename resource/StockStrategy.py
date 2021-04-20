from flask_restful import Api, Resource


class StockStrategy(Resource):
  def __init__(self, df):
    self.df = df
  
  def sayhi(self):
    print("hello linebot")