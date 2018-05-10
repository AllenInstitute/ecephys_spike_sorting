# aibs_sphinx
theme.conf, static, and template files for aibs-style sphinx documentation


## Portal Assets

### Automated Install
To re-build the common header/theme..

`$ cd project-root`

`$ sh ./buildPortalAssets.sh`. 

This shell script will add our _internal_ npm registry and install the npm package needed. Next, it will copy the bundled javascript file into the static/external_assets folder which sphinx requires in templates/portalHeader.html. 

### Manual Install
If you want to manually upgrade..

`$ cd project-root`

`$ rm -rf node_modules`

`$ npm set registry <url>`

Open package.json and increment the npm package

`$ npm install`

`$ cp node_modules/aibs-portal-assets/dist/bundled.js static/external_assets/bundled.js`. 

### Notes
Eventually, this bundled javascript file will be served through a web server.