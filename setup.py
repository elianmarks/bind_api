# -*- coding: utf-8 -*-
#Elliann Marks
#elian.markes@gmail.com
#

#Bibliotecas
from setuptools import setup

setup(
    name="Bind REST API Server",
    version="1.0",
    packages=["bindrest", "bindrest.cli"],
    include_package_data=True,
    install_requires=['argparse', 'flask', 'gunicorn', 'pyyaml'],
    entry_points={ "console_scripts": [ "bindrest = bindrest.bindrest:main", ]},
    package_data={'bindrest': ['doc/*.yml', 'templates/*', 'static/*']},
    data_files=[('/usr/bin', ['bin/bindrestd']), ('/var/lib/bindrest/', ['data/port'])],
    platforms="linux",
    zip_safe=False,
    author="Elliann Marks",
    author_email="elian.markes@gmail.com",
    description="Bind REST API server",
    license="BSD",
    keywords="bind, cli, rest",
    url="https://github.com/elliannmarks/bind_api",
)
