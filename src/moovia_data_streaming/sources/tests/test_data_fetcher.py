from unittest.mock import patch, Mock, MagicMock
from utils import set_full_package_path
set_full_package_path('src/moovia_data_streaming/sources/api')
from data_fetcher import ApiDataFetcher

ENDPOINT = "http://moovia:8000/users"
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
            },
            {
              "id": 72733,
              "name": "difficult",
              "artist": "Lauren Johnson",
              "songwriters": "Brian Robinson",
              "duration": "23:07",
              "genres": "floor",
              "album": "arm",
              "created_at": "2023-10-14T00:33:41",
              "updated_at": "2023-12-08T06:23:55"
            }]

@patch('data_fetcher.requests')
def test_when_get_data_by_page_then_data_returned(mock_requests):
    #Arrange     
    mock_logging = MagicMock()     
    mock_logging.error.return_value = ''
    mock_response = MagicMock(status_code=200)    
    response_dict = {
          "items": EXPECTED_DATA
          }    
    mock_response.json.return_value = response_dict
    mock_requests.get.return_value = mock_response
    fetch = ApiDataFetcher(mock_logging, 1)         
    fetch.set_endpoint(ENDPOINT)

     #Act
    response = fetch.get_data_by_page()    

    #Assert
    mock_requests.get.assert_called_with(f'{ENDPOINT}?page=1&size=100')   
    mock_logging.error.assert_not_called()
    assert response == EXPECTED_DATA

@patch('data_fetcher.requests')
def test_when_get_all_with_no_data_returned_then_empty_arry_returned(mock_requests):
    #Arrange
    mock_logging = MagicMock()     
    mock_logging.error.return_value = ''
    mock_response = MagicMock(status_code=200)
    response_dict = {
          "items": []
          }    
    mock_response.json.return_value = response_dict    
    mock_requests.get.return_value = mock_response
    fetch = ApiDataFetcher(mock_logging, 1)      
    fetch.set_endpoint(ENDPOINT)
     
     #Act 
    response = fetch.get_all_data()    

    #Assert
    mock_requests.get.assert_called_with(f'{ENDPOINT}?page=1&size=100')   
    mock_logging.error.assert_not_called()
    assert response[0] == []
    assert response[1] == 0

@patch('data_fetcher.requests')
def test_when_get_all_with_status_code_not_200_then_log_message_return_empty_array(mock_requests):
    #Arrange
    mock_logging = MagicMock()     
    mock_logging.error.return_value = ''
    mock_response = MagicMock(status_code=500)
    response_dict = {
          "items": []
          }    
    mock_response.json.return_value = response_dict    
    mock_requests.get.return_value = mock_response
    fetch = ApiDataFetcher(mock_logging, 1)     
    fetch.set_endpoint(ENDPOINT)
     
     #Act 
    response = fetch.get_all_data()    

    #Assert
    mock_requests.get.assert_called_with(f'{ENDPOINT}?page=1&size=100')   
    mock_logging.error.assert_called()
    assert response[0] == []
    assert response[1] == 0

@patch('data_fetcher.requests')
def test_when_get_all_with_exception_then_log_message_return_empty_array(mock_requests):
    #Arrange
    mock_logging = MagicMock()     
    mock_logging.error.return_value = ''
  
    fetch = ApiDataFetcher(mock_logging, 1)    
    fetch.set_endpoint(ENDPOINT)
     
     #Act 
    response = fetch.get_all_data()    

    #Assert    
    mock_logging.error.assert_called()
    assert response[0] == []
    assert response[1] == 0



