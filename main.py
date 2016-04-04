import json
import re
import time
from slackclient import SlackClient
# ['<@U0XKTUM2S>: <@U0255R6S3>']
def main():
    userRegex = re.compile('(<@[A-Z0-9]\w+>)');
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
                    messageWithUserRefs = [userRegex.findall(input) for input in inputText]
                    for userRefs in messageWithUserRefs:
                        # Find if the message is referencing Bantonio
                        if config['SlackBotId'] in userRefs:
                            sc.rtm_send_message(channel='C0Q5816U9', message='I see ya')
                time.sleep(1)
        else:
            print("Issue connecting!!!")
    except FileNotFoundError as err:
        print(err)
main()
