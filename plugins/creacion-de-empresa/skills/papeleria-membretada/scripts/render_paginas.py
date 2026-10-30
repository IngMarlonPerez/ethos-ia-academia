import sys, pymupdf
pdf, prefix = sys.argv[1], sys.argv[2]
doc = pymupdf.open(pdf)
for i, p in enumerate(doc):
    p.get_pixmap(dpi=int(sys.argv[3]) if len(sys.argv)>3 else 90).save(f"{prefix}-{i+1}.png")
print(len(doc), "pages")
