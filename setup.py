from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='mobi_results_extraction',
      version='0.1',
      description='Utility to extract mobi model results to AWS',
      long_description=readme(),
      url='',
      author='NatureServe',
      license='MIT',
      packages=['mobi_results_extraction'],
      install_requires=[
          'botocore',
          'boto3',
          'pandas',
          'xlrd'
      ],
      zip_safe=False)
