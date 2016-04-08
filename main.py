import json
import re
import time
import markovify
import os.path
from slackclient import SlackClient

userMap = {}
def sanitizeUserId(userId):
    return userId[2:-1]
def addUserToMap(sc, userId):
    # Find the users details and udpdated mapped users
    newUserInfo = sc.api_call('users.info', user=userId)
    userMap.update({userId: newUserInfo['user']['name']})
def findRoom(input):
    return input.get('channel')
def findUserRefences(input):
    userRegex = re.compile('(<@[A-Z0-9]\w+>)');
    inputText = input.get('text')
    if (inputText):
        return [sanitizeUserId(id) for id in userRegex.findall(inputText)]
    else:
        return []
def main():
    try:
        config = {}
        # Read in our config stuff
        with open('config.json', 'r') as f:
            config = json.load(f)
        userMap[config['SlackBotId']] = 'bantonio'
        sc = SlackClient(config['SlackApiKey'])
        if sc.rtm_connect():
            while True:
                inputCollection = sc.rtm_read()
                for input in inputCollection:
                    userRefs = findUserRefences(input)
                    room = findRoom(input)
                    # Only look for info if they are referencing bantonio
                    if config['SlackBotId'] in userRefs:
                        for userId in [ref for ref in userRefs if ref != config['SlackBotId']]:
                            if userMap.get(userId):
                                print('Delivering text for', userMap.get(userId))
                                with open(userMap[userId] + '.txt', 'r') as f:
                                    text = f.read();
                                    f.close()
                                textModel = markovify.Text(text)
                                sc.rtm_send_message(channel=room, message=userMap[userId] + ': `' + textModel.make_short_sentence(140) + '`')
                            else:
                                sc.rtm_send_message(channel=room, message="I'll read their chat history.")
                                addUserToMap(sc, userId)
                                # If there isn't an existing file for the user, we create one
                                if os.path.isfile(userMap[userId] + '.txt') == False:
                                    # Look up that users chat history
                                    history = sc.api_call('groups.history', channel='G04HQ5WHB')
                                    messages = []
                                    if history['has_more'] != True:
                                        messages += [message for message in history['messages'] if userId == message.get('user')]
                                    while(history['has_more']):
                                        historyMessages = history['messages']
                                        messages += [message for message in historyMessages if userId == message.get('user')]
                                        history = sc.api_call('groups.history', channel='G04HQ5WHB', latest=historyMessages[len(historyMessages) - 1]['ts'])
                                    with open(userMap[userId] + '.txt', 'w') as f:
                                        for message in messages:
                                            f.write('%s.\n' % message['text'])
                                        f.close()
                    elif userMap.get(input.get('user')):
                        # If we aresn't talking to bantio, we want to update the data we have on them
                        if input.get('text'):
                            print('Update content for', userMap[input['user']], input.get('text'))
                            with open(userMap[input['user']] + ".txt", "a") as f:
                                f.write('%s.\n' % input.get('text'))
                                f.close()
                time.sleep(1)
        else:
            print("Issue connecting!!!")
    except FileNotFoundError as err:
        print(err)
main()
