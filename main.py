import json
import re
import time
from slackclient import SlackClient
# ['<@U0XKTUM2S>: <@U0255R6S3>']
def main():
    userMap = {
        'jimmyhillis' : '@U0255R6S3'
    }
    try:
        config = {}
        # Read in our config stuff
        with open('config.json', 'r') as f:
            config = json.load(f)
        sc = SlackClient(config['SlackApiKey'])
        if sc.rtm_connect():
            while True:
                inputCollection = sc.rtm_read()
                if len(inputCollection):
                    inputText = [input['text'] for input in inputCollection if input.get('text')]
                    # if '@U0XKTUM2S' in input.get('text', '')]
                    for blah in inputText:
                        print(re.search('^(<@)([A-Z0-9])\w+>', blah).group(0))
                    # if len(textForMe):
                    #     print(textForMe)
                    #     retVals = sc.api_call('channels.history',  channel='C0Q5816U9')
                    #     print([message['text'] for message in retVals['messages'] if 'jimmyhillis' in message['text']])
                time.sleep(1)
        else:
            print("Issue connecting!!!")
    except FileNotFoundError as err:
        print(err)
main()
