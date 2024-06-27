from typing import List
from abc import ABC, abstractmethod
import requests
import logging


class Fetcher(ABC):
   @abstractmethod
   def get_data(self) -> List:
      pass

class ApiDataFetcher(Fetcher):

  def __init__(self, log:logging, max_pages:int=10):
    self.endpoint = ""    
    self.log = log
    self.max_pages = max_pages  

  def set_endpoint(self, endpoint):
    self.endpoint = endpoint

  def set_max_pages(self, max_pages:int):
    self.max_pages = max_pages  

  def get_data(self) -> List:
      return self.get_all_data()        
  
  def get_data_by_page(self, page=1):         
    try:
      res = requests.get(f'{self.endpoint}?page={page}&size=100')
      if res.status_code == 200:
         res = res.json()
         res_items = res['items']  
         return res_items
      else:
        self.log.error('An error occurred when fetching data at endpoint: {self.endpoint} - page: {page}: %s', str(res.status_code))    
        return []
    except Exception as e:
     self.log.error('An error occurred when fetching data at endpoint: {self.endpoint} - page: {page}: %s', str(e))    
     return []
       
  def get_all_data(self):    
    result = []
    page = 1
    res_items = self.get_data_by_page(page)
    while len(res_items) > 0 and page <= self.max_pages:
      result.extend(res_items)
      page += 1
      res_items = self.get_data_by_page(page)
    return [result, page-1] 
