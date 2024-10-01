# conda create -n dev python=3.11.0; conda activate dev
conda install python=3.11.0 numpy<=1.26.4 \
    matplotlib conda-forge::opencv scikit-image pillow scikit-learn conda-forge::tifffile
pip install pyvtools
# Line1 > Anaconda environment with Python 3.11.0 to ensure compatibility
# Line2 > Required packages = Scientific tools + Image processing libraries
# Line3 > Current package's scientific custom tools