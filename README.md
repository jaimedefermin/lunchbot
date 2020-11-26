# lunchbot :ramen:
Slack bot that makes lunch groups of up to 7 people and chooses a person in charge of making a reservation for each group.

In order for the bot to work, a server must be provided in the slack api menu, as well as the token and signing secret in .env.

*For visual purposes a Demo of how the bot works has been provided. (lunchbot.mp4)*

## Bot commands.
- To start the bot use `/lunch-time`. The bot will ask who will be having lunch and those who respond will be noted.

- The command `/no-more-people` stops the count and sends a group message to each of the groups with the information they need.

## Issues.
- As of right now, there is no possibility in slack to delete group chats, and therefore we have the risk of repeating the groupchat name. An extended name has been provided, using round time, to mediate this problem. However it would have been preferable to have a delete option for bots.

- Additionally slack's legacy tokens are deprecated and therefore slack bots cannot execute commands. The bot would just post a message with the command name. This makes translating the code from command based to time based harder than expected.

  **Both these issues could be resolved with unofficial methods, however since these are not supported by slack I have chosen not to implement them.**

