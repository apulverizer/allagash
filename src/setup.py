from distutils.core import setup

setup(name='Allagash',
      version='0.0.1',
      description='A Python Spatial Optimization Library',
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
          'Intended Audience :: Developers/Researchers',
          'Programming Language :: Python :: 3'
      ]
      )
