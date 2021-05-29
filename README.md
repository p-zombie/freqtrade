To create an app from the setup section defined in your heroku.yml manifest, install the heroku-manifest plugin from the beta update channel:
```bash
heroku update beta
heroku plugins:install @heroku-cli/plugin-manifest
heroku create --manifest
git push heroku master
```
