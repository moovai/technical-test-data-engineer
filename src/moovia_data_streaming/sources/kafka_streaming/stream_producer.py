from abc import ABC, abstractmethod

class StreamProducer(ABC):
   @abstractmethod
   def produce(self):
      pass