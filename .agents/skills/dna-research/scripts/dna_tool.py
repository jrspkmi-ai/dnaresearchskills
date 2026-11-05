#!/usr/bin/env python3
"""Local, dependency-free research workflow helpers. No network access."""
import argparse, csv, datetime as dt, hashlib, json, os, platform, re, shutil, subprocess, sys
from pathlib import Path
import xml.etree.ElementTree as ET


def run(cmd):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=15, check=False)
        return p.returncode, (p.stdout + p.stderr).strip()
    except (OSError, subprocess.TimeoutExpired):
        return -1, ''


def documents():
    system = platform.system()
    if system == 'Windows':
        try:
            import ctypes
            from ctypes import wintypes
            class GUID(ctypes.Structure):
                _fields_ = [('Data1', wintypes.DWORD), ('Data2', wintypes.WORD), ('Data3', wintypes.WORD), ('Data4', ctypes.c_ubyte * 8)]
            guid = GUID(0xFDD39AD0, 0x238F, 0x46AF, (ctypes.c_ubyte * 8)(0xAD, 0xB4, 0x6C, 0x85, 0x48, 0x03, 0x69, 0xC7))
            ptr = ctypes.c_wchar_p()
            shell = ctypes.windll.shell32
            shell.SHGetKnownFolderPath.argtypes = [ctypes.POINTER(GUID), wintypes.DWORD, wintypes.HANDLE, ctypes.POINTER(ctypes.c_wchar_p)]
            if shell.SHGetKnownFolderPath(ctypes.byref(guid), 0, None, ctypes.byref(ptr)) == 0:
                path = Path(ptr.value); ctypes.windll.ole32.CoTaskMemFree(ctypes.cast(ptr, ctypes.c_void_p)); return path, 'known-folder API; confirm with user'
        except (AttributeError, OSError, ValueError):
            pass
    if system == 'Linux' and shutil.which('xdg-user-dir'):
        rc, out = run(['xdg-user-dir', 'DOCUMENTS'])
        if rc == 0 and out and Path(out).is_absolute() and Path(out) != Path.home():
            return Path(out), 'XDG; confirm with user'
    if system == 'Darwin':
        candidate = Path.home() / 'Documents'
        if candidate.is_dir(): return candidate, 'conventional path; iCloud or redirects need confirmation'
    return None, 'unknown; choose a root explicitly'


def discover():
    doc, source = documents()
    result = {'host_os': platform.system(), 'architecture': platform.machine(),
              'documents': {'status': source, 'exists': bool(doc and doc.is_dir()), 'path': 'redacted' if doc else None},
              'write_permission': 'not tested', 'execution': 'local subprocesses permitted for successful probes',
              'scope': 'PATH and limited standard locations; unknown is not absent'}
    java = shutil.which('java')
    if java:
        rc, output = run([java, '-version'])
        first = output.splitlines()[0] if output else 'unknown'
        result['java'] = {'found_on_path': True, 'version_output': first[:160], 'probe_ok': rc == 0, 'path': 'redacted'}
    else: result['java'] = {'found_on_path': False}
    r = shutil.which('Rscript')
    result['Rscript'] = {'found_on_path': bool(r), 'path': 'redacted' if r else None}
    if r:
        rc, out = run([r, '--version']); result['Rscript']['version_output'] = out.splitlines()[0][:160] if out else 'unknown'
        for pkg in ('rJava', 'rDNA'):
            code = 'p <- '+repr(pkg)+'; if (!requireNamespace(p, quietly=TRUE)) {cat("NOT_INSTALLED"); quit(status=2)}; cat(as.character(packageVersion(p)))'
            rc, out = run([r, '-e', code]); result[pkg] = {'probe_ok': rc == 0, 'version_or_status': (out.rsplit(' ', 1)[-1] if rc == 0 and re.fullmatch(r'[0-9]+(?:\.[0-9]+)+', out.rsplit(' ', 1)[-1]) else 'unknown; inspect locally')}
    else:
        result['rJava'] = result['rDNA'] = {'probe_ok': False, 'version_or_status': 'unknown: Rscript not found'}
    homes = [Path.home() / 'Documents' / 'DNA_Tools' / 'apps' / 'dna', Path.home() / 'Downloads']
    candidates = []
    for folder in homes:
        try:
            if folder.is_dir(): candidates.extend(f.name for f in folder.glob('dna-*.jar') if f.is_file())
        except OSError: pass
    result['dna'] = {'candidate_filenames': sorted(set(candidates)), 'version_source': 'filename only; not verified', 'search': 'Documents/DNA_Tools/apps/dna and Downloads only'}
    for app in ['visone', 'gephi']:
        found = bool(shutil.which(app))
        if platform.system() == 'Darwin': found = found or Path('/Applications/'+app.capitalize()+'.app').exists()
        result[app] = {'found_in_limited_search': found, 'version': 'unknown'}
    return result


def read_csv(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or len(reader.fieldnames) != len(set(reader.fieldnames)): raise ValueError('Missing or duplicate header')
        rows = list(reader)
        if any(None in row for row in rows): raise ValueError('Row has more fields than header')
        return reader.fieldnames, rows


def validate_corpus(path):
    fields, rows = read_csv(path); required = {'document_id','source_id','date','title'}; errors=[]; seen=set()
    if required - set(fields): return ['Missing columns: '+', '.join(sorted(required-set(fields)))]
    if not rows: errors.append('No rows')
    for n,row in enumerate(rows,2):
        for key in required:
            if not (row.get(key) or '').strip(): errors.append(f'Line {n}: missing {key}')
        if row['document_id'] in seen: errors.append(f'Line {n}: duplicate document_id')
        seen.add(row['document_id'])
        try:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', row['date']): raise ValueError()
            dt.date.fromisoformat(row['date'])
        except ValueError: errors.append(f'Line {n}: date must be ISO YYYY-MM-DD')
    return errors


def validate_statements(path, corpus, codebook):
    fields, rows = read_csv(path); required={'statement_id','document_id','actor','concept','qualifier','event_time','evidence_location','review_status','reviewer'}; errors=[]; seen=set()
    if required-set(fields): return ['Missing columns: '+', '.join(sorted(required-set(fields)))]
    corpus_errors = validate_corpus(corpus)
    if corpus_errors: return ['Invalid corpus: '+x for x in corpus_errors]
    _, docs = read_csv(corpus); docids = {r['document_id'] for r in docs}
    with open(codebook, encoding='utf-8') as f: cb=json.load(f)
    allowed=cb.get('qualifiers');
    if not isinstance(allowed,list) or not allowed or not all(isinstance(x,str) and x for x in allowed): raise ValueError('Codebook must have a non-empty qualifiers list')
    if not rows: errors.append('No rows')
    for n,row in enumerate(rows,2):
        for key in required-{'reviewer'}:
            if not (row.get(key) or '').strip(): errors.append(f'Line {n}: missing {key}')
        if row['statement_id'] in seen: errors.append(f'Line {n}: duplicate statement_id')
        seen.add(row['statement_id'])
        if row['document_id'] not in docids: errors.append(f'Line {n}: unknown document_id')
        if row['qualifier'] not in allowed: errors.append(f'Line {n}: qualifier absent from codebook')
        if row['review_status'] not in ('AI_CANDIDATE','HUMAN_VALIDATED'): errors.append(f'Line {n}: invalid review_status')
        if row['review_status']=='HUMAN_VALIDATED' and not row['reviewer'].strip(): errors.append(f'Line {n}: validated row requires reviewer')
        try:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', row['event_time']): raise ValueError()
            dt.date.fromisoformat(row['event_time'])
        except ValueError: errors.append(f'Line {n}: event_time must be ISO YYYY-MM-DD')
    return errors


def normalize_actors(path, mapping_path, output):
    fields, rows = read_csv(path)
    if 'actor' not in fields: raise ValueError('Missing actor column')
    with open(mapping_path, encoding='utf-8') as f: mapping = json.load(f)
    if not isinstance(mapping, dict) or not all(isinstance(k,str) and k.strip() and isinstance(v,str) and v.strip() for k,v in mapping.items()):
        raise ValueError('Mapping must be a JSON object with nonempty string names')
    for row in rows: row['actor'] = mapping.get(row['actor'], row['actor'])
    with open(output, 'x', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    print('Created a separate normalized copy. Review mappings and retain originals.')

def create_manifest(files, status, output):
    # Only digests are stored, not paths, file contents, or credentials.
    hashes=[]
    for path in files:
        digest=hashlib.sha256()
        with open(path,'rb') as stream:
            for block in iter(lambda: stream.read(1024*1024), b''): digest.update(block)
        hashes.append(digest.hexdigest())
    manifest={'created_utc':dt.datetime.now(dt.timezone.utc).isoformat(), 'reported_status':status,
              'status_is_self_reported':True, 'input_sha256':hashes,
              'note':'Hashes do not prove execution, review, correctness, or visualization. Add research metadata privately.'}
    with open(output,'x',encoding='utf-8') as f: json.dump(manifest,f,indent=2); f.write('\n')
    print('Created manifest; status is self-reported and must be supported by evidence.')

def graphml(path):
    data=Path(path).read_bytes()
    if len(data)>50_000_000: raise ValueError('GraphML exceeds 50 MB safety limit')
    content=data.decode('utf-8-sig')
    if '<!DOCTYPE' in content.upper() or '<!ENTITY' in content.upper(): raise ValueError('DTD and entity definitions are not allowed')
    root=ET.fromstring(content); ns='{http://graphml.graphdrawing.org/xmlns}'
    errors=[]
    if root.tag!=ns+'graphml': errors.append('Not a GraphML root element')
    graphs=list(root.iter(ns+'graph'))
    if not graphs: errors.append('No graph element')
    for g in graphs:
        ids=[n.get('id') for n in g.findall(ns+'node')]; seen=set(ids)
        if None in seen or len(ids)!=len(seen): errors.append('Missing or duplicate node IDs')
        for e in g.findall(ns+'edge'):
            if e.get('source') not in seen or e.get('target') not in seen: errors.append('Edge refers to an unknown node')
    return errors


def init(root, project):
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}', project): raise ValueError('Project ID: use 1-64 letters, numbers, underscores or hyphens')
    root=Path(root).expanduser()
    if not root.is_absolute(): raise ValueError('Root must be absolute')
    root=root.resolve()
    paths=[root/'projects'/project/x for x in ('corpus','codebook','statements','database','analysis','audit')]+[root/'output'/project/x for x in ('networks','figures','tables','reports','manifests')]
    for folder in paths:
        if not folder.resolve().is_relative_to(root): raise ValueError('Symlink escapes root')
    for folder in paths: folder.mkdir(parents=True, exist_ok=True)
    print('Project folders created or already present; existing files were not overwritten. Root is private.')


def main():
    parser=argparse.ArgumentParser(description=__doc__); sub=parser.add_subparsers(dest='cmd',required=True)
    sub.add_parser('discover'); x=sub.add_parser('init'); x.add_argument('--root',required=True); x.add_argument('--project',required=True)
    x=sub.add_parser('validate-corpus'); x.add_argument('file')
    x=sub.add_parser('validate-statements'); x.add_argument('file'); x.add_argument('--corpus',required=True); x.add_argument('--codebook',required=True)
    x=sub.add_parser('graphml'); x.add_argument('file')
    x=sub.add_parser('manifest'); x.add_argument('--file',action='append',required=True); x.add_argument('--output',required=True); x.add_argument('--status',required=True,choices=['AI_CANDIDATE','HUMAN_VALIDATED','DNA_EXECUTED','EXTERNALLY_COMPUTED','VISUALIZED'])
    x=sub.add_parser('normalize-actors'); x.add_argument('file'); x.add_argument('--mapping',required=True); x.add_argument('--output',required=True)
    a=parser.parse_args()
    try:
        if a.cmd=='discover': print(json.dumps(discover(),indent=2)); return 0
        if a.cmd=='init': init(a.root,a.project); return 0
        if a.cmd=='normalize-actors': normalize_actors(a.file,a.mapping,a.output); return 0
        if a.cmd=='manifest': create_manifest(a.file,a.status,a.output); return 0
        if a.cmd=='validate-corpus': errors=validate_corpus(a.file)
        elif a.cmd=='validate-statements': errors=validate_statements(a.file,a.corpus,a.codebook)
        else: errors=graphml(a.file)
        if errors:
            print('\n'.join(errors),file=sys.stderr); return 1
        print('PASS: structural checks only; no claim of factual accuracy or tool execution.'); return 0
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, ET.ParseError, json.JSONDecodeError) as e:
        print('ERROR:',str(e),file=sys.stderr); return 2
if __name__=='__main__': sys.exit(main())
