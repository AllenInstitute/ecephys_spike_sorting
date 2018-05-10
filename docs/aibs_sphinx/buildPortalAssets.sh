#!/bin/sh
echo "\n\n[rebuildPortalAssets.sh] Downloading latest npm package from internal npm registry..\n\n"
rm -rf ./node_modules 
rm -f ./static/external_assets/bundled.js  
npm install aibs-portal-assets --save --registry http://dev_resource:4873 
rm -f ./node_modules/aibs-portal-assets/dist/index.html  
cp ./node_modules/aibs-portal-assets/dist/bundled.js ./static/external_assets/bundled.js
echo "[rebuildPortalAssets.sh] Copied the new bundle to /static/external_assets..\n"