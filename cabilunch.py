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
            if len(available)==1:
                client.chat_postMessage(channel=channel_id, text=f'{msg} is comming')
            else:
                client.chat_postMessage(channel=channel_id, text=f'{msg} are comming')


#@app.shortcut("create_conversation")
def send_group_to_groupchat(n, users):
    channel_name = f'lunch-group-{n}'
    response = client.conversations_create(name = channel_name, user_ids = users)
    channel_id = response["channel"]["id"]
    response = client.conversations_invite(channel=channel_id, users=users)
    leader = random.randint(0, len(users)-1)
    client.chat_postMessage(channel=channel_id, text=f'This is lunchgroup number {n}')
    client.chat_postMessage(channel=channel_id, text=f'The person in charge of making the reservation is <@{users[leader]}>')
    

@app.route('/lunch-time', methods=['POST'])
def lunch_time():
    global counting
    counting = True
    data =request.form
    channel_id =data.get('channel_id')
    client.chat_postMessage(channel=channel_id, text="""Hello, who's having lunch out today? Please reply "me" or "yes" if you would """)
    return Response(), 200

@app.route('/no-more-people', methods=['POST'])
def no_more_people():
    global groups
    global lunchgroups
    global available
    global counting

    data =request.form
    channel_id =data.get('channel_id')

    if counting == False:
        client.chat_postMessage(channel=channel_id, text= "You forgot to ask who was coming to lunch. Please type /lunch-time if you wish to ask the group :)")
    
    else:
        counting = False
        nlunchers = len(available)
        if nlunchers <= 7:
            groups = 1
        elif nlunchers % 7 == 0:
            groups = nlunchers/7
        else:
            groups = int(nlunchers/7) +1
        
        ppl = int(nlunchers/groups)
        leftovers = nlunchers - ppl*groups

        for i in range(0,groups):
            lunchgroups.append([])
            for _ in range(0,ppl):
                person = random.randint(0,len(available)-1)
                lunchgroups[i].append(available[person])
                del available[person]
        if leftovers > 0:
            for i in range(0, leftovers):
                lunchgroups[i].append(available[i])
                del available[i]

        client.chat_postMessage(channel=channel_id, text="""We are no longer counting""")
    
        if nlunchers  < 1:
            client.chat_postMessage(channel=channel_id, text='No one is going out for lunch today')
        elif nlunchers == 1:
            client.chat_postMessage(channel=channel_id, text=f'Only <@{lunchgroups[0][0]}> is having lunch out today :(')
            send_group_to_groupchat(1, lunchgroups[0])
        else:
            client.chat_postMessage(channel=channel_id, text=f'{nlunchers} people are coming')
            for i in range(0, len(lunchgroups)-1):
                send_group_to_groupchat(i+1, lunchgroups[i])   
    return Response(), 200



if __name__ == "__main__":
    app.run(debug=True)