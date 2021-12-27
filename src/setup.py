import codecs
import os
import re
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(name='Allagash',
      version=find_version("allagash", "__init__.py"),
      description='A Python Spatial Optimization Library',
      long_description='A spatial optimization library for covering problems.',
      author='Aaron Pulver',
      author_email='apulverizer@gmail.com',
      url='https://github.com/apulverizer/allagash',
      packages=['allagash'],
      license='MIT',
      python_requires='>=3.6',
      install_requires=[
          'pandas>=0.23.0',
          'pulp>=1.6.1'
      ],
      extras_require={
          "arcgis": ["arcgis>=1.8.2"],
          "geopandas": ["geopandas>=0.4.1"]
      },
      classifiers=[
          'Intended Audience :: Science/Research',
          'Programming Language :: Python :: 3'
      ]
      )
