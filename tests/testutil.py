import tarfile
import os


def sampleDatasetArgs(outDir, hgnc=False):

    if hgnc:
        args = " -d hgnc,go,uniprot,ensembl,interpro"
    else:
        args = "  -d go,uniprot,ensembl,interpro"

    args = args+" --uniprot.file "+"../sample_data/uniprot_sample.xml.gz"
    args = args+" --interpro.file "+"../sample_data/interpro_sample.xml.gz"

    if not os.path.isfile(outDir+"/ensembl_sample.json"):
        tar = tarfile.open("sample_data/ensembl_sample.json.tar.gz", "r:gz")
        tar.extractall(path=outDir)
        tar.close()
    args = args+" --ensembl.file "+"ensembl_sample.json"

    if not os.path.isfile(outDir+"/go_sample.owl"):
        tar = tarfile.open("sample_data/go_sample.tar.gz", "r:gz")
        tar.extractall(path=outDir)
        tar.close()
    args = args+" --go.file "+"go_sample.owl"

    args = args+" build"

    return args
