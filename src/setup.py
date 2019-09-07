from setuptools import setup

setup(name='Allagash',
      version='0.0.6',
      description='A Python Spatial Optimization Library',
      long_description='A spatial optimization library for covering problems.',
      author='Aaron Pulver',
      author_email='apulverizer@gmail.com',
      url='https://github.com/apulverizer/allagash',
      packages=['allagash'],
      license='MIT',
      install_requires=[
          'pulp~=1.6.1',
          'geopandas~=0.4.1'
      ],
      classifiers=[
          'Intended Audience :: Science/Research',
          'Programming Language :: Python :: 3'
      ]
      )
