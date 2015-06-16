# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

VERSION = '2.4.0'

setup(
    name='tornadoes',
    version=VERSION,
    description="A tornado-powered python library that provides asynchronous access to elasticsearch.",
    long_description="""\
    A tornado-powered python library that provides asynchronous access to elasticsearch.""",
    author='Team Search of globo.com',
    author_email='busca@corp.globo.com',
    url='http://github.com/globocom/tornado-es',
    download_url='http://github.com/globocom/tornado-es',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'testes']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Operating System :: OS Independent',
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'tornado>=3.0.0,<4.2.0',
        'six>=1.7.3',
    ],
    tests_require=[
        'unittest2',
        'nose'
    ],
    dependency_links=[],
)
