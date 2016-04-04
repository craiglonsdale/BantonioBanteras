import json
import time
from slackclient import SlackClient

def main():
    try:
        config = {}
        # Read in our config stuff
        with open('config.json', 'r') as f:
            config = json.load(f)
        sc = SlackClient(config["SlackApiKey"])
        if sc.rtm_connect():
            while True:
                print(sc.rtm_read())
                time.sleep(1)
        else:
            print("Issue connecting!!!")
    except FileNotFoundError as err:
        print(err)
main()
