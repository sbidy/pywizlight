import setuptools
import os
import re

with open("README.md", "r") as fh:
    long_description = fh.read()

def get_version() -> str:
    version_file = open(os.path.join('pywizlight', '_version.py'))
    version_contents = version_file.read()
    return re.search("__version__ = '(.*?)'", version_contents).group(1)

setuptools.setup(
     name='pywizlight',  
     version=get_version(),
     author="Stephan Traub",
     author_email="sbidy@hotmail.com",
     description="A python connector for WiZ light bulbs (e.g SLV Play)",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/sbidy/pywizlight",
     packages=setuptools.find_packages(exclude=["test.py"]),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )