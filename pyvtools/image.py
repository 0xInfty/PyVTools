import os
import numpy as np
from skimage.metrics import structural_similarity
from math import log10, sqrt
import matplotlib.pyplot as plt

#%% GLOBAL VARIABLES

IMAGE_FILE_TYPES = ["dng", "png", "tif", "tiff"]

#%% IMAGE STORAGE

def list_images(path):
    """List images in the selected directory"""

    return [
        os.path.join(path, fname)
        for fname in os.listdir(path)
        if fname.split(".")[-1].lower() in IMAGE_FILE_TYPES
    ]

#%% IMAGE ANALYSIS

def MSE(image_1, image_2):    
    """Mean-Square Error (MSE) to compare two images"""

    image_1, image_2 = np.asarray(image_1), np.asarray(image_2)
    image_1 = image_1.astype(np.float32)
    image_2 = image_2.astype(np.float32)
    mse = np.mean( ( image_1 - image_2 )**2 )

    return mse

def PSNR(image_1, image_2, byte_depth=8):    
   """Peak Signal-to-Noise Ratio (PSNR) to compare two images.
   
   Parameters
   ----------
   image_1, image_2 : np.array
       The two pictures to compare. Must have the same shape.
    byte_depth : int, optional
        Image byte depth. Default is 8 for 8-bit images.
      
   Returns
   -------
   psnr : float
   """
    
   mse = MSE(image_1, image_2)
    
   if(mse == 0):  return np.inf
   # If MSE is null, then the two pictures are equal

   maximum_pixel = 2**byte_depth - 1

   psnr = 20 * log10(maximum_pixel / sqrt(mse)) # dB
    
   return psnr

def SSIM(image_1, image_2, byte_depth=8, win_size=None):    
    """Structural Similarity Index Measure (SSIM) to compare two images.
    
    Parameters
    ----------
    image_1, image_2 : np.array
        The two images to compare. Must have the same shape.
    byte_depth : int, optional
        Image byte depth. Default is 8 for 8-bit images.
        
    Returns
    -------
    ssim : float
    
    See also
    --------
    skimage.metrics.structural_similarity
    """
     
    data_range = 2**byte_depth

    image_1, image_2 = np.asarray(image_1), np.asarray(image_2)
    
    return structural_similarity(image_1, image_2, 
                                 data_range=data_range, win_size=win_size)

def IOU(mask_1, mask_2):
    """Intersection Over Union (IOU) to compare two boolean masks.
    
    Parameters
    ----------
    mask_1, mask_2 : np.array, torch.Tensor
        The two image masks to compare. Must have the same shape.
        
    Returns
    -------
    iou : float
    """

    image_1, image_2 = np.asarray(image_1), np.asarray(image_2)
    intersection_count = int( np.sum(np.logical_and(mask_1, mask_2)) )
    union_count = int( np.sum(np.logical_or(mask_1, mask_2)) )
    
    return intersection_count / union_count

#%% PLOTTING TOOLS

def plot_image(image, title=None, dark=True, colormap="viridis",
               figsize=(2.66, 1.7), dpi=200, ax=None):

    if ax is None: fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    else: fig = ax.get_figure()

    ax.imshow(image, cmap=colormap)  # Convert BGR to RGB for Matplotlib
    if title is not None: 
        if dark: ax.set_title(title, fontsize="xx-small", color="w")
        else: ax.set_title(title, fontsize="xx-small")
    if dark: fig.patch.set_facecolor('k')

    # Remove axes and padding
    ax.axis("off")
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    return