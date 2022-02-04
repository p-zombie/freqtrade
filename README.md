# Freqtrade
Automatically deploy freqtrade to a remote Docker host and auto update strategies.
I've been using it to automatically deploy to vultr, but you can use it with any provider of your choice, as long as you have a docker host running.

### Requirements
* First of all, you need a docker host to deploy the app, like https://www.vultr.com/docs/one-click-docker/ or any other provider you want.
* Then, you need to have a docker hub account
* Optionally, you may setup a telegram bot to receive deployment messages.

Once you have everything above, fork the repo, then you'll need to setup a few GitHub secrets to make it work:
### Github Secrets
* DOCKER_USERNAME -- docker hub username
* DOCKER_PASSWORD -- docker hub password
* DOCKER_HOST -- used by https://github.com/wshihadeh/docker-deployment-action
* DOCKER_SSH_PRIVATE_KEY -- used by https://github.com/wshihadeh/docker-deployment-action
* DOCKER_SSH_PUBLIC_KEY -- used by https://github.com/wshihadeh/docker-deployment-action
* TELEGRAM_TO -- chat id which will receive deployment messages
* TELEGRAM_TOKEN -- telegram bot token
* GH_PAT -- personal GitHub token, used by https://github.com/p-zombie/freqtrade/blob/master/.github/workflows/update_strat.yml

### Workflow
Every-time you commit something to the repo, it will trigger a new docker build and push the image to docker hub (https://github.com/p-zombie/freqtrade/blob/master/.github/workflows/main.yml), and it will deploy production.yml to the host you setup using a docker deployment action. 

*PS; you may need to modify production.yml and change the image name to match your docker hub username, if not, it will use the image under my username.*

I also added a scheduled job to run using GitHub actions: https://github.com/p-zombie/freqtrade/blob/master/.github/workflows/update_strat.yml
it is set to run every minute but GitHub actually runs it about every 5 minutes; it pulls strategies, blacklists and pairlist files from https://github.com/iterativv/NostalgiaForInfinity and if the files changed, it will commit to the repo, which will trigger a new deploy and send a message in the telegram chat specified in the secrets.

That's about it, the hardest part is probably setting up the secrets for docker-deployment-action, but it should be pretty straightforward. I also added a docker prune file to prevent docker cache consuming all space in your docker host, copy to your docker host and run chmod +x docker-prune && mv docker-prune /etc/cron.daily and it should run every day.

if you plan to run it locally, it works exactly as the heroku repo, take a look at the makefile to check the available commands, or simply run make or make help to get a list of commands.

**Feel free to open an Issue if you need help to setup this repo or if you find any issues.**
