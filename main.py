import json
import time

from slackclient import SlackClient
from bantonio import Bantonio
def sanitizeUserId(userId):
    return userId[2:-1]
def findRoom(input):
    return input.get('channel')
def main():
    try:
        # Read in our config stuff
        with open('config.json', 'r') as f:
            config = json.load(f)
        sc = SlackClient(config['SlackApiKey'])
        bantonio = Bantonio(config, sc)
        bantonio.connect()
        bantonio.wait()
        while bantonio.state == 'waiting':
            bantonio.read()
            bantonio.parse()
            bantonio.update()
            time.sleep(1)
        # if 'brains' in input.get('text'):
        #     sc.api_call('files.upload', content=text, filename=userName + '.txt', filetype='text', title=userName, channels=channel)
        # elif 'twitter' in input.get('text'):
        #     twitterRegex = re.compile('twitter:(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9-_\.]+)');
        #     twitterHandle = twitterRegex.findall(input.get('text'))[0]
        #     content.loadTweets(config, userName, twitterHandle)
    except FileNotFoundError as err:
        print(err)
main()
