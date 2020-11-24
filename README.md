# lunchbot :ramen:
Slack bot that makes lunch groups of up to 7 people and chooses a person in charge of making a reservation for each group.

In order for the bot to work, a server must be provided in the slack api menu, as well as the token and signing secret in .env.

## Bot commands.
- To start the bot use `/lunch-time`. The bot will ask who will be having lunch and those who respond will be noted.

- The command `/no-more-people` stops the count and sends a group message to each of the groups with the information they need.



