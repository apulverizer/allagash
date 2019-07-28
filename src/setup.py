from distutils.core import setup

setup(name='Allagash',
    version='0.0.1',
    description='A Python Spatial Optimization Library',
    author='Aaron Pulver',
    author_email='apulverizer@gmail.com',
    url='https://github.com/apulverizer/allagash',
    packages=['allagash', 'allagash.coverage',
              'allagash/data'],
    license='MIT',
    install_requires=[
        'pulp>=1.6.1',
        'pyshp==1.2.11'
    ],
    classifiers=[
      'Intended Audience :: Developers/Researchers',
      'Programming Language :: Python :: 3.6'
    ]
 )
