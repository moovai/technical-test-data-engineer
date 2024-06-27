from unittest.mock import patch, Mock, MagicMock
from utils import set_full_package_path
set_full_package_path('src/moovia_data_streaming/sources/kafka_streaming')
from kafka_stream_consumer import KafkaStreamConsumer

EXPECTED_DATA = [
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
            }] 

@patch('kafka.KafkaConsumer')
def test_when_consuming_no_data_to_topic_then_empty_data_returned(mock_Kafka_consumer):
    #Arrange
    mock_logging = MagicMock()     
    mock_logging.error.return_value = ''    
    mock_Kafka_consumer.poll.return_value = None  

    consumer = KafkaStreamConsumer(mock_Kafka_consumer, mock_logging)            
    consumer.set_topic_name("topic")

     #Act
    result = consumer.consume()    

    #Assert
    mock_Kafka_consumer.subscribe.assert_called_with(["topic"])
    mock_Kafka_consumer.poll.assert_called()
    mock_Kafka_consumer.close.assert_called()
    mock_logging.error.assert_not_called()
    assert result == []

@patch('kafka.KafkaConsumer')
def test_when_consuming_data_to_topic_then_data_returned(mock_Kafka_consumer):
    #Arrange
    mock_logging = MagicMock()     
    mock_logging.error.return_value = ''    

    mock_poll_message = MagicMock()     
    mock_poll_message.error.return_value = False 
    mock_poll_message.value.return_value = EXPECTED_DATA[0] 
    mock_Kafka_consumer.poll.return_value = mock_poll_message

    consumer = KafkaStreamConsumer(mock_Kafka_consumer, mock_logging)            
    consumer.set_topic_name("topic")

     #Act
    result = consumer.consume()    

    #Assert
    mock_Kafka_consumer.subscribe.assert_called_with(["topic"])
    mock_Kafka_consumer.poll.assert_called()
    mock_Kafka_consumer.close.assert_called()
    mock_logging.error.assert_not_called()
    assert result == EXPECTED_DATA   

@patch('kafka.KafkaConsumer')
def test_when_consuming_data_to_topic_with_message_error_then_empty_data_returned(mock_Kafka_consumer):
    #Arrange
    mock_logging = MagicMock()     
    mock_logging.error.return_value = ''    

    mock_poll_message = MagicMock()     
    mock_poll_message.error.return_value = True 
    mock_poll_message.value.return_value = EXPECTED_DATA[0] 
    mock_Kafka_consumer.poll.return_value = mock_poll_message

    consumer = KafkaStreamConsumer(mock_Kafka_consumer, mock_logging)            
    consumer.set_topic_name("topic")

     #Act
    result = consumer.consume()    

    #Assert
    mock_Kafka_consumer.subscribe.assert_called_with(["topic"])
    mock_Kafka_consumer.poll.assert_called()
    mock_Kafka_consumer.close.assert_called()
    mock_logging.error.assert_called()
    assert result == []   
    
@patch('kafka.KafkaConsumer')
def test_when_consuming_data_to_topic_with_exception_then_empty_data_returned(mock_Kafka_consumer):
    #Arrange
    mock_logging = MagicMock()     
    mock_logging.error.return_value = ''    

    mock_poll_message = MagicMock()
    mock_poll_message.value.return_value = EXPECTED_DATA[0] 
    mock_Kafka_consumer.poll.return_value = mock_poll_message

    consumer = KafkaStreamConsumer(mock_Kafka_consumer, mock_logging)            
    consumer.set_topic_name("topic")

     #Act
    result = consumer.consume()    

    #Assert
    mock_Kafka_consumer.subscribe.assert_called_with(["topic"])
    mock_Kafka_consumer.poll.assert_called()
    mock_Kafka_consumer.close.assert_called()
    mock_logging.error.assert_called()
    assert result == []   
