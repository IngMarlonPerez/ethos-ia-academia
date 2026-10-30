import re
from xml.sax.saxutils import escape
BS=chr(92)
FONT='<w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr>'
CTRL='<m:ctrlPr>'+FONT+'</m:ctrlPr>'
SYM={'varepsilon':'ε','Delta':'Δ','times':'×','approx':'≈','lt':'<','gt':'>','cdot':'·'}
SYM2={'alpha':'α','beta':'β','theta':'θ','oplus':'⊕','odot':'⊙','in':'∈','neq':'≠','ge':'≥','le':'≤','rightarrow':'→','Rightarrow':'⇒'}
ITALIC={'alpha','beta','theta'}
FUNCS={'cos','arccos','sen','sin','tan','ln','log'}
def run(t,plain=False):
    p='<m:rPr><m:sty m:val="p"/></m:rPr>' if plain else ''
    return '<m:r>%s%s<m:t xml:space="preserve">%s</m:t></m:r>'%(p,FONT,escape(t))
def group(s,i):
    d=0;j=i
    while True:
        if s[j]=='{': d+=1
        elif s[j]=='}':
            d-=1
            if d==0: return s[i+1:j],j+1
        j+=1
def parse(s):
    out=[];i=0
    while i<len(s):
        c=s[i]
        if c==BS:
            m=re.match(r'\\([A-Za-z]+|.)',s[i:]); n=m.group(1); i+=len(m.group(0))
            if n=='frac':
                a,i=group(s,i);b,i=group(s,i)
                out.append('<m:f><m:fPr>%s</m:fPr><m:num>%s</m:num><m:den>%s</m:den></m:f>'%(CTRL,parse(a),parse(b)))
            elif n=='sqrt':
                a,i=group(s,i); out.append('<m:rad><m:radPr><m:degHide m:val="1"/>%s</m:radPr><m:deg/><m:e>%s</m:e></m:rad>'%(CTRL,parse(a)))
            elif n=='vec':
                a,i=group(s,i); out.append('<m:acc><m:accPr><m:chr m:val="'+chr(0x20d7)+'"/>%s</m:accPr><m:e>%s</m:e></m:acc>'%(CTRL,parse(a)))
            elif n=='mathbb':
                a,i=group(s,i); out.append('<m:r><m:rPr><m:scr m:val="double-struck"/><m:sty m:val="p"/></m:rPr>%s<m:t>%s</m:t></m:r>'%(FONT,a))
            elif n in FUNCS: out.append(run(n,True)); out.append(run(' ',True))
            elif n in SYM2: out.append(run(SYM2[n],n not in ITALIC))
            elif n in('text','mathrm'):
                a,i=group(s,i); out.append(run(a,True))
            elif n=='left':
                op=s[i];i+=1
                if op==BS: op='‖' if s[i]=='|' else s[i]; i+=1
                k=s.index(BS+'right',i); inner=s[i:k]; cl=s[k+6]; i=k+7
                if cl==BS: cl='‖'; i+=1
                out.append('<m:d><m:dPr><m:begChr m:val="%s"/><m:endChr m:val="%s"/>%s</m:dPr><m:e>%s</m:e></m:d>'%(op,cl,CTRL,parse(inner)))
            elif n=='%': out.append(run('%',True))
            elif n=='$': out.append(run('$',True))
            elif n in SYM: out.append(run(SYM[n],n not in('varepsilon','Delta')))
            elif n in(';',',',' '): out.append(run(' ',True))
            else: raise ValueError(n)
        elif c=='_':
            i+=1
            if s[i]=='{': a,i=group(s,i)
            else: a=s[i];i+=1
            base=out.pop()
            out.append('<m:sSub><m:sSubPr>%s</m:sSubPr><m:e>%s</m:e><m:sub>%s</m:sub></m:sSub>'%(CTRL,base,parse(a)))
        elif c=='^':
            i+=1
            if s[i]=='{': a,i=group(s,i)
            else: a=s[i];i+=1
            base=out.pop()
            out.append('<m:sSup><m:sSupPr>%s</m:sSupPr><m:e>%s</m:e><m:sup>%s</m:sup></m:sSup>'%(CTRL,base,parse(a)))
        elif c=='{':
            a,i=group(s,i); out.append(parse(a))
        elif c.isdigit():
            m=re.match(r'[0-9]+(?:[,.][0-9]+)?',s[i:]); out.append(run(m.group(0))); i+=len(m.group(0))
        elif c=='~': out.append(run(' ',True)); i+=1
        elif c=='-': out.append(run('−',True)); i+=1
        elif c.isalpha(): out.append(run(c)); i+=1
        else: out.append(run(c,True)); i+=1
    return ''.join(out)
def omath(s): return '<m:oMath>'+parse(s)+'</m:oMath>'
RP='<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>%s<w:sz w:val="%d"/><w:szCs w:val="%d"/><w:lang w:val="es-EC"/></w:rPr>'
def tr(t,b=False,i=False,sz=24):
    fl=('<w:b/>' if b else '')+('<w:i/>' if i else '')
    return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>'%(RP%(fl,sz,sz),escape(t))
def inline(text,b=False,i=False,sz=24):
    out=''
    for k,part in enumerate(re.split(r'\$\$(.+?)\$\$',text)):
        if k%2: out+=omath(part)
        elif part: out+=tr(part,b,i,sz)
    return out
def para(text,kind='body'):
    if kind=='body':
        return '<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="480" w:lineRule="auto"/><w:ind w:firstLine="720"/><w:jc w:val="both"/></w:pPr>%s</w:p>'%inline(text)
    if kind=='data':
        return '<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="480" w:lineRule="auto"/></w:pPr>%s</w:p>'%inline(text)
    if kind=='h1':
        rp='<w:rPr><w:b/><w:bCs/><w:color w:val="1A3A7A"/><w:sz w:val="30"/><w:szCs w:val="30"/><w:lang w:val="es-EC"/></w:rPr>'
        return '<w:p><w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="240" w:after="120" w:line="240" w:lineRule="auto"/><w:outlineLvl w:val="1"/>%s</w:pPr><w:r>%s<w:t>%s</w:t></w:r></w:p>'%(rp,rp,escape(text))
    if kind in('h2','h3'):
        return '<w:p><w:pPr><w:keepNext/><w:spacing w:before="120" w:after="60" w:line="360" w:lineRule="auto"/><w:outlineLvl w:val="%d"/></w:pPr>%s</w:p>'%(2 if kind=='h2' else 3,tr(text,True,kind=='h3'))
    if kind=='eq':
        return '<w:p><w:pPr><w:keepLines/><w:spacing w:before="60" w:after="60" w:line="360" w:lineRule="auto"/><w:jc w:val="center"/></w:pPr><m:oMathPara><m:oMathParaPr><m:jc m:val="center"/></m:oMathParaPr>%s</m:oMathPara></w:p>'%omath(text)
    if kind=='ref':
        return '<w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="480" w:lineRule="auto"/><w:ind w:left="720" w:hanging="720"/><w:jc w:val="left"/></w:pPr>%s</w:p>'%inline(text)
    if kind=='pb': return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'
    if kind=='cap':
        return '<w:p><w:pPr><w:keepNext/><w:spacing w:before="120" w:after="60" w:line="240" w:lineRule="auto"/></w:pPr>%s</w:p>'%tr(text,True)
def table(rows,widths,header=True):
    b=''.join('<w:%s w:val="single" w:sz="4" w:space="0" w:color="1A3A7A"/>'%x for x in('top','left','bottom','right','insideH','insideV'))
    x='<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/><w:jc w:val="center"/><w:tblBorders>%s</w:tblBorders><w:tblLayout w:type="fixed"/><w:tblCellMar><w:left w:w="80" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>%s</w:tblGrid>'%(sum(widths),b,''.join('<w:gridCol w:w="%d"/>'%w for w in widths))
    for r,row in enumerate(rows):
        hd=r==0 and header
        x+='<w:tr>'+('<w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>' if hd else '<w:trPr><w:cantSplit/></w:trPr>')
        for w,cell in zip(widths,row):
            shade='<w:shd w:val="clear" w:color="auto" w:fill="DCE6F2"/>' if hd else ''
            x+='<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s<w:vAlign w:val="center"/></w:tcPr><w:p><w:pPr><w:spacing w:before="40" w:after="40" w:line="240" w:lineRule="auto"/><w:ind w:firstLine="0"/><w:jc w:val="center"/></w:pPr>%s</w:p></w:tc>'%(w,shade,inline(cell,hd,False,20))
        x+='</w:tr>'
    return x+'</w:tbl>'
