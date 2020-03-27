from math import sqrt, ceil
import numpy as np

def make_tensor(images):
    """
    Turn a list of PIL images into a stacked of numpy arrays of same shape.

    Input:
    - images: list of PIL images
    Output:
    - Numpy array of shape (n_images, max_height, max_width)
    """
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