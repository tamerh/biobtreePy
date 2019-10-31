from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='bbpy',
    version='0.99.0',
    description="The biobtreePy package provides an interface to [biobtree](https://github.com/tamerh/biobtree) tool which covers large set of bioinformatics datasets and allows search and chain mappings functionalities.",
    author="Tamer Gur",
    author_email='tgur@ebi.ac.uk',
    url='https://github.com/tamerh/biobtreePy',
    long_description="The biobtreePy package provides an interface to [biobtree](https://github.com/tamerh/biobtree) tool which covers large set of bioinformatics datasets and allows search and chain mappings functionalities.",
    packages=find_packages(),
    install_requires=["grpc"],
    license="MIT license",
    keywords=["bioinformatics", "identifiers", "mapping", "biobtree"],
    test_suite='tests',
    include_package_data=True

)
