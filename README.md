# Explorify

![Explorify webapp](/DOC/explorify.png?raw=true)

## Description
The aim of Explorify is to provide an interactive photograph-driven map experience 
to find the best spots to take the best photographs. Explorify leverage photos and metadata
from the open API of Flickr and uses unsupervised machine learning to extract the best spots,
represented as clusters learned using a multi-feature approach of DBSCAN. The project has a 
2-pronged approach, which includes backend logic and frontend visualization. This package 
contains code for the frontend and backend, respectively in `CODE/explorify_deploy` and `CODE/explorify`.

## Installation
The data has already been generated, you don't have to download it. You'll need to 
install a few pip requirements to run frontend or backend.
* If you want to run the frontend: pip -r requirements.txt in `CODE/explorify_deploy` 
* If you want to run the backend: pip -r requirements.txt in `CODE/explorify`

You will need a working web connection to run the frontend as the city data is hosted 
in an online MongoDB database.

## Execution
We already trained our clustering algorithm and you should run the frontend web 
application to visualize the Atlanta and Paris results. Go to `CODE/explorify_deploy` 
and follow "Getting started" instructions in the README.md of this folder to start the 
local webapp, run the follwing commands:
```
chmod 775 startup_local.sh
sh startup_local.sh
```

*(Useful)* An instance of this has been put online if needed: https://dva-explorify.herokuapp.com/

If you want to run the clustering algorithms in the backend, go to `CODE/explorify` 
and follow "Getting started" instructions in the README.md file:

Run the jupyter notebook `clustering/clustering.ipynb` to run clustering.
