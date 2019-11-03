## biobtreePy
This package provides a Python interface to [biobtree](https://github.com/tamerh/biobtree) tool which provides search and chain mappings functionalities for identifiers, accessions and special keywords for genomic research pipelines.

## Installation

```python
pip install bbpy
```

## Quick introduction

```python
import bbpy
import os

# first create or used existing folder for the tool files
os.mkdir('outFolder')

# create the package class instance with new or existing folder which data built before.
bb=bbpy.bbpy('outFolder')

# build data locally. Takes some minutes
bb.buildData(datasets='hgnc,uniprot,go')

#start local server which allows performing queries and provide web interface
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

# stop local server. server can be start again with existing built data
bb.stop()

```

## Build data
Building data process selected datasets and retrieve indivudual records belonging to these datasets with their attributes and mapping data.x


```python
# List datasets and genomes
bb.datasetsView
bb.listGenomes("ensembl")
bb.listGenomes("ensembl_bacteria")
bb.listGenomes("ensembl_fungi")
bb.listGenomes("ensembl_metazoa")
bb.listGenomes("ensembl_plants")
bb.listGenomes("ensembl_protists")
```


```python
# Build data examples 

#specific datasets
bb.buildData(datasets = "hgnc,go,taxonomy")

# build default datasets ensembl(homo_sapiens) uniprot(reviewed) hgnc taxonomy go eco efo interpro chebi
bb.buildData() 

#only specific datasets with specific mappings to speed up the build process
bb.buildData(datasets = "hgnc,uniprot,go,taxonomy",targetDatasets = "hgnc,uniprot,taxonomy,ufeature,go,pdb,taxchild,taxparent") 

# build both mouse and human genomes in ensembl insted of default human
bb.buildData(genome="homo_sapiens,mus_musculus")

# build genomes from ensembl genomes fungi + means in addition to default dataset
bb.buildData(datasets="+ensembl_fungi",genome="saccharomyces_cerevisiae")

# multiple species genomes from ensembl genomes plants and protists
bb.buildData(datasets="+ensembl_plants,ensembl_protists",genome="arabidopsis_thaliana,phytophthora_parasitica")

# multiple bacteria genomes with pattern which means any genomes contains given names seperated by comma
bb.buildData(datasets="+ensembl_bacteria",genomePattern="serovar_infantis,serovar_virchow")
```

## Example use cases


```python
# build data with default dataset and start server
bb=bbpy.bbpy('outFolder')
bb.buildData()
bb.stop()
bb.start()
```

## Gene centric use cases
Ensembl, Ensembl Genomes and HGNC datasets are used for gene related data. One of the most common gene related dataset identfiers are `ensembl`,`hgnc`,`transcript`,`exon`. Note that there are several other gene related datasets without attributes and can be used in mapping queries such as probesets, genebank and entrez etc.


```python
# list gene related dataset attiributes
bb.listAttrs('ensembl')
bb.listAttrs('hgnc')
bb.listAttrs('transcript')
bb.listAttrs('exon')
```


```python
# Map gene names to Ensembl transcript identifier
bb.mapping('ATP5MC3,TP53','map(transcript)')

# Map gene names to exon identifiers and retrieve the region
bb.mapping('ATP5MC3,TP53','map(transcript).map(exon)',attrs = "seq_region_name")

# Map gene to its ortholog identifiers
bb.mapping('shh','map(ortholog)')

# Map gene to its paralog
bb.mapping('fry','map(paralog)')

# Map ensembl identifier or gene name to the entrez identifier
bb.mapping('ENSG00000073910,shh' ,'map(entrez)')

# Map refseq identifiers to hgnc identifiers
bb.mapping('NM_005359,NM_000546','map(hgnc)',attrs = 'symbols')

# Get all Ensembl human identifiers and gene names on chromosome Y with lncRNA type
bb.mapping('homo_sapiens','map(ensembl).filter(ensembl.seq_region_name=="Y" && ensembl.biotype=="lncRNA")',attrs = 'name')

 
# Get all Ensembl human identifiers and gene names within or overlapping range [114129278-114129328]
# In this example as a first parameter taxonomy identifier is used instead of specifying as homo sapiens like in the previous example. 
# Both of these usage are equivalent and produce same output as homo sapiens refer to taxonomy identifer 9606.
bb.mapping('9606','map(ensembl).filter((114129278>ensembl.start && 114129278<ensembl.end) || (114129328>ensembl.start && 114129328<ensembl.end))',attrs = 'name')

# Map Affymetrix identifiers to Ensembl identifiers and gene names
res=bb.mapping("202763_at,213596_at,209310_s_at",source ="affy_hg_u133_plus_2" ,'map(transcript).map(ensembl)',attrs = "name")

# all mappings can be done with opposite way, for instance from gene name to Affymetrix identifiers mapping is performed following way
res=bb.mapping("CASP3,CASP4",'map(transcript).map(affy_hg_u133_plus_2)')

# Retrieve all the human gene names which contains TTY
res=bb.mapping("homo sapiens",'map(ensembl).filter(ensembl.name.contains("TTY"))',attrs = "name")
```

## Protein centric use cases


```python
# list some protein related dataset attiributes
bb.listAttrs('uniprot')
bb.listAttrs('ufeature')
bb.listAttrs('pdb')
bb.listAttrs('interpro')
```


```python
# Map gene names to reviewed uniprot identifiers

#search & filter by name
bb.mapping('rag1_human,clock_human,bmal1_human,shh_human,aicda_human,at5g3_human,p53_human','filter(uniprot.names.exists(a,a=="Sonic hedgehog protein"))')

#search & filter by sequence mass
bb.mapping('rag1_human,clock_human,bmal1_human,shh_human,aicda_human,at5g3_human,p53_human','filter(uniprot.sequence.mass > 45000)')

#search & filter by sequence size
bb.mapping('rag1_human,clock_human,bmal1_human,shh_human,aicda_human,at5g3_human,p53_human','filter(size(uniprot.sequence.seq) > 400)')

#go term molecular
bb.mapping('shh_human,p53_human','map(go).filter(go.type=="molecular_function")')

#go term cellular
bb.mapping('shh_human,p53_human','map(go).filter(go.type=="cellular_component")')

#go term boolean
bb.mapping('shh_human,p53_human','map(go).filter(go.name.contains("binding") || go.name.contains("activity"))')

#filter first then go terms contains word
bb.mapping('shh_human,p53_human,rag1_human,clock_human,bmal1_human,aicda_human,at5g3_human','filter(size(uniprot.sequence.seq) > 400).map(go).filter(go.name.contains("binding") || go.name.contains("activity"))')

#interpro Conserved site
bb.mapping('shh_human,p53_human,rag1_human,clock_human,bmal1_human,aicda_human,at5g3_human','map(interpro).filter(interpro.type=="Conserved_site")')

#ENA type mRNA
bb.mapping('shh_human,p53_human','map(ena).filter(ena.type=="mrna")')

#ENA type genomic DNA
bb.mapping('shh_human,p53_human','map(ena).filter(ena.type=="genomic_dna")')

#to refseqs
bb.mapping('rag1_human,clock_human,bmal1_human,shh_human,aicda_human,at5g3_human,p53_human','map(refseq)')

#cancer related gene variants
bb.mapping('pms2,mlh1,msh2,msh6,stk11,bmpr1a,smad4,brca1,brca2,tp53,pten,palb2,tsc1,tsc2,flcn,met,cdkn2a,rb1','map(uniprot).filter(uniprot.reviewed).map(ufeature).map(variantid)')

#feature helix type
bb.mapping('shh_human,p53_human','map(ufeature).filter(ufeature.type=="helix")')

#feature sequence variant
bb.mapping('shh_human,p53_human','map(ufeature).filter(ufeature.type=="sequence variant")')

#genes to mutation feature or contains
bb.mapping('her2,ras,p53','map(uniprot).map(ufeature).filter(ufeature.type=="mutagenesis site" || ufeature.description.contains("cancer"))')

#feature location
bb.mapping('shh_human,p53_human','map(ufeature).filter(ufeature.location.begin>0 && ufeature.location.end<300)')

#feature description contains
bb.mapping('shh_human,p53_human','map(ufeature).filter(ufeature.description.contains("tumor"))')

#feature specific variant
bb.mapping('shh_human,p53_human','map(ufeature).filter(ufeature.original=="I" && ufeature.variation=="S")')

#feature maps variantid
bb.mapping('shh_human,p53_human','map(ufeature).filter(ufeature.original=="I" && ufeature.variation=="S").map(variantid)')

#feature has evidences
bb.mapping('shh_human,p53_human','map(ufeature).filter(size(ufeature.evidences)>1)')

#feature has experimental evidence
bb.mapping('shh_human,p53_human','map(ufeature).filter(ufeature.evidences.exists(a,a.type=="ECO:0000269"))')

#feature has pubmed evidence
bb.mapping('shh_human,p53_human','map(ufeature).filter(ufeature.evidences.exists(a,a.source=="pubmed"))')

#feature pdb evidence
bb.mapping('shh_human,p53_human','map(ufeature).filter(ufeature.evidences.exists(a,a.source=="pdb"))')

#pdb method NMR
bb.mapping('shh_human,p53_human','map(pdb).filter(pdb.method=="nmr")')

#pdb chains
bb.mapping('shh_human,p53_human','map(pdb).filter(pdb.chains=="A/C=95-292")')

#pdb resolution
bb.mapping('shh_human,p53_human','map(pdb).filter(pdb.resolution=="2.60 A")')

#pdb method or chains
bb.mapping('shh_human,p53_human','map(pdb).filter(pdb.method=="nmr" || pdb.chains=="C/D=1-177")')

#reactome activation pathways
bb.mapping('shh_human,p53_human','map(reactome).filter(reactome.pathway.contains("activation"))')

#reactome signaling pathways
bb.mapping('shh_human,p53_human','map(reactome).filter(reactome.pathway.contains("signaling"))')

#reactome regulation pathways
bb.mapping('shh_human,p53_human','map(reactome).filter(reactome.pathway.contains("Regulation"))')

#orphanet disease name
bb.mapping('shh_human,p53_human','map(orphanet).filter(orphanet.disease.contains("cancer"))')

#durgs by drugbank
bb.mapping('shh_human,p53_human','map(drugbank)')

```

## Ontology & Taxonomy use cases


```python
#taxonomy children
bb.mapping('9606','map(taxchild)')

# taxonomy grand children
bb.mapping('862507','map(taxchild).map(taxchild)')

#taxonomy grand^2 parent
bb.mapping('10090','map(taxparent).map(taxparent).map(taxparent)')

#taxonomy Asian children
bb.mapping('10090','map(taxchild).filter(taxonomy.common_name.contains("Asian"))')

#taxonomy European children
bb.mapping('10090','map(taxchild).filter(taxonomy.common_name.contains("European"))')

#go term parent
bb.mapping('go:0004707','map(goparent)')

#go term parent type
bb.mapping('go:0004707','map(goparent).filter(go.type=="biological_process")')

#efo disaease name
bb.search('inflammatory bowel disease')

#efo children
bb.mapping('efo:0003767','map(efochild)')

#efo parent
bb.mapping('efo:0000384','map(efoparent)')

#eco children
bb.mapping('eco:0000269','map(ecochild)')

#eco parent
bb.mapping('eco:0007742','map(ecoparent)')

```

## ChEMBL centric use cases
ChEMBL is used as a source for chemical related datasets.


```python
# Chembl is not in the default dataset so first built the data
bb=bbpy.bbpy('bbChem')
bb.buildData(datasets="chembl,uniprot,hgnc,taxonomy,go,efo,eco")
bb.start()
```


```python
#Listing chembl related dataset attiributes
bb.listAttrs('chembl_document')
bb.listAttrs('chembl_assay')
bb.listAttrs('chembl_activity')
bb.listAttrs('chembl_molecule')
bb.listAttrs('chembl_target')
bb.listAttrs('chembl_target_component')
bb.listAttrs('chembl_cell_line')
```


```python
# search document, molecules by names,smile and inchi key
bb.search('GSK2606414,Cn1cc(c2ccc3N(CCc3c2)C(=O)Cc4cccc(c4)C(F)(F)F)c5c(N)ncnc15,SIXVRXARNAVBTC-UHFFFAOYSA-N,CHEMBL3421631')

#target single protein to uniprot
bb.mapping('chembl2789','filter(chembl.target.type=="single_protein").map(chembl_target_component).map(uniprot)')

#cancer related genes to targets
bb.mapping('pms2,mlh1,msh2,msh6,stk11,bmpr1a,smad4,brca1,brca2,tp53,pten,palb2,tsc1,tsc2,flcn,met,cdkn2a,rb1','map(uniprot).map(chembl_target_component).map(chembl_target)')

#cancer related genes to target with type
bb.mapping('pms2,mlh1,msh2,msh6,stk11,bmpr1a,smad4,brca1,brca2,tp53,pten,palb2,tsc1,tsc2,flcn,met,cdkn2a,rb1','map(uniprot).map(chembl_target_component).map(chembl_target).filter(chembl.target.type=="protein-protein_interaction")',source='hgnc')

#molecule activities filter bao
bb.mapping('gsk2606414','map(chembl_activity).filter(chembl.activity.bao=="BAO_0000190")')

#molecule activities AND
bb.mapping('gsk2606414','map(chembl_activity).filter(chembl.activity.value > 10.0 && chembl.activity.bao=="BAO_0000190")')

#molecule activities OR
bb.mapping('gsk2606414','map(chembl_activity).filter(chembl.activity.value>10.0 || chembl.activity.pChembl>5.0)')

#molecule targets
bb.mapping('gsk2606414','map(chembl_activity).map(chembl_document).map(chembl_assay).map(chembl_target)')

#document activities
bb.mapping('chembl1121978','map(chembl_activity)')

#document assay
bb.mapping('chembl3421631','map(chembl_assay)')

#document assay filter
bb.mapping('chembl3421631','map(chembl_assay).filter(chembl.assay.type=="Functional" || chembl.assay.type=="Binding")')

#document cell line
bb.mapping('chembl3421631','map(chembl_assay).map(chembl_cell_line)')

#document cell line Filter
bb.mapping('chembl3421631','map(chembl_assay).map(chembl_cell_line).filter(chembl.cellLine.tax=="9615" || chembl.cellLine.efo=="EFO_0002841")')

#document target
bb.mapping('chembl3421631','map(chembl_assay).map(chembl_target)')

#document target protein type
bb.mapping('chembl3421631','map(chembl_assay).map(chembl_target).filter(chembl.target.type=="single_protein")')

#document target tissue
bb.mapping('chembl3421631','map(chembl_assay).map(chembl_target).filter(chembl.target.type=="tissue")')

#document target organism
bb.mapping('chembl3421631','map(chembl_assay).map(chembl_target).filter(chembl.target.type=="organism")')

#document target protein uniprot
bb.mapping('chembl3421631','map(chembl_assay).map(chembl_target).map(chembl_target_component).map(uniprot)')

#document molecule
bb.mapping('chembl3421631','map(chembl_molecule)')

#document molecule filter
bb.mapping('chembl3421631','map(chembl_molecule).filter(chembl.molecule.heavyAtoms < 30.0 && chembl.molecule.aromaticRings <2.0)')

#assay target
bb.mapping('chembl615156','map(chembl_target)')

#assay cell line
bb.mapping('chembl3424821','map(chembl_cell_line)')

#assay target protein
bb.mapping('chembl615156','map(chembl_target).filter(chembl.target.type=="single_protein")')

#assay target protein uniprot
bb.mapping('chembl615156','map(chembl_target).map(chembl_target_component).map(uniprot)')

#search activity
bb.search('chembl_act_93229')

#activity molecule with filter
bb.mapping('chembl_act_93229','filter(chembl.activity.bao=="BAO_0000179").map(chembl_molecule)')

```