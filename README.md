## biobtreePy
Python package for genomic research via [biobtree](https://github.com/tamerh/biobtree). It aims to provide a strong alternative to similar tools with abilty process large and diverse datasets effectievly and allows executing simple or complex queries between these datasets.

## Installation

```python
pip install bbpy
```

## Usage

```python
import bbpy
import os

# create the package class instance with new or existing folder which data built before.
bb=bbpy.bbpy('specify your directory')


# default database for most studied dataset and organism genomes 
# once it is retrieved it is saved to your directory for later reuse
# check document for included dataset or other builtin databases or build custom data
bb.getBuiltInDB()

# starts server for executing queries inside Python pipelines and provide web interface with examples
# web interface address http://localhost:8888/ui/
bb.start()


#Searching identfiers and keywords such as gene name or accessions by passing comma seperated terms.
bb.search('tpi1,vav_mouse,p15498')

#search only within dataset
bb.search("shh,tp53","hgnc")

#Mappings queries allow chains mapping among datasets and in following format
#map(dataset_id).filter(Boolean expression).map(...).filter(...) 

# map proteins to go terms
bb.mapping('at5g3_human,vav_human','map(go)',attrs = "type")

# map proteins to go terms types with filter
bb.mapping('at5g3_human,vav_human','map(go).filter(go.type=="biological_process")',attrs = "type")

# stop local server. server can be start again with existing data
bb.stop()

```
