import argparse
import schedule
import datetime
import time
import requests
import validators

# One could have a more extensive way to perform all of our requests
REQUEST_LIST = ["listen_history", "tracks", "users"]

class AppException(Exception):
    def __init__(self, message):
        self.message = message

def setup_parser():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-url', type=str, default='http://127.0.0.1:8000',
                        help='The required url of the Fastapi, typically http://127.0.0.1:8000/')
    
    parser.add_argument('-schedule_date', type=str, default='13:00',
                        help='A string with the format XX:XX, with X being integers. By default it is set to 13:00')
    
    parser.add_argument('-nowait', action='store_true',
                        help='If true, does not schedule and executes immediatly ')

    return parser.parse_args()

##############################################################################



def onDailyRequest(t):
    # Parameter t is silent
    
    for request in REQUEST_LIST:
        requestUrl = args.url + "/" + request
        response = requests.get(requestUrl)
        print("Request: " + requestUrl)
        print(response.text)
        
        # Save each response in their appropriate database accordingly
        # TODO
        
    print("The daily request has been executed successfully!")


# Takes a list of arguments from the parser as an entry
def main(args):
    # Validate arguments
    if (not validators.url(args.url) ):
        raise AppException("Input URL does not have a correct format")

    try:
        time.strptime(args.schedule_date, '%H:%M')
    except ValueError:
        raise AppException("schedule_date does not have a valid format")  
        
    if args.nowait:
        onDailyRequest(0)
    else:
        schedule.every().day.at(args.schedule_date).do(onDailyRequest, "Fetching song history at " + args.schedule_date)
        
        while True:
            # This is a simple and not cost effective approach to run periodically,
            # but it works
            print("Current time: ")
            print(datetime.datetime.now())
            schedule.run_pending()
            time.sleep(60) # wait one minute
          
def test_parser_bad_inputs():
    try:
        main(["url", "BadUrl"])
        assert(False)
    except AppException:
        assert(True)
      
    
if __name__ == "__main__":    
    args = setup_parser()

    main(args)

    