from setuptools import setup

setup(
    name='bbpy',
    version='1.0.6',
    description="This package provides a Python interface to biobtree",
    author="Tamer Gur",
    author_email='tgur@ebi.ac.uk',
    url='https://github.com/tamerh/biobtreePy',
    long_description="This package provides a Python interface to biobtree",
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
