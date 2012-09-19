# -*- coding: utf-8 -*-  

from setuptools import setup, find_packages

VERSION = '1.1.0'

setup(
      name='tornadoes',
      version=VERSION,
      description="Conexão assíncrona com o elasticsearch.",
      long_description="""\
Conexão assíncrona com o elasticsearch. Para ser utilizado com o Tornado Server.""",
      author='Time de busca da globo.com',
      author_email='busca@corp.globo.com',
      url = 'http://github.com/globocom/tornado-es',
      download_url = 'http://github.com/globocom/tornado-es',
      license='Proprietary',
      packages=find_packages(exclude=['ez_setup', 'testes']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'tornado',
      ],
      tests_require=[
            'unittest2',
        ],
      dependency_links=[],
)
