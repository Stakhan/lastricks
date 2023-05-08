from importlib.metadata import distribution  

dist = distribution('lastricks')  

__version__ = dist.version