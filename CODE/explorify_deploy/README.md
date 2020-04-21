# Explorify - Frontend

This is the frontend application of Explorify. The front-end is served by a Flask application, using pymongo as the database driver.

app.py - defines the web-server
statics - contains js, css and image files
templates - contains html templates

The Client-side application is split into two parts, the landing page, located in templates/home, and the geojson viewer, located in templates/viewer.

## Getting started
Install frontend dependencies to run the Flask server hosting the webapp.
```
pip install -r requirements.txt
```

Run the server:
```
chmod 775 startup_local.sh
sh startup_local.sh
```
