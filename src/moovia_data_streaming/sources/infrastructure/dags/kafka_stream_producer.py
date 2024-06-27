from utils import set_full_package_path
set_full_package_path('src/moovia_data_streaming/sources/api')

from json import dumps
import logging
from data_fetcher import Fetcher
from stream_producer import StreamProducer
from kafka import KafkaProducer

class KafkaStreamProducer(StreamProducer):
  
  def __init__(self, fetcher: Fetcher, producer: KafkaProducer, log:logging):
    self.fetcher = fetcher
    self.producer = producer    
    self.log = log    
    self.topic_name = ""   

  def set_topic_name(self, topic_name):
      self.topic_name = topic_name

  def produce(self):      
      datas = self.fetcher.get_data()         
      for data in datas[0]:         
          try:
             self.producer.send(topic=self.topic_name, value=data)            
          except Exception as e:
            self.log.error('An error occurred when producing data to: {self.kafka_nodes} - topic: {self.topic_name}: %s', str(e))    
        
      self.producer.flush()
       