import logging
from kafka import KafkaConsumer
from stream_consumer import StreamConsumer

class KafkaStreamConsumer(StreamConsumer):
  
  def __init__(self, consumer:KafkaConsumer, log:logging):        
    self.consumer = consumer
    self.log = log
    self.topic_name = ""    

  def set_topic_name(self, topic_name):
      self.topic_name = topic_name  

  def consume(self):      
      self.consumer.subscribe([self.topic_name])
      messages = []
      #while True:
      try:
        message = self.consumer.poll(max_records=100)
        if not message:            
            return messages

        if message.error():
            self.log.error('An error occurred when consuming message from to: {self.kafka_nodes} - topic: {self.topic_name}: %s', str(message.error()))                                   
            return messages
        messages.append(message.value())#.decode('utf-8'))
        return messages
      except Exception as e:
        self.log.error('An error occurred when consuming message from to: {self.kafka_nodes} - topic: {self.topic_name}: %s', str(e))                
      finally:
        self.consumer.close()  
      return messages               