import json
import re
import time
from slackclient import SlackClient
# ['<@U0XKTUM2S>: <@U0255R6S3>']
def main():
    userRegex = re.compile('(<@[A-Z0-9]\w+>)');
    try:
        config = {}
        # Read in our config stuff
        with open('config.json', 'r') as f:
            config = json.load(f)
        userMap = {
            config['SlackBotId'] : 'bantonio'
        }
        print(userMap)
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
                            sc.rtm_send_message(channel='C0Q5816U9', message='Let the banter begin!')
                            # Check out our usermap to see if we recognise anyone else
                            if userMap.keys() in userRefs:
                                mappedUsers = [userMap.get(user) for user in userRefs if user in userMap.keys()]
                                sc.rtm_send_message(channel='C0Q5816U9', message='I see you mentioned')
                            else:
                                print('Adding referenced user')
                                newUsersId = [userRef for userRef in userRefs if userRef != config['SlackBotId']]
                                # Find the users details
                                print(newUsersId[0][2:-1])
                                newUserInfo = sc.api_call('users.info', user=newUsersId[0][2:-1])
                                print(newUserInfo)
                                userMap.update(newUsers)
                                print(userMap)
                time.sleep(1)
        else:
            print("Issue connecting!!!")
    except FileNotFoundError as err:
        print(err)
main()
