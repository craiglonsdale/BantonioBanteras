import re
import os.path
import content
import markovify
from transitions import Machine
class Bantonio(object):
    isConnected = False
    userMap = {}
    roomList = []
    botRefs = {}
    userInputs = {}
    actions = {}
    #Basic states
    states = ['asleep', 'waiting', 'reading', 'parsing', 'updating', 'loading content', 'generating content']
    transitions = [
        # HANDLING CONNECTION TO SLACK
        { 'trigger': 'connect', 'source': 'asleep', 'dest': 'loading content',
            'before': 'connect_slack', 'after': 'loadSlackHistory', 'unless': 'isSlackConnected'},
        # HANDLING INPUT FROM SLACK
        { 'trigger': 'read', 'source': 'waiting', 'dest': 'reading', 'before': 'readInput', 'conditions': 'isSlackConnected'},
        { 'trigger': 'parse', 'source': 'reading', 'dest': 'parsing', 'before': 'parseInput', 'conditions': 'isProccessingRequired'},
        { 'trigger': 'parse', 'source': 'reading', 'dest': 'parsing', 'conditions': 'isSlackConnected'},
        { 'trigger': 'update', 'source': 'parsing', 'dest': 'waiting', 'before': 'updateContent', 'conditions': 'isUpdatingRequired'},
        { 'trigger': 'update', 'source': 'parsing', 'dest': 'waiting', 'conditions': 'isSlackConnected'},
        # HANDLING WAIT SCENARIOS
        { 'trigger': 'wait', 'source': 'loading content', 'dest': 'waiting', 'conditions': 'isSlackConnected'},
        { 'trigger': 'wait', 'source': 'waiting', 'dest': 'waiting', 'conditions': 'isSlackConnected'},
        { 'trigger': 'generate content', 'source': 'waiting', 'dest': 'generating content', 'unless': 'isSlackConnected'}
    ]
    def isProccessingRequired(self): return len(self.botRefs) != 0
    def isUpdatingRequired(self): return len(self.userInputs) != 0
    def isSlackConnected(self): return self.isConnected
    def loadSlackHistory(self): content.loadSlackHistory(self.slackClient, self.userMap, self.roomList)
    def findAllUsers(self): return {user['id']: user['name'] for user in self.slackClient.api_call('users.list')['members']}

    def __init__(self, config, sc):
        #Store a copy of the config, we will need that later on
        self.config = config
        self.slackClient = sc
        self.machine = Machine(model=self, states=Bantonio.states, transitions=Bantonio.transitions, initial='asleep')
    def readInput(self):
        inputCollection = self.slackClient.rtm_read()
        for input in inputCollection:
            referencedUsers = self.findUserRefences(input)
            if (self.config['SlackBotId'] in referencedUsers):
                self.botRefs.update({userId: input for userId in referencedUsers if userId != self.config['SlackBotId']})
            elif (input.get('user') and input.get('text')):
                self.userInputs.update({input.get('user'): input.get('text')})
    def updateContent(self):
        for user, content in self.userInputs.items():
            print('Update content for', self.userMap[user], content)
            with open(self.userMap[user] + ".txt", "a") as f:
                f.write('%s.\n' % content)
                f.close()
        self.userInputs= {}
    def parseInput(self):
        for user, data in self.botRefs.items():
            room = data.get('channel')
            text = self.loadUserHistory(self.userMap[user]);
            textModel = markovify.Text(text)
            self.slackClient.rtm_send_message(channel=room, message=self.userMap[user] + ': `' + textModel.make_short_sentence(140) + '`')
        self.botRefs = {};
    def findAvailableRooms(self):
        # Get private groups that we have info about
        availableRooms = [group['id'] for group in self.slackClient.api_call('groups.list')['groups']]
        availableRooms += [channel['id'] for channel in self.slackClient.api_call('channels.list')['channels']]
        return availableRooms
    def findUserRefences(self, input):
        userRegex = re.compile('(<@[A-Z0-9]\w+>)');
        return [id[2:-1] for id in userRegex.findall(input['text'])] if (input.get('text')) else []
    def connect_slack(self):
        print('Collecting Slack Details')
        self.isConnected = self.slackClient.rtm_connect()
        self.userMap = self.findAllUsers()
        self.roomList = self.findAvailableRooms()
    def loadUserHistory(self, userName):
        # User regular chat to seed the user text
        with open(userName + '.txt', 'r') as f:
            text = f.read();
            f.close()
        # Add in twitter text if we have any available
        if os.path.isfile(userName + '_tweets' + '.txt'):
            with open(userName + '_tweets' + '.txt', 'r') as f:
                text += f.read()
                f.close()
        return text
