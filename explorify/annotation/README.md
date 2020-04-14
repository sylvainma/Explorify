Annotations
===========
A web interface to collect annotations for the clustering task. Pairs of photos will be shown and the user has to decided whether or not they should be in the same cluster. This decision have to be based on location and visual similarity first. Other metadata can help to further decide.

## Data to annotate
Provide a `data.geojson` file in the directory.

## Download
When the user annotated, he has to download the CSV file of annotations using the buttons in the header. Otherwise annotations are lost.

## Start webapp
```
python main.py
```