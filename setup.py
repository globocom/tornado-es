# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

VERSION = '1.5.0'

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
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'tornado>=3.0.0,<3.3.0',
    ],
    tests_require=[
        'unittest2',
        'nose'
    ],
    dependency_links=[],
)
