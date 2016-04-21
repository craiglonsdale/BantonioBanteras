import os.path
from twython import Twython
# Load Slack history from all channels
def loadSlackHistory(sc, userMap, roomList):
    for userId, userName in userMap.items():
        print('Generating map for', userName)
        # If there isn't an existing file for the user, we create one
        if os.path.isfile(userName + '.txt') == False:
            print("Gathering slack history...")
            for room in roomList:
                method = 'groups.history' if room[0] == 'G' else 'channels.history'
                # Look up that users chat history
                history = sc.api_call(method, channel=room, count=1000)
                messages = []
                if history['has_more'] != True:
                    messages += [message for message in history['messages'] if userId == message.get('user')]
                    while(history['has_more']):
                        historyMessages = history['messages']
                        messages += [message for message in historyMessages if userId == message.get('user')]
                        history = sc.api_call(method, channel=room, latest=historyMessages[len(historyMessages) - 1]['ts'])
                        print('Writing tweets to: ', userName, '.txt', sep='')
                        with open(userName + '.txt', 'a') as f:
                            for message in messages:
                                f.write('%s.\n' % message['text'])
                                f.close()
# Load tweets from twitter stream
def loadTweets(config, userName, twitterId):
    CONSUMER_KEY = config["ConsumerKey"]
    CONSUMER_SECRET = config["ConsumerSecret"]
    ACCESS_KEY = config['AccessToken']
    ACCESS_SECRET = config['AccessTokenSecret']
    twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
    if os.path.isfile(userName + '_tweets' + '.txt') == False:
        userTimeline = twitter.get_user_timeline(screen_name=twitterId, count=200, include_retweets=False)
        messages = [tweetData.get('text') for tweetData in userTimeline]
        latestId = userTimeline[0].get('id')
        print("Gathering tweets...")
        for i in range(0, 15): ## iterate through remaining of 3200 tweets
            userTimeline = twitter.get_user_timeline(screen_name=twitterId, count=200, include_retweets=False, max_id=userTimeline[0].get('id'))
            messages += [tweetData.get('text') for tweetData in userTimeline]
        # Once we have all the data, write the latest ID, then data
        print('Writing tweets to: ', userName, '_tweets', '.txt', sep='')
        with open(userName + '_tweets' + '.txt', 'w') as f:
            f.write('%s\n' % latestId)
            for message in messages:
                f.write('%s.\n' % message)
            f.close()
