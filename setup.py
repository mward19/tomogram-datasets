from setuptools import setup, find_packages

setup(
    name='tomograms',
    version='0.1',
    packages=find_packages(),
    package_dir={'tomograms': 'tomograms'},
    install_requires=[
        'numpy',
        'scikit-image',
        'mrcfile',
        'imodmodel',
        'pandas'
    ],
    author='Matthew Ward',
    author_email='matthew.merrill.ward@gmail.com',
    description='A package for handling tomograms and related tasks',
    url='https://github.com/mward19/tomogram-datasets/blob/master/',
)