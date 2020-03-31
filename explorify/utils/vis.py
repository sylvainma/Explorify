from math import sqrt, ceil
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid
import numpy as np
import PIL
from PIL import Image

def thumb_grid(im_list, grid_shape, txt_list=[], scale=1, axes_pad=0.01):
    """Display a grid of thumbnails from a list of PIL images"""
    # To numpy
    im_list = [np.array(im) for im in im_list]

    # Grid must be 2D:
    assert len(grid_shape) == 2

    # Make sure all images can fit in grid:
    assert np.prod(grid_shape) >= len(im_list)

    grid = ImageGrid(plt.gcf(), 111, grid_shape, axes_pad=(axes_pad, axes_pad+0.28))
    for i in range(len(im_list)):
        data_orig = im_list[i]
        text = txt_list[i] if len(txt_list) > 0 else ""

        # Scale image:
        im = PIL.Image.fromarray(data_orig)
        thumb_shape = [int(scale*j) for j in im.size]
        im.thumbnail(thumb_shape, PIL.Image.ANTIALIAS)
        data_thumb = np.array(im)
        grid[i].imshow(data_thumb)
        grid[i].set_title(text)

        # Turn off axes:
        grid[i].axes.get_xaxis().set_visible(False)
        grid[i].axes.get_yaxis().set_visible(False)

    for i in range(np.prod(grid_shape)):
      grid[int(i)].axis('off')
    
    return plt.gcf()

def make_tensor(images, target_width=200):
    """
    Turn a list of PIL images into a stacked of numpy arrays of same shape.

    Input:
    - images: list of PIL images
    Output:
    - Numpy array of shape (n_images, max_height, max_width)
    """
    target_sizes = [(target_width, int(target_width*im.size[1]/im.size[0])) for im in images]
    images = [im.resize(s, Image.ANTIALIAS) for im, s in zip(images, target_sizes)]
    arrays = [np.asarray(img.convert("RGB")) for img in images]
    max_width = max(img.shape[1] for img in arrays)
    max_height = max(img.shape[0] for img in arrays)
    arrays = [np.pad(t, (
        (0,max_height-t.shape[0]),
        (0,max_width-t.shape[1]), 
        (0,0)
    ), constant_values=0) for t in arrays]
    return np.stack(arrays, axis=0)

def visualize_grid(Xs, ubound=255.0, padding=1):
  """
  Reshape a 4D tensor of image data to a grid for easy visualization.

  Inputs:
  - Xs: Data of shape (N, H, W, C)
  - ubound: Output grid will have values scaled to the range [0, ubound]
  - padding: The number of blank pixels between elements of the grid
  """
  (N, H, W, C) = Xs.shape
  grid_size = int(ceil(sqrt(N)))
  grid_height = H * grid_size + padding * (grid_size - 1)
  grid_width = W * grid_size + padding * (grid_size - 1)
  grid = np.zeros((grid_height, grid_width, C))
  next_idx = 0
  y0, y1 = 0, H
  for y in range(grid_size):
    x0, x1 = 0, W
    for x in range(grid_size):
      if next_idx < N:
        img = Xs[next_idx]
        low, high = np.min(img), np.max(img)
        grid[y0:y1, x0:x1] = ubound * (img - low) / (high - low)
        # grid[y0:y1, x0:x1] = Xs[next_idx]
        next_idx += 1
      x0 += W + padding
      x1 += W + padding
    y0 += H + padding
    y1 += H + padding
  # grid_max = np.max(grid)
  # grid_min = np.min(grid)
  # grid = ubound * (grid - grid_min) / (grid_max - grid_min)
  return grid