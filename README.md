# PyVTools

General custom tools to work in scientific research using Python

## Getting Started

### Installation

This package can easily be installed using `pip`:

```bash
pip install pyvtools
```

An alternative installation that partially uses Anaconda would involve...

1. First, install some Anaconda distribution, in case you do not have any:
   https://docs.anaconda.com/anaconda/install/
2. Then, create an Anaconda environment with Python 3.11.0
   ```bash
   conda create -n dev python=3.11.0
   ```
3. Activate the environment
   ```bash
   conda activate dev
   ```
3. Then, install all required packages by running the `install.sh` script:
   ```bash
   yes | . install.sh
   ```
   This will have executed...
   ```bash
   conda install python=3.11.0 numpy<=1.26.4 \
       matplotlib conda-forge::opencv scikit-image pillow scikit-learn conda-forge::tifffile
   pip install pyvtools
   ```
5. That's it! You're good to go :)

That second installation procedure is designed to be overly redundant, so please feel free to follow your own installation procedure.

### Requirements

Provided installation steps are only guaranteed to work in Ubuntu 24.04.

In case you are following another installation procedure, this repository requires...

- Python 3.11.0
- Numpy <= 1.26.4

## Additional information

### Main Author Contact

Valeria Pais - @vrpais - valeriarpais@gmail.com