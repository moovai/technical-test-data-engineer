from abc import ABC, abstractmethod

class StreamConsumer(ABC):
   @abstractmethod
   def consume(self):
      pass