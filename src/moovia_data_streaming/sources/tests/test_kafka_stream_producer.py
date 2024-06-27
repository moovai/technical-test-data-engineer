from unittest.mock import patch, Mock, MagicMock
from utils import set_full_package_path
set_full_package_path('src/moovia_data_streaming/sources/kafka_streaming')
from kafka_stream_producer import KafkaStreamProducer

ENDPOINT = "http://moovia:8000/users"
FETCH_DATA =[[
            {
              "id": 24817,
              "name": "second",
              "artist": "Thomas Duncan",
              "songwriters": "Catherine Brooks",
              "duration": "20:04",
              "genres": "approach",
              "album": "election",
              "created_at": "2023-09-22T16:59:35",
              "updated_at": "2024-04-23T07:24:46"
            }], 1] 

@patch('data_fetcher.Fetcher')
@patch('kafka.KafkaProducer')
def test_when_producing_data_to_topic_then_success(mock_fetcher, mock_Kafka_producer):
    #Arrange
    mock_logging = MagicMock()
    mock_fetcher.get_data.return_value = FETCH_DATA        
    mock_Kafka_producer.send.return_value = ''    
    mock_logging.error.return_value = ''    
    
    producer = KafkaStreamProducer(mock_fetcher, mock_Kafka_producer, mock_logging)            
    producer.set_topic_name("topic")

     #Act
    producer.produce()    

    #Assert
    mock_fetcher.get_data.assert_called()
    mock_Kafka_producer.send.assert_called()
    mock_Kafka_producer.flush.assert_called()
    mock_logging.error.assert_not_called()

