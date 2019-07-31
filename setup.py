from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

from conf import PACKAGE_NAME, VERSION

curr_path = path.abspath(path.dirname(__file__))

with open(path.join(curr_path, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description='',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/qedsoftware/puppet-master',
    author='Quantitative Engineering Design Inc.',
    author_email='info@qed.ai',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='puppet selenium form filling driver',
    packages=find_packages(exclude=['tests']),
)
