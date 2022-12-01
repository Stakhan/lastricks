## Building
Install tools:
```
conda install conda-build conda-verify
```
Inside this directory:
```
conda build . -c conda-forge
```

## Quicker build with mamba
```
conda install mamba
```
Inside this directory:
```
conda mambabuild . -c conda-forge
```

## Test Anaconda badge
https://anaconda.org/eal/lastricks/badges/version.svg