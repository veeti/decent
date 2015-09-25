from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    readme = f.read()

setup(
    name='decent',
    version='0.1.0.dev1',

    license='MIT',
    description="Simple data validation library",
    long_description=readme,
    url='https://github.com/veeti/decent',
    author="Veeti Paananen",
    author_email='veeti.paananen@rojekti.fi',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    packages=['decent'],
    install_requires=[
        'six',
    ],
    extras_require={
        'test': [
            'pytest',
            'pytest-cov',
        ],
    },
)
