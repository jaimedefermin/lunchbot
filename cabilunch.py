import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
from time import time
import random

env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'],'/slack/events',app)

client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']

counting = False
available=[]
lunchgroups = []
groups = 0

class GroupMessage:
    START_TEXT = {
        'type' : 'section',
        'text' : {
            'type': 'mrkdwn',
            'text':(
                'This will be your lunch group for today. \n\n'
                '*{} is in charge of making the reservations.*'.format(available)
            )
        }
    }

    DIVIDER = {'type': 'divider'}


    def __init__(self, channel, users):
        self.channel = channel
        self.users = users
        self.icon_emoji = ':ramen:'
        self.timestamp = ''

    def get_message(self):
        return {
            'ts' : self.timestamp,
            'channel': self.channel,
            'username' : 'Lunch Bot',
            'icon_emoji': self.icon_emoji,
            'leader' : self.users[0],
            'blocks':[
                self.START_TEXT,
                self.DIVIDER
            ]
        }
    
    

    

@slack_event_adapter.on('message')
def message(payLoad):
    #print(payLoad)
    global counting
    event = payLoad.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')

    if user_id != None and not (user_id in available) and BOT_ID != user_id and counting:
        if text.lower() == 'me' or text.lower() == 'yes':
            available.append(user_id)
            client.chat_postMessage(channel=channel_id, text=f'<@{user_id}> said yes')
            printable_users = [f"<@{user}> " for user in available]
            msg = "".join(printable_users)
            client.chat_postMessage(channel=channel_id, text=f'{msg}are comming')


#@app.shortcut("create_conversation")
def send_group_to_groupchat(users):
    #gm= GroupMessage(channel,users)
    #message = gm.get_message()
    #response = client.chat_postMessage(**message)
    #gm.timestamp = response['ts']

    global available
    print(users)
    client.conversations_open(users= users)





@app.route('/lunch-time', methods=['POST'])
def lunch_time():
    global counting
    counting = True
    data =request.form
    user_id = data.get('user_id')
    #print(data)
    channel_id =data.get('channel_id')
    client.chat_postMessage(channel=channel_id, text="""Hello, who's having lunch out today? Please reply "me" or "yes" if you would """)
    return Response(), 200

@app.route('/no-more-people', methods=['POST'])
def no_more_people():
    global groups
    global lunchgroups
    data =request.form
    channel_id =data.get('channel_id')
    user_id = data.get('user_id')
    global counting
    counting = False
    global available
    
    #response = client.conversations_open(users=available)

    nlunchers = len(available)
    if nlunchers <= 7:
        groups = 1
    elif nlunchers % 7 == 0:
        groups = nlunchers/7
    else:
        groups = int(nlunchers/7) +1
    
    ppl = int(nlunchers/groups)
    leftovers = nlunchers - ppl*groups
    index=0

    for i in range(0,groups):
        lunchgroups.append([])
        for j in range (0, ppl): 
            lunchgroups[i].append(available[index])
            index+=1
    if leftovers > 0:
        for i in range(0, leftovers):
            lunchgroups[i].append(available[ppl*groups + i+1])

            
                




    client.chat_postMessage(channel=channel_id, text="""We are no longer counting""")

    #debug
    for i in range(0,len(lunchgroups)):
            send_group_to_groupchat(lunchgroups[i])



    for i in range(1, groups+1):
        client.chat_postMessage(channel=channel_id, text="""The groups are as follows :""")
        gp = lunchgroups[i-1]
        client.chat_postMessage(channel=channel_id, text=f'Group{i}: ')
        for j in range(0,len(gp)):
            client.chat_postMessage(channel=channel_id, text=f'<@{gp[j]}>')
        leader=random.randint(0,len(gp))
        client.chat_postMessage(channel=channel_id, text=f'Leader for Group{i}: <@{gp[leader]}>')

        
    if nlunchers  < 1:
        client.chat_postMessage(channel=channel_id, text='No one is going out for lunch today')
    elif nlunchers == 1:
        client.chat_postMessage(channel=channel_id, text=f'Only <@{available[0]}> is having lunch out today :(')
        send_group_to_groupchat(available[0])
        #send_group_to_groupchat(f'@{available[0]}', available)
    else:
        client.chat_postMessage(channel=channel_id, text=f'{nlunchers} people are coming')
        for i in range(0, len(lunchgroups)):
            send_group_to_groupchat(lunchgroups[i])
        #send_group_to_groupchat(f'@{available[0]}', available)

    available.clear()
    return Response(), 200



if __name__ == "__main__":
    app.run(debug=True)