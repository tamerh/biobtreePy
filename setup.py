from setuptools import setup

setup(
    name='bbpy',
    version='1.0.0',
    description="The biobtreePy package provides an interface to [biobtree](https://github.com/tamerh/biobtree) tool which covers large set of bioinformatics datasets and allows search and chain mappings functionalities.",
    author="Tamer Gur",
    author_email='tgur@ebi.ac.uk',
    url='https://github.com/tamerh/biobtreePy',
    long_description="The biobtreePy package provides an interface to [biobtree](https://github.com/tamerh/biobtree) tool which covers large set of bioinformatics datasets and allows search and chain mappings functionalities.",
    packages=['bbpy', 'bbpy.pbuf'],
    install_requires=[
        "grpcio>=1.24.3",
        "protobuf>=3.5.0",
        "requests>=2.20"],
    license="MIT license",
    keywords=["bioinformatics", "identifiers", "mapping", "biobtree"],
    test_suite='tests',
    include_package_data=True
)
