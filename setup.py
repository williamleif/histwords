from setuptools import setup

setup(name='histwords',
      version='0.1',
      description='Code for manipulating historical word vector embeddings.',
      url='https://github.com/williamleif/histwords',
      author='William Hamilton',
      author_email='wleif@stanford.edu',
      license='Apache Version 2',
      install_requires = ['numpy',
                          'cython',
                          'sklearn>=0.17',
                          'statsmodels']
      )
