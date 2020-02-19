import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='pywizlight',  
     version='0.1',
     scripts=['pywizlight.py'] ,
     author="Stephan Traub",
     author_email="sbidy@hotmail.com",
     description="A python connector for WiZ light bulbs (e.g SLV Play)",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/sbidy/pywizlight",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )