# conda create -n dev python==3.13.2; conda activate dev
conda install python \
    numpy matplotlib conda-forge::opencv scikit-image pillow scikit-learn \
    conda-forge::tifffile
pip install pyvtools
# Line1 > Anaconda environment with Python 3.13.2 to ensure compatibility
# Line2 > Required packages = Scientific tools + Image processing libraries
# Line3 > Current package's scientific custom tools