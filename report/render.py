"""Xuất .docx -> PDF bằng Word COM rồi PNG các trang chọn: python report/render.py file.docx [trang,trang...]"""
import os
import subprocess
import sys

import fitz

src = os.path.abspath(sys.argv[1])
pdf = os.path.splitext(src)[0] + ".pdf"
ps = ("$w=New-Object -ComObject Word.Application;$w.Visible=$false;"
      f"$d=$w.Documents.Open('{src}');$d.ExportAsFixedFormat('{pdf}',17);$d.Close(0);$w.Quit()")
subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
d = fitz.open(pdf)
print("pages", len(d))
if len(sys.argv) > 2:
    for p in sys.argv[2].split(","):
        out = os.path.join(os.path.dirname(src), f"_pg{int(p)}.png")
        d[int(p) - 1].get_pixmap(dpi=75).save(out)
        print(out)
