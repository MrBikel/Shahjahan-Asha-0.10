#!/usr/bin/env python3
from pathlib import Path
from fontTools.ttLib import TTFont
import json, subprocess

P=Path(__file__).resolve().parent.parent
FONT=P/'ShahjahanAsha-SourceGlyphSeed-0.13-private-test.ttf'
f=TTFont(FONT)

def shape(s):
    return json.loads(subprocess.check_output(['hb-shape','--output-format=json',str(FONT),s],text=True))

def boxes(name):
    g=f['glyf'][name];start=0;out=[]
    for end in g.endPtsOfContours:
        pts=g.coordinates[start:end+1];start=end+1
        out.append((min(x for x,y in pts),min(y for x,y in pts),max(x for x,y in pts),max(y for x,y in pts)))
    return out

pairs=[('ড়','ড\u09bc'),('ঢ়','ঢ\u09bc'),('য়','য\u09bc')]
canonical=[];separation=[];all_shapes={}
for direct,decomposed in pairs:
    for sign in ('','ু','ূ','ৃ'):
        a,b=shape(direct+sign),shape(decomposed+sign)
        same=a==b
        canonical.append({'direct':direct+sign,'decomposed':decomposed+sign,'exactShapeMatch':same})
        assert same,(direct,sign,a,b)
        all_shapes[direct+sign]=a
        if sign:
            base=a[0];dot=[x for x in boxes(base['g']) if x[3]<0 and x[2]-x[0]<=100 and x[3]-x[1]<=100]
            assert len(dot)==1,(direct,dot)
            mark=a[-1];g=f['glyf'][mark['g']];g.recalcBounds(f['glyf'])
            dot_bottom=base['dy']+dot[0][1]
            mark_top=mark['dy']+g.yMax
            gap=dot_bottom-mark_top
            assert gap>=10,(direct,sign,gap)
            separation.append({'text':direct+sign,'dotBottom':dot_bottom,'belowMarkTop':mark_top,'verticalGapUnits':gap,'pass':True})
report={'canonicalEquivalence':canonical,'belowDotSeparation':separation,'shapes':all_shapes,
        'meaning':'12 exact direct/decomposed shaping comparisons; 9 measured vertical ink-box separations. This checks these three dot letters with u/uu/vocalic-r, not all possible mark stacks.'}
(P/'tests/below-dot-combinations.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
text='ড় ড়ু ড়ূ ড়ৃ\nঢ় ঢ়ু ঢ়ূ ঢ়ৃ\nয় য়ু য়ূ য়ৃ\nড\u09bc ঢ\u09bc য\u09bc'
subprocess.run(['hb-view','--font-size=64','--margin=15','--line-space=10','--output-format=png',f'--output-file={P}/proofs/hb/below-dot-combinations-64px.png',str(FONT),text],check=True)
print('Canonical pairs:',len(canonical),'matched; below-dot separations:',len(separation),'passed; minimum gap',min(x['verticalGapUnits']for x in separation))
