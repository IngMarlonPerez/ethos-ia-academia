# -*- coding: utf-8 -*-
"""Helpers mínimos para generar WordprocessingML (Arial 12, interlineado sencillo)."""
import re
from xml.sax.saxutils import escape

NAVY = "1B3247"
NB = " "


def rpr(sz=24, b=False, i=False, color=None, hl=False, u=False):
    s = '<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial" w:eastAsia="Arial"/>'
    if b:
        s += '<w:b w:val="1"/><w:bCs w:val="1"/>'
    if i:
        s += '<w:i w:val="1"/><w:iCs w:val="1"/>'
    if color:
        s += f'<w:color w:val="{color}"/>'
    s += f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>'
    if hl:
        s += '<w:highlight w:val="yellow"/>'
    if u:
        s += '<w:u w:val="single"/>'
    return s + '</w:rPr>'


TOK = re.compile(r'(\*\*.+?\*\*|==.+?==|\*[^*]+?\*)')


def runs(text, sz=24, b=False, i=False, color=None):
    out = []
    for part in TOK.split(text):
        if not part:
            continue
        bb, ii, hl = b, i, False
        if part.startswith('**') and part.endswith('**') and len(part) > 4:
            part, bb = part[2:-2], True
        elif part.startswith('==') and part.endswith('==') and len(part) > 4:
            part, hl = part[2:-2], True
        elif part.startswith('*') and part.endswith('*') and len(part) > 2:
            part, ii = part[1:-1], True
        out.append(f'<w:r>{rpr(sz, bb, ii, color, hl)}<w:t xml:space="preserve">{escape(part)}</w:t></w:r>')
    return ''.join(out)


def para(text, sz=24, align="both", before=0, after=100, left=0, hanging=0, first=0,
         b=False, i=False, color=None, keep_next=False, style=None, num=None, border_bottom=False,
         page_break_before=False):
    ppr = ''
    if style:
        ppr += f'<w:pStyle w:val="{style}"/>'
    if keep_next:
        ppr += '<w:keepNext w:val="1"/>'
    if page_break_before:
        ppr += '<w:pageBreakBefore w:val="1"/>'
    if border_bottom:
        ppr += f'<w:pBdr><w:bottom w:val="single" w:sz="6" w:space="1" w:color="{NAVY}"/></w:pBdr>'
    if num is not None:
        ppr += f'<w:numPr><w:ilvl w:val="0"/><w:numId w:val="{num}"/></w:numPr>'
    ppr += f'<w:spacing w:before="{before}" w:after="{after}" w:line="240" w:lineRule="auto"/>'
    ind = f'<w:ind w:left="{left}"'
    if hanging:
        ind += f' w:hanging="{hanging}"'
    else:
        ind += f' w:firstLine="{first}"'
    ind += '/>'
    ppr += ind
    ppr += f'<w:jc w:val="{align}"/>'
    return f'<w:p><w:pPr>{ppr}</w:pPr>{runs(text, sz, b, i, color)}</w:p>'


def h1(text):
    return para(text, b=True, color=NAVY, before=200, after=100, keep_next=True, style="Heading1",
                align="left", border_bottom=True)


def h2(text):
    return para(text, b=True, color=NAVY, before=120, after=60, keep_next=True, style="Heading2", align="left")


def resp(name):
    return para(f"Responsable: {name}", sz=22, i=True, after=80, align="left", keep_next=True)


def bullet(text, sz=24, after=40):
    return para(text, sz=sz, num=1, left=360, hanging=360, after=after)


def caption(n, title):
    return (para(f"Tabla {n}", b=True, after=0, keep_next=True, align="left", sz=22) +
            para(title, i=True, after=60, keep_next=True, align="left", sz=22))


def nota(text):
    return para("*Nota.* " + text, sz=18, after=140, align="left")


def _cell(content, w, sz, header=False, fill=None, bold=False, keep=False):
    tcpr = f'<w:tcW w:w="{w}" w:type="dxa"/>'
    if header:
        tcpr += f'<w:shd w:val="clear" w:color="auto" w:fill="{NAVY}"/>'
    elif fill:
        tcpr += f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>'
    ps = ''
    lines = content.split('\n') if content else ['']
    for ln in lines:
        if ln.startswith('- '):
            ps += para(ln[2:], sz=sz, num=1, left=200, hanging=200, after=10, align="left", keep_next=keep)
        else:
            ps += para(ln, sz=sz, after=10, align="left", b=(header or bold), color=("FFFFFF" if header else None), keep_next=keep)
    return f'<w:tc><w:tcPr>{tcpr}</w:tcPr>{ps}</w:tc>'


def table(widths, header, rows, sz=19, first_col_bold=False, first_col_fill=None, keep=False):
    total = sum(widths)
    bd = ''.join(f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="8A96A3"/>'
                 for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
    x = (f'<w:tbl><w:tblPr><w:tblW w:w="{total}" w:type="dxa"/><w:tblBorders>{bd}</w:tblBorders>'
         f'<w:tblLayout w:type="fixed"/><w:tblCellMar><w:top w:w="30" w:type="dxa"/><w:left w:w="70" w:type="dxa"/>'
         f'<w:bottom w:w="30" w:type="dxa"/><w:right w:w="70" w:type="dxa"/></w:tblCellMar></w:tblPr>')
    x += '<w:tblGrid>' + ''.join(f'<w:gridCol w:w="{w}"/>' for w in widths) + '</w:tblGrid>'
    if header:
        x += '<w:tr><w:trPr><w:cantSplit/><w:tblHeader/></w:trPr>' + ''.join(
            _cell(h, w, sz, header=True) for h, w in zip(header, widths)) + '</w:tr>'
    for ri, r in enumerate(rows):
        x += '<w:tr><w:trPr><w:cantSplit/></w:trPr>'
        kp = keep and ri < len(rows) - 1
        for k, (c, w) in enumerate(zip(r, widths)):
            x += _cell(c, w, sz, bold=(first_col_bold and k == 0), fill=(first_col_fill if k == 0 else None), keep=kp)
        x += '</w:tr>'
    x += '</w:tbl>' + para("", sz=8, after=60)
    return x
