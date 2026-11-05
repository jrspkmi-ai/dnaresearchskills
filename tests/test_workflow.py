import importlib.util, json, pathlib, tempfile, unittest
from unittest.mock import patch

ROOT=pathlib.Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'.agents/skills/dna-research/scripts/dna_tool.py'
spec=importlib.util.spec_from_file_location('dna_tool', SCRIPT)
dna=importlib.util.module_from_spec(spec); spec.loader.exec_module(dna)
EX=ROOT/'examples/synthetic-case'

class WorkflowTests(unittest.TestCase):
    def test_valid_synthetic_corpus_and_statements(self):
        self.assertEqual(dna.validate_corpus(EX/'corpus.csv'), [])
        self.assertEqual(dna.validate_statements(EX/'statements.csv',EX/'corpus.csv',EX/'codebook.json'), [])
    def test_invalid_review_and_unknown_source_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            f=pathlib.Path(d)/'s.csv'; s=(EX/'statements.csv').read_text().replace('ST02,D02','ST02,missing').replace('HUMAN_VALIDATED,Researcher 1','HUMAN_VALIDATED,')
            f.write_text(s); errors=dna.validate_statements(f,EX/'corpus.csv',EX/'codebook.json')
            self.assertTrue(any('unknown document_id' in x for x in errors)); self.assertTrue(any('requires reviewer' in x for x in errors))
    def test_rejects_invalid_qualifier_and_duplicate_id(self):
        with tempfile.TemporaryDirectory() as d:
            f=pathlib.Path(d)/'s.csv'; f.write_text((EX/'statements.csv').read_text().replace('ST02,','ST01,').replace(',opposes,',',invented,'))
            errors=dna.validate_statements(f,EX/'corpus.csv',EX/'codebook.json')
            self.assertTrue(any('duplicate statement_id' in x for x in errors)); self.assertTrue(any('qualifier' in x for x in errors))
    def test_actor_mapping_is_non_destructive(self):
        with tempfile.TemporaryDirectory() as d:
            d=pathlib.Path(d); mapping=d/'map.json'; mapping.write_text(json.dumps({'Actor A':'Person A'})); out=d/'out.csv'
            original=(EX/'statements.csv').read_bytes(); dna.normalize_actors(EX/'statements.csv',mapping,out)
            self.assertIn('Person A',out.read_text()); self.assertEqual(original,(EX/'statements.csv').read_bytes())
            with self.assertRaises(FileExistsError): dna.normalize_actors(EX/'statements.csv',mapping,out)
    def test_init_rejects_traversal_and_preserves_files(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d); dna.init(root,'study_1'); f=root/'projects/study_1/corpus/data.txt'; f.write_text('original'); dna.init(root,'study_1'); self.assertEqual(f.read_text(),'original')
            with self.assertRaises(ValueError): dna.init(root,'../outside')
            with self.assertRaises(ValueError): dna.init('relative','study')
    def test_manifest_hashes_without_paths_or_execution_claim(self):
        with tempfile.TemporaryDirectory() as d:
            d=pathlib.Path(d); src=d/'secret-path.txt'; src.write_text('evidence'); out=d/'manifest.json'
            dna.create_manifest([src],'DNA_EXECUTED',out); m=json.loads(out.read_text())
            self.assertTrue(m['status_is_self_reported']); self.assertEqual(len(m['input_sha256'][0]),64); self.assertNotIn(str(src),out.read_text())
            with self.assertRaises(FileExistsError): dna.create_manifest([src],'DNA_EXECUTED',out)
    def test_graphml_checks_edges_and_external_entities(self):
        with tempfile.TemporaryDirectory() as d:
            f=pathlib.Path(d)/'net.graphml'; f.write_text('<graphml xmlns="http://graphml.graphdrawing.org/xmlns"><graph edgedefault="undirected"><node id="a"/><node id="b"/><edge source="a" target="b"/></graph></graphml>')
            self.assertEqual(dna.graphml(f),[])
            f.write_text(f.read_text().replace('target="b"','target="missing"')); self.assertTrue(dna.graphml(f))
            f.write_text('<!DOCTYPE x [<!ENTITY z SYSTEM "file:///etc/passwd">]><x>&z;</x>')
            with self.assertRaises(ValueError): dna.graphml(f)
    def test_discovery_readonly_and_handles_missing_commands(self):
        with tempfile.TemporaryDirectory() as d, patch.object(dna.Path,'home',return_value=pathlib.Path(d)), patch.object(dna.shutil,'which',return_value=None), patch.object(dna.platform,'system',return_value='Linux'):
            before=list(pathlib.Path(d).iterdir()); result=dna.discover(); after=list(pathlib.Path(d).iterdir())
            self.assertEqual(before,after); self.assertFalse(result['java']['found_on_path']); self.assertIn('unknown',result['rDNA']['version_or_status'])
    def test_linux_documents_discovery(self):
        with patch.object(dna.platform,'system',return_value='Linux'), patch.object(dna.shutil,'which',return_value='/mock/xdg-user-dir'), patch.object(dna,'run',return_value=(0,'/mnt/redirected/Documents')):
            path, why=dna.documents(); self.assertEqual(str(path),'/mnt/redirected/Documents'); self.assertIn('XDG',why)
    def test_skill_metadata_and_svg(self):
        import xml.etree.ElementTree as ET
        skill=(ROOT/'.agents/skills/dna-research/SKILL.md').read_text(); self.assertTrue(skill.startswith('---\nname: dna-research\n')); self.assertIn('\ndescription:',skill)
        for file in (ROOT/'assets').glob('*.svg'): self.assertTrue(ET.parse(file).getroot().tag.endswith('svg'))

if __name__=='__main__': unittest.main()
