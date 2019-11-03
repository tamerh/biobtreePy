import unittest
import os
import bbpy
import shutil
import os


class TestBiobtreePy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if os.path.isdir('bbtest'):
            shutil.rmtree('bbtest')
        os.mkdir('bbtest')

    @classmethod
    def tearDownClass(cls):
        if os.path.isdir('bbtest'):
            shutil.rmtree('bbtest')

    def test_Search_Mapping(self):

        if os.path.isdir(os.path.abspath('bbtest/out')):
            shutil.rmtree(os.path.abspath('bbtest/out'))
        bb = bbpy.bbpy(outDir='bbtest')
        bb.buildData(datasets='sample_data')
        self.assertTrue(os.path.isfile(
            os.path.abspath('bbtest/out/db/db.meta.json')))

        bb.start()

        res = bb.search('tpi1, vav_human, ENST00000297261')
        self.assertTrue(len(res) == 3)
        self.assertTrue(res['keyword'][0] == 'TPI1')
        self.assertTrue(res['keyword'][1] == 'VAV_HUMAN')
        self.assertTrue(res['identifier'][0] == 'ENSG00000111669')
        self.assertTrue(res['identifier'][1] == 'P15498')
        self.assertTrue(res['identifier'][2] == 'ENST00000297261')
        self.assertTrue(res['dataset'][0] == 'ensembl')
        self.assertTrue(res['dataset'][1] == 'uniprot')
        self.assertTrue(res['dataset'][2] == 'transcript')

        res = bb.mapping('AT5G3_HUMAN', 'map(go)', attrs='type')
        self.assertTrue(len(res) == 2)
        self.assertTrue(len(res['mapping_id']) == 10)
        self.assertTrue(len(res['type']) == 10)
        expected_ids = ['GO:0000276', 'GO:0005741', 'GO:0006754', 'GO:0008289',
                        'GO:0015986', 'GO:0016021', 'GO:0042407', 'GO:0042776',
                        'GO:0045263', 'GO:0046933']
        for id in expected_ids:
            self.assertTrue(id in res['mapping_id'])

        res = bb.mapping(
            'AT5G3_HUMAN', 'map(go).filter(go.type=="biological_process")', attrs='type')
        expected_ids = ['GO:0006754', 'GO:0015986', 'GO:0042407', 'GO:0042776']
        for id in expected_ids:
            self.assertTrue(id in res['mapping_id'])
        bb.stop()

    def test_ListGenomes(self):

        bb = bbpy.bbpy(outDir='bbtest')

        res = bb.listGenomes('ensembl')
        self.assertTrue('homo_sapiens' in res)
        self.assertTrue('mus_musculus' in res)
        self.assertTrue('xenopus_tropicalis' in res)
        self.assertTrue('xiphophorus_maculatus' in res)

        res = bb.listGenomes('ensembl_fungi')

        self.assertTrue('ashbya_gossypii' in res)
        self.assertTrue('saccharomyces_cerevisiae' in res)
        self.assertTrue('pyrenophora_teres' in res)
        self.assertTrue('ustilago_maydis' in res)

        res = bb.listGenomes('ensembl_plants')

        self.assertTrue('arabidopsis_thaliana' in res)
        self.assertTrue('oryza_sativa' in res)
        self.assertTrue('cynara_cardunculus' in res)
        self.assertTrue('zea_mays' in res)

        res = bb.listGenomes('ensembl_protists')

        self.assertTrue('phytophthora_parasitica' in res)
        self.assertTrue('entamoeba_histolytica' in res)
        self.assertTrue('pythium_ultimum' in res)
        self.assertTrue('trypanosoma_brucei' in res)

        res = bb.listGenomes('ensembl_bacteria')

        self.assertTrue('salmonella_enterica' in res)
        self.assertTrue('dissulfuribacter_thermophilus' in res)
        self.assertTrue('corynebacterium_pseudotuberculosis' in res)
        self.assertTrue('yersinia_rohdei' in res)

    def test_ListDatasets(self):
        bb = bbpy.bbpy(outDir='bbtest')

        self.assertTrue('uniprot' in bb.datasets.keys())
        self.assertTrue('hgnc' in bb.datasets.keys())
        self.assertTrue('entrez' in bb.datasets.keys())
        self.assertTrue('ensembl' in bb.datasets.keys())
        self.assertTrue('taxchild' in bb.datasets.keys())
        self.assertTrue('transcript' in bb.datasets.keys())
        self.assertTrue('exon' in bb.datasets.keys())

    def test_ListAttr(self):

        bb = bbpy.bbpy(outDir='bbtest')

        res = bb.listAttrs('hgnc')
        self.assertTrue(len(res) >= 6)
        self.assertTrue('locus_group' in res)

        res = bb.listAttrs('ensembl')
        self.assertTrue(len(res) >= 9)
        self.assertTrue('seq_region_name' in res)

        res = bb.listAttrs('transcript')
        self.assertTrue(len(res) >= 7)
        self.assertTrue('start' in res)

        res = bb.listAttrs('exon')
        self.assertTrue(len(res) >= 4)
        self.assertTrue('start' in res)


if __name__ == '__main__':
    unittest.main()
