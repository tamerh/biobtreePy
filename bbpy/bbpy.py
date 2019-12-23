import bbpy.pbuf.app_pb2_grpc as biobtree_grpc
import bbpy.pbuf.app_pb2 as biobtree_proto

import grpc
import os
import string
import platform
import requests
import tarfile
import zipfile
import time
import copy
import json


class bbpy:

    def __init__(self, outDir=None, remoteAddr=None):

        self.startupTimeout = 50
        self.datasets = None
        self.datasetsByNum = None
        self.datasetsView = None
        self.channel = None
        self.stub = None
        self.configLoaded = False
        self.externalAddr = None
        self.localAddr = None
        self.remote = False
        self.genomeDatasets = ["ensembl", "ensembl_bacteria", "ensembl_fungi",
                               "ensembl_metazoa", "ensembl_plants", "ensembl_protists"]

        if remoteAddr is not None:
            self.externalAddr = remoteAddr
            self.channel = grpc.insecure_channel(self.externalAddr)
            self.stub = biobtree_grpc.BiobtreeServiceStub(self.channel)
            self.remote = True
            self.__setConfig__()
        else:
            if outDir is None:
                raise Exception("outDir parameter needed")
            if not os.path.isdir(os.path.abspath(outDir)):
                raise Exception("Specified outDir is not exist")

            self.bbDir = os.path.abspath(outDir)
            curDir = os.getcwd()
            try:
                os.chdir(self.bbDir)
                execFile = self.__bbExecFile__()
                os.system(execFile + " install")
            finally:
                os.chdir(curDir)
            self.__setConfig__()

    def __isRunning__(self):
        try:
            r = requests.head(self.localWebAddr)
        except:
            return False
        return True

    def __bbExecFile__(self):

        if self.remote:
            print("When remote bb is set, it is not needed to use this method")
            return

        osy = platform.system()
        if osy == "Windows":
            latestUrl = self.__latestbbPath__() + "/biobtree_Windows_64bit.zip"
        elif osy == "Darwin":
            latestUrl = self.__latestbbPath__() + "/biobtree_MacOS_64bit.tar.gz"
        elif osy == "Linux":
            latestUrl = self.__latestbbPath__()+"/biobtree_Linux_64bit.tar.gz"

        if osy == "Windows":

            if not os.path.isfile('biobtree.exe'):

                bbFile = requests.get(latestUrl, allow_redirects=True)
                with open('biobtree.zip', 'wb') as output:
                    output.write(bbFile.content)
                with zipfile.ZipFile('biobtree.zip', 'r') as zip_ref:
                    zip_ref.extractall(self.bbDir)
                os.remove('biobtree.zip')

            return os.path.abspath('biobtree.exe')

        elif osy == "Darwin" or osy == "Linux":

            if not os.path.isfile('biobtree'):

                bbFile = requests.get(latestUrl, allow_redirects=True)
                with open('biobtree.tar.gz', 'wb') as output:
                    output.write(bbFile.content)
                bbFile.close()
                tar = tarfile.open('biobtree.tar.gz', "r:gz")
                tar.extractall()
                tar.close()
                os.remove('biobtree.tar.gz')

            return os.path.abspath('biobtree')

        else:
            raise Exception("Unsupported OS")

    def __latestbbPath__(self):

        r = requests.get("https://github.com/tamerh/biobtree/releases/latest")
        if r.status_code != 200:
            raise Exception(
                "Error while connecting github for retrieving latest version")
        splittedurl = r.url.split("/")
        version = splittedurl[len(splittedurl)-1]
        return "https://github.com/tamerh/biobtree/releases/download/" + version

    def __setConfig__(self):

        self.datasets = dict()
        self.datasetsByNum = dict()
        self.datasetsView = list()

        numIDs = list()

        if self.remote:
            meta = self.stub.Meta(
                biobtree_proto.MetaRequest())

            metaClone = biobtree_proto.MetaResponse()
            metaClone.CopyFrom(meta)

            res = meta.results
            cloneres = metaClone.results

            for k in res:
                idstr = res[k].keyvalues["id"]
                self.datasetsByNum[int(k)] = res[k].keyvalues
                self.datasets[res[k].keyvalues["id"]] = cloneres[k].keyvalues
                self.datasets[res[k].keyvalues["id"]]["id"] = k
                numIDs.append(int(k))

            if len(self.datasets) == 0 or len(self.datasetsByNum) == 0:
                raise Exception(
                    "Error while 1retrieving meta information. Check configured previous step correctly")
        else:
            # read dataset conf files
            with open(os.path.abspath(self.bbDir+"/conf/source.dataset.json"), 'r') as sourcefile:
                content = sourcefile.read()
                self.datasets = json.loads(content)
            with open(os.path.abspath(self.bbDir+"/conf/default.dataset.json"), 'r') as sourcefile:
                content = sourcefile.read()
                self.datasets.update(json.loads(content))
            with open(os.path.abspath(self.bbDir+"/conf/optional.dataset.json"), 'r') as sourcefile:
                content = sourcefile.read()
                self.datasets.update(json.loads(content))

            for k, v in self.datasets.items():
                numID = int(v["id"])
                self.datasetsByNum[numID] = copy.deepcopy(v)
                self.datasetsByNum[numID]["id"] = k
                numIDs.append(numID)

            # read app conf files
            with open(os.path.abspath(self.bbDir+"/conf/application.param.json"), 'r') as sourcefile:
                content = sourcefile.read()
                appparams = json.loads(content)
                if 'grpcPort' not in appparams.keys():
                    raise Exception(
                        "grpcPort could not found check application.param.json file")
                if 'httpPort' not in appparams.keys():
                    raise Exception(
                        "httpPort could not found check application.param.json file")
                self.localAddr = 'localhost:'+appparams['grpcPort']
                self.localWebAddr = 'http://localhost:' + appparams['httpPort']

        for k in numIDs:  # TODO add chembl etc...
            dataset = self.datasetsByNum[k]["id"]
            if dataset in ['go', 'efo', 'eco']:
                self.datasetsByNum[k]["attrPath"] = "ontology"
            elif dataset in ['transcript', 'exon', 'ortholog', 'paralog']:
                self.datasetsByNum[k]["attrPath"] = 'ensembl'
            else:
                self.datasetsByNum[k]["attrPath"] = dataset

        numIDs.sort()
        self.datasetsView.append(["id", "numeric id", "type"])
        for k in numIDs:
            if k < 30:
                self.datasetsView.append(
                    [self.datasetsByNum[k]["id"], k, "source & target"])
            else:
                self.datasetsView.append(
                    [self.datasetsByNum[k]["id"], k, "target"])

        self.configLoaded = True

    def start(self):

        if self.remote:
            print("When remote bb is set, it is not needed to use this method")
            return
        else:

            curDir = os.getcwd()
            os.chdir(self.bbDir)

            try:

                execFile = self.__bbExecFile__()

                if(not self.__isRunning__()):

                    if not os.path.isfile(os.path.abspath(self.bbDir+"/out/db/db.meta.json")):
                        raise Exception(
                            "Could not started, make sure data built correctly with specified path")

                    print("biobtreePy is starting")
                    os.spawnl(os.P_NOWAIT, execFile, execFile, 'web')

                    elapsed = 1
                    while True:

                        if elapsed > self.startupTimeout:
                            self.stop()
                            raise Exception(
                                "Timeout while starting up biobtree. Check that you set everything correctly")

                        time.sleep(1)
                        if not self.__isRunning__():
                            elapsed = elapsed + 1
                            continue
                        self.channel = grpc.insecure_channel(self.localAddr)
                        self.stub = biobtree_grpc.BiobtreeServiceStub(
                            self.channel)
                        return("biobtreePy started")

                else:
                    return "biobtree started before. Stop first if you need restart"
            except Exception as e:
                self.stop()
                print(e)
            finally:
                os.chdir(curDir)

    def stop(self):
        osy = platform.system()
        if osy == "Windows":
            os.system('taskkill "/IM biobtree.exe /F')
        elif osy == "Darwin" or osy == "Linux":
            os.system('killall biobtree')
        else:
            raise Exception("Unsupported OS")

    """
    Get pre build biobtree database

    Pre build biobtree database for commonly studied datasets and model organism genomes. Once this function called it retrieves
    the pre build database saves to users output directory. To created custom database with data not included in builtin database use buildData function

    :type built in database type accepted values are 1,2,3 and 4. Currently there are 4 different builtin database;
    Type 1
    Included datasets hgnc,hmdb,taxonomy,go,efo,eco,chebi,interpro
    Included uniprot proteins and ensembl genomes belongs to following organisms

    homo_sapiens 9606 --> ensembl
    danio_rerio 7955 zebrafish --> ensembl
    gallus_gallus 9031 chicken --> ensembl
    mus_musculus 10090 --> ensembl
    Rattus norvegicus 10116 ---> ensembl
    saccharomyces_cerevisiae 4932--> ensembl,ensembl_fungi
    arabidopsis_thaliana 3702--> ensembl_plants
    drosophila_melanogaster 7227 --> ensembl,ensembl_metazoa
    caenorhabditis_elegans 6239 --> ensembl,ensembl_metazoa
    Escherichia coli 562 --> ensembl_bacteria
    Escherichia coli str. K-12 substr. MG1655 511145 --> ensembl_bacteria
    Escherichia coli K-12 83333 --> ensembl_bacteria

    Type 2
    Instead of genomes in in the type 1 it contains human and all the mouse strains genomes with their uniprot proteins.
    In addition hgnc,hmdb,taxonomy,go,efo,eco,chebi,interpro datasets are included

    Type 3
    Contains no genome but it contains all the uniprot data with hgnc,hmdb,taxonomy,go,efo,eco,chebi,interpro

    Type 4
    Contains no genome but full uniprot and chembl data with hgnc,hmdb,taxonomy,go,efo,eco,chebi,interpro
    """

    def getBuiltInDB(self, builtInType="1"):

        curDir = os.getcwd()

        os.chdir(self.bbDir)

        try:

            execFile = self.__bbExecFile__()

            os.system(execFile + " --pre-built "+builtInType + " install")

        finally:
            os.chdir(curDir)

    def buildData(self, taxonomyIDs=None, rawArgs=None):

        if self.remote:
            print("When remote bb is set, it is not needed to use this method")
            return

        if self.__isRunning__():
            raise Exception('There is a running biobtree stop first')

        curDir = os.getcwd()

        os.chdir(self.bbDir)

        try:

            execFile = self.__bbExecFile__()

            if rawArgs is not None:
                os.system(execFile + " " + rawArgs)
            elif taxonomyIDs is not None:
                args = " -tax "+taxonomyIDs+" --keep --ensembl-orthologs" + " build"
                os.system(execFile + args)

        finally:
            os.chdir(curDir)

    def __sampleDatasetArgs__(self, hgnc=False):

        if hgnc:
            args = " -d hgnc,go,uniprot,ensembl,interpro"
        else:
            args = "  -d go,uniprot,ensembl,interpro"

        args = args+" --uniprot.file "+"../sample_data/uniprot_sample.xml.gz"
        args = args+" --interpro.file "+"../sample_data/interpro_sample.xml.gz"

        if not os.path.isfile(os.path.abspath(self.bbDir+"/ensembl_sample.json")):
            tar = tarfile.open(
                os.path.abspath("../sample_data/ensembl_sample.json.tar.gz"), "r:gz")
            tar.extractall(path=self.bbDir)
            tar.close()
        args = args+" --ensembl.file "+"ensembl_sample.json"

        if not os.path.isfile(os.path.abspath(self.bbDir+"/go_sample.owl")):
            tar = tarfile.open(os.path.abspath(
                "../sample_data/go_sample.tar.gz"), "r:gz")
            tar.extractall(path=self.bbDir)
            tar.close()
        args = args+" --go.file "+"go_sample.owl"

        args = args+" build"

        return args

    def search(self, terms, source=None, filter=None, page=None, limit=1000, showURL=False, lite=True):

        if len(terms) < 2:
            raise Exception("Input terms should be at least 2 charhacters")

        termarr = terms.split(",")
        for i in range(len(termarr)):
            termarr[i] = termarr[i].strip()
            if len(termarr[i]) < 2:
                raise Exception(
                    "Each input term should be at least 2 charhacters")

        req = biobtree_proto.SearchRequest(terms=termarr)
        req.url = True
        if source is not None:
            req.dataset = source
        if filter is not None:
            req.query = filter
        if page is not None:
            req.page = page
        if showURL:
            req.url = True
        if not lite:
            req.detail = True

        res = self.stub.Search(req)

        results = res.results.results

        if len(res.results.nextpage) > 0 and len(results) < limit:
            lastpagekey = res.results.nextpage
            while len(results) < limit:
                req.page = lastpagekey
                newres = self.stub.Search(req)

                results.extend(newres.results.results)
                if len(res.results.nextpage) > 0:
                    lastpagekey = lastpagekey = newres.results.nextpage
                else:
                    break

        if lite:
            input = list()
            id = list()
            source = list()
            if showURL:
                urls = list()

            for r in results:
                if hasattr(r, 'keyword'):
                    input.append(r.keyword)
                else:
                    input.append(r.identifier)
                id.append(r.identifier)
                source.append(self.datasetsByNum[r.dataset]["id"])
                if showURL:
                    urls.append(r.url)

            if showURL:
                return {
                    "keyword": input,
                    "identifier": id,
                    "dataset": source,
                    "url": urls
                }
            else:
                return {
                    "keyword": input,
                    "identifier": id,
                    "dataset": source
                }

        return res

    def mapping(self, terms, mappingq, source=None, page=None, lite=True, limit=1000, inattrs=None, attrs=None, showInputColumn=False):

        if len(terms) < 2:
            raise Exception("Input terms should be at least 2 charhacters")

        if len(mappingq) == 0:
            raise Exception("Mapping query is required")

        termarr = terms.split(",")
        for i in range(len(termarr)):
            termarr[i] = termarr[i].strip()
            if len(termarr[i]) < 2:
                raise Exception(
                    "Each input term should be at least 2 charhacters")

        req = biobtree_proto.MappingRequest(terms=termarr, query=mappingq)
        if source is not None:
            req.dataset = source
        if page is not None:
            req.page = page

        res = self.stub.Mapping(req)
        results = res.results.results
        totalMapping = 0
        for r in results:
            totalMapping = totalMapping+len(r.targets)

        if len(res.results.nextpage) > 0 and totalMapping < limit:
            lastpagekey = res.results.nextpage
            while totalMapping < limit:

                req.page = lastpagekey
                newres = self.stub.Mapping(req)
                for rnew in newres.results.results:
                    for i in range(len(results)):
                        r = results[i]
                        if rnew.source.dataset == r.source.dataset and rnew.source.identifier == r.source.identifier:
                            totalMapping = totalMapping+len(rnew.targets)
                            results[i].targets.extend(rnew.targets)
                            break
                if len(newres.results.nextpage) > 0:
                    lastpagekey = lastpagekey = newres.results.nextpage
                else:
                    break

        if lite:
            multiInput = False
            if len(results) > 1 or showInputColumn:
                multiInput = True

            if attrs is not None:
                attrsarr = attrs.split(",")
                attrsVals = []
                for i in range(len(attrsarr)):
                    attrsVals.append([])

            if inattrs is not None:
                multiInput = True
                inattrsarr = inattrs.split(",")
                inattrsVals = []
                for i in range(len(inattrsarr)):
                    inattrsVals.append([])

            mappingID = []
            if multiInput:
                inID = []
                inSource = []
            for r in results:
                j = 0
                for rtarget in r.targets:

                    mappingID.append(rtarget.identifier)

                    if j == 0:
                        if multiInput:

                            if len(r.source.keyword) > 0:
                                inID.append(r.source.keyword+"-" +
                                            r.source.identifier)
                            else:
                                inID.append(r.source.identifier)

                            inSource.append(
                                self.datasetsByNum[r.source.dataset]["id"])
                    else:
                        inID.append("-")
                        inSource.append("-")

                    if attrs is not None:
                        for i, attr in enumerate(attrsarr):
                            try:
                                allVals = getattr(
                                    rtarget, self.datasetsByNum[rtarget.dataset]["attrPath"])
                                attrsVals[i].append(getattr(allVals, attr))
                            except:
                                attrsVals[i].append("")

                    if inattrs is not None:
                        for i, attr in enumerate(inattrsarr):
                            try:
                                allVals = getattr(
                                    r, self.datasetsByNum[r.source.dataset]["attrPath"])
                                inattrsVals[i].append(getattr(allVals, attr))
                            except:
                                inattrsVals[i].append("")
            res = {}
            if multiInput:
                res["in_identifier"] = inID
                res["in_source"] = inSource
            if inattrs is not None:
                for i, attr in enumerate(inattrsarr):
                    res["in_"+attr] = inattrsVals[i]

            res["mapping_id"] = mappingID

            if attrs is not None:
                for i, attr in enumerate(attrsarr):
                    res[attr] = attrsVals[i]

            return res

        return results

    def listGenomes(self, dataset):

        if self.remote:
            res = self.stub.ListGenomes(
                biobtree_proto.ListGenomesRequest(type=type))
            resjs = json.loads(res.results)
            return resjs["jsons"].keys()
        else:
            if not dataset in self.genomeDatasets:
                raise Exception(
                    "Invalid dataset for genome listing valid datasets")
            with open(os.path.abspath(self.bbDir+"/ensembl/"+dataset+".paths.json"), 'r') as sourcefile:
                content = sourcefile.read()
                genomes = json.loads(content)
                return genomes["jsons"].keys()

    def listAttrs(self, dataset):

        if dataset in self.datasets:
            if "attrs" in self.datasets[dataset]:
                return self.datasets[dataset]["attrs"].split(",")
            else:
                return []
        else:
            raise Exception("Invalid dataset")

    def entry(self, identifier, dataset):
        response = self.stub.Entry(
            biobtree_proto.EntryRequest(identifier=identifier, dataset=dataset))
        return response

    def entryPage(self, identifier, dataset, page, total):
        response = self.stub.Page(
            biobtree_proto.PageRequest(identifier=identifier, dataset=dataset, page=page, total=total))
        return response

    def entryFilter(self, identifier, dataset, filters, page):
        response = stub.Filter(
            biobtree_proto.FilterRequest(identifier=identifier, dataset=dataset, filters=filters, page=page))
        return response
