# Data

Structure of the .h5 files:
```
id_photo_1       # group type
    binary       # dataset type  
    embedding    # dataset type
    metadata     # attribute type
id_photo_2
    ...
```
See `../datasets/visualization.ipynb` for an example on how to read and use them.

## Annotations
Files in `annotations` folder are cvs files representing a pair of images and a label. The first two colums are the Flickr id of the images and the last column is the label "should the photos be clustered together?". These csv files are generated and downloaded manually in this folder using the `../annotatin` tool.

## Changes
You can use the `changes.ipynb` notebook to edit the h5 files instead of regenerating them from scratch using `../dataset` folder.