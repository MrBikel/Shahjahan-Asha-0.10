#!/usr/bin/env python3
"""Validate delivered and round-trip Shahjahan Asha private test fonts."""
import collections, hashlib, json, subprocess
from pathlib import Path
from fontTools.ttLib import TTFont

ROOT=Path(__file__).resolve().parents[1]
V=ROOT/'tests'/'validation'; V.mkdir(exist_ok=True)
DEL=ROOT/'ShahjahanAsha-SourceGlyphSeed-0.13-private-test.ttf'
ROUND=V/'roundtrip.ttf'; CORP=ROOT/'tests'/'corpus.txt'
SFD=ROOT/'ShahjahanAsha-SourceGlyphSeed-0.13-private-test.sfd'
FEA=ROOT/'ShahjahanAsha-opentype-features-0.13.fea'
PHYSICAL=0x4007e
BITS={0x2:'open contour',0x4:'self-intersection',0x8:'wrong contour direction',0x10:'flipped reference',0x20:'missing extrema',0x40:'missing glyph naming substitution',0x40000:'coordinates too far apart',0x80000:'nonintegral coordinates (source SFD floats)',0x100000:'missing anchor',0x200000:'duplicate glyph name',0x400000:'duplicate Unicode'}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run(cmd):
 p=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 return {'returncode':p.returncode,'output':p.stdout}
def shape(font,text,size=24):
 r=run(['hb-shape','--output-format=json','--font-size',str(size*64),str(font),text])
 if r['returncode']: raise RuntimeError(r['output'])
 return json.loads(r['output'])
def norm_shape(sh): return [(x.get('g'),x.get('cl'),x.get('dx'),x.get('dy'),x.get('ax'),x.get('ay')) for x in sh]
def inspect(path):
 f=TTFont(path,checkChecksums=2); cmap={cp:g for t in f['cmap'].tables if t.isUnicode() for cp,g in t.cmap.items()}
 names={str(n.nameID):n.toUnicode() for n in f['name'].names}
 metrics={'unitsPerEm':f['head'].unitsPerEm,'hheaAscent':f['hhea'].ascent,'hheaDescent':f['hhea'].descent,'hheaLineGap':f['hhea'].lineGap,'typoAscender':f['OS/2'].sTypoAscender,'typoDescender':f['OS/2'].sTypoDescender,'winAscent':f['OS/2'].usWinAscent,'winDescent':f['OS/2'].usWinDescent}
 errs=[]
 for table in ['head','hhea','maxp','OS/2','hmtx','cmap','loca','glyf','name','post','GSUB','GPOS','GDEF']:
  if table not in f: errs.append('missing '+table)
 order=f.getGlyphOrder()
 if len(order)!=len(set(order)): errs.append('duplicate glyph order names')
 if 'glyf' in f:
  for g in order:
   try: f['glyf'][g].isComposite()
   except Exception as e: errs.append(f'glyf {g}: {e}')
 return f,cmap,names,metrics,errs

def ff_validate(path):
 code='''import fontforge,json,sys\nf=fontforge.open(sys.argv[1]); out=[]\nfor g in f.glyphs():\n try: out.append({"glyph":g.glyphname,"unicode":int(g.unicode),"mask":int(g.validate(True)),"anchors":[list(a) for a in g.anchorPoints]})\n except Exception as e: out.append({"glyph":g.glyphname,"error":str(e)})\nprint(json.dumps(out,ensure_ascii=False))\n'''
 p=subprocess.run(['/usr/bin/fontforge','-lang=py','-c',code,str(path)],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 result=[]
 for line in p.stdout.splitlines():
  try:
   x=json.loads(line)
   if isinstance(x,list): result=x
  except Exception: pass
 if not result: raise RuntimeError(f'FontForge validation did not return records for {path}: {p.stderr}')
 for rec in result:
  mask=rec.get('mask',0)
  rec['maskHex']=f'0x{mask:x}'
  rec['decodedFlags']=[label for bit,label in BITS.items() if mask&bit]
  rec['physicalErrorMaskHex']=f'0x{mask&PHYSICAL:x}'
  rec['missingAnchorClasses']=[f'Anchor-{i}' for i in range(10) if f'Anchor-{i}' not in [a[0] for a in rec.get('anchors',[])]] if mask&0x100000 else []
 return {'returncode':p.returncode,'stderr':p.stderr[-1000:],'glyphCount':len(result),'nonzeroGlyphs':[r for r in result if r.get('mask',0)],'maskDistribution':{f'0x{k:x}':v for k,v in sorted(collections.Counter(r.get('mask',0) for r in result).items())},'physicalErrorCount':sum(bool(r.get('mask',0)&PHYSICAL) for r in result)}

report={'inputs':{},'tools':{},'tests':{},'limitations':[]}
for p in (DEL,SFD,FEA,CORP): report['inputs'][p.name]={'path':str(p),'sha256':sha(p)}
for cmd in (['fontforge','-version'],['ots-sanitize','--version'],['hb-shape','--version']): report['tools'][cmd[0]]=run(cmd)['output'].splitlines()[:4]
import fontTools; report['tools']['fontTools']=fontTools.__version__
fonts={}
for key,p in [('delivered',DEL),('roundtrip',ROUND)]:
 f,c,n,m,e=inspect(p); fonts[key]=(f,c,n,m)
 report['tests'][key+'_tables']={'errors':e,'glyphCount':len(f.getGlyphOrder()),'cmapEntries':len(c),'names':n,'metrics':m,'tables':f.keys()}
lines=[(n,s.strip()) for n,s in enumerate(CORP.read_text().splitlines(),1) if s.strip() and not s.lstrip().startswith('#')]
shape_result={'lineCount':len(lines),'sizes':[12,16,24,36,48],'comparisons':0,'differences':[],'notdef':[]}
for ln,text in lines:
 for size in shape_result['sizes']:
  a=shape(DEL,text,size); b=shape(ROUND,text,size)
  for font,sh in [('delivered',a),('roundtrip',b)]:
   if any(x.get('g')=='.notdef' for x in sh): shape_result['notdef'].append({'line':ln,'size':size,'text':text,'font':font})
  shape_result['comparisons']+=1
  if norm_shape(a)!=norm_shape(b): shape_result['differences'].append({'line':ln,'size':size,'text':text,'delivered':a,'roundtrip':b})
report['tests']['corpus_shaping']=shape_result
_,cmap,_,_=fonts['delivered']; required_punct='।,. :;!?“”‘’-—()[]/%'
coverage={'missingPunctuation':[f'U+{ord(c):04X} {c}' for c in required_punct if not c.isspace() and ord(c) not in cmap], 'requiredBases':{c:ord(c) in cmap for c in 'কগটতবরশ'},'matras':['া','ি','ী','ু','ূ','ৃ','ে','ৈ','ো','ৌ'],'requiredSequences':{}}
for base in 'কগটতবরশ':
 for m in coverage['matras']:
  seq=base+m; sh=shape(DEL,seq,24)
  coverage['requiredSequences'][seq]={'mapped':all(x.get('g')!='.notdef' for x in sh),'glyphs':[x.get('g') for x in sh]}
ligatures={'ক্ষ':'lig_ksha','ক্ষ্ম':'lig_kshma','ক্র':'lig_kra','ক্ক':'lig_kka','ক্ত':'lig_kta','ক্ল':'lig_kla'}
for s,g in ligatures.items():
 sh=shape(DEL,s,24); coverage['requiredSequences'][s]={'expectedLigature':g,'shapedGlyphs':[x.get('g') for x in sh],'formed':g in [x.get('g') for x in sh]}
report['tests']['coverage']=coverage
# Separate codepoint/.notdef inventory from linguistic shaping acceptance.
report['tests']['notdef_and_codepoint_checks']={'purpose':'Codepoint mapping and absence of .notdef in named tests; not linguistic or visual shaping acceptance.','corpusNotdefCount':len(shape_result['notdef']),'cmapEntries':len(cmap),'punctuationCoveragePass':not coverage['missingPunctuation'],'requiredBaseCoveragePass':all(coverage['requiredBases'].values()),'baseMatraPairCount':70,'baseMatraAllMapped':all(x['mapped'] for s,x in coverage['requiredSequences'].items() if len(s)==2 and s[0] in 'কগটতবরশ')}
report['tests']['ots']={k:run(['ots-sanitize',str(p)]) for k,p in [('delivered',DEL),('roundtrip',ROUND)]}
report['tests']['fontforge_flags']={'definitions':{f'0x{k:x}':v for k,v in BITS.items()},'physicalMaskHex':f'0x{PHYSICAL:x}','sourceSFD':ff_validate(SFD),'deliveredTTF':ff_validate(DEL),'roundtripTTF':ff_validate(ROUND),'sources':['https://fontforge.org/docs/scripting/python/fontforge.html','https://raw.githubusercontent.com/fontforge/fontforge/master/fontforge/splinefont.h']}
# Preserve concrete anchor evidence for remaining missing-anchor flags.
ttf_records=report['tests']['fontforge_flags']['deliveredTTF']['nonzeroGlyphs']
byname={r['glyph']:r for r in ttf_records}
anchor_examples=[]
for name in ['uni0995','uni09A1','uni0985','uni0988','uni0993']:
 r=byname.get(name)
 if r: anchor_examples.append({'glyph':name,'unicode':f'U+{r["unicode"]:04X}','maskHex':r['maskHex'],'presentAnchors':[a[0] for a in r.get('anchors',[])],'missingAnchorClasses':r['missingAnchorClasses']})
report['tests']['anchor_warning_examples']=anchor_examples
anchor_sequences={}
for seq,label,direct in [('ক়','consonant + nukta (anchor diagnostic)',None),('ড়','DDA + nukta (canonical dotted-letter composition)','ড়'),('অ্','independent vowel + hasanta (anchor diagnostic)',None)]:
 shaped=shape(DEL,seq,24)
 marks=[x for x in shaped if x.get('g') in ('uni09BC','uni09CD')]
 equivalent=shape(DEL,direct,24) if direct else None
 anchor_sequences[seq]={'case':label,'glyphs':shaped,'unattachedMarkGlyphs':[x.get('g') for x in marks],'markOffsets':[(x.get('g'),x.get('dx',0),x.get('dy',0)) for x in marks],'nonzeroMarkAttachmentObserved':any(x.get('dx',0)!=0 or x.get('dy',0)!=0 for x in marks),'canonicalTarget':direct,'matchesCanonicalTarget':norm_shape(shaped)==norm_shape(equivalent) if equivalent else None,'coveredByAcceptance':False}
report['tests']['anchor_dependent_sequence_probes']={'note':'Diagnostic probes only, not expanded linguistic acceptance. ক় and অ্ retain unattached marks because applicable base anchors are missing. ড় is expected to become one canonical precomposed dotted glyph via ccmp and is separately covered by exact direct/decomposed tests; it is not evidence of a separate mark attachment.','sequences':anchor_sequences}
report['tests']['source_vs_roundtrip_metadata']={'delivered':fonts['delivered'][3],'roundtrip':fonts['roundtrip'][3],'match':fonts['delivered'][3]==fonts['roundtrip'][3],'method':'SFD Ascent/Descent/OS2/Hhea fields supply source metadata; FEA compilation changes layout tables only.'}
report['limitations']=['No full Bengali shaping acceptance claimed; only the listed 15-line corpus, 70 base×matra mapping cases and six named ligatures are checked.','Missing-anchor warnings are real positioning limitations, not harmless warnings: missing base anchors prevent the associated mark attachment in those contexts; only sequences explicitly verified in coverage are claimed.','No general reph or phala support is claimed; unlisted conjuncts and reph sequences are unsupported/unvalidated.','Notdef/codepoint coverage is reported separately and does not imply linguistic shaping support.','Source photographs were owner-provided; no 3804/3805 material was used; no benchmark font outlines were used.']
(V/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'validation_json':str(V/'validation.json'),'delivered_sha256':report['inputs'][DEL.name]['sha256'],'roundtrip_sha256':sha(ROUND),'corpus':shape_result,'coverage':report['tests']['notdef_and_codepoint_checks'],'masks':{k:v['maskDistribution'] for k,v in report['tests']['fontforge_flags'].items() if isinstance(v,dict) and 'maskDistribution' in v},'physicalErrors':{k:v['physicalErrorCount'] for k,v in report['tests']['fontforge_flags'].items() if isinstance(v,dict) and 'physicalErrorCount' in v}},ensure_ascii=False,indent=2))
