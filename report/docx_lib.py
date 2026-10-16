"""
Thư viện nhỏ dựng báo cáo .docx: công thức OMML (soạn từ cú pháp giống LaTeX), đoạn văn, bảng, hình, chú thích.
Công thức là đối tượng Word (OMML) chỉnh sửa được, không phải ảnh.
"""

import os
import re
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt, RGBColor

M = 'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"'
W = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
FONT = "Times New Roman"

GREEK = {"alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε", "theta": "θ", "lambda": "λ", "mu": "μ",
         "sigma": "σ", "tau": "τ", "phi": "φ", "omega": "ω", "Delta": "Δ", "Sigma": "Σ", "Theta": "Θ", "eta": "η",
         "rho": "ρ", "pi": "π", "varphi": "φ", "nu": "ν", "lVert": "‖", "rVert": "‖", "cdots": "⋯", "kappa": "κ", "nabla": "∇", "partial": "∂"}
SYM = {"cdot": "·", "odot": "⊙", "times": "×", "leq": "≤", "geq": "≥", "neq": "≠", "approx": "≈", "in": "∈", "to": "→",
       "rightarrow": "→", "leftarrow": "←", "mid": "|", "oplus": "⊕", "infty": "∞", "pm": "±", "cup": "∪", "subseteq": "⊆",
       "forall": "∀", "ldots": "…", "top": "⊤", "circ": "∘", "sim": "∼", "propto": "∝", "wedge": "∧", "emptyset": "∅", "ell": "ℓ"}
BIG = {"sum": "∑", "prod": "∏"}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _run(text, sty=None):
    """sty: None (italic mặc định), 'p' (đứng), 'b' (đậm đứng), 'bi' (đậm nghiêng)."""
    rpr = f'<m:rPr><m:scr m:val="script"/><m:sty m:val="p"/></m:rPr>' if sty == "scr" else (
        f'<m:rPr><m:sty m:val="{sty}"/></m:rPr>' if sty else "")
    return (f'<m:r>{rpr}<w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr>'
            f'<m:t xml:space="preserve">{esc(text)}</m:t></m:r>')


class _P:
    """Bộ phân tích cú pháp con của LaTeX -> OMML."""

    def __init__(self, s):
        self.s, self.i = s, 0

    def eof(self):
        return self.i >= len(self.s)

    def group(self):
        """Đọc {...} hoặc một ký tự đơn."""
        while not self.eof() and self.s[self.i] == " ":
            self.i += 1
        if self.s[self.i] == "{":
            depth, j = 1, self.i + 1
            while depth:
                depth += {"{": 1, "}": -1}.get(self.s[j], 0)
                j += 1
            inner = self.s[self.i + 1:j - 1]
            self.i = j
            return _P(inner).parse()
        return self.atom()

    def raw_group(self):
        while self.s[self.i] == " ":
            self.i += 1
        depth, j = 1, self.i + 1
        while depth:
            depth += {"{": 1, "}": -1}.get(self.s[j], 0)
            j += 1
        inner = self.s[self.i + 1:j - 1]
        self.i = j
        return inner

    def atom(self, sty=None):
        c = self.s[self.i]
        if c == "\\":
            m = re.match(r"\\([A-Za-z]+|.)", self.s[self.i:])
            name = m.group(1)
            self.i += len(m.group(0))
            if name in GREEK:
                return _run(GREEK[name], sty)
            if name in SYM:
                return _run(SYM[name], "p")
            if name in BIG:
                return ("BIG", BIG[name])
            if name in ("big", "Big", "bigl", "bigr", "Bigl", "Bigr"):
                return ""
            if name == "mathbb":
                g = self.raw_group()
                return _run({"R": "ℝ", "N": "ℕ", "1": "𝟙"}.get(g, g), "p")
            if name == "qquad":
                return _run("    ", "p")
            if name in ("frac", "tfrac"):
                a, b = self.group(), self.group()
                return f"<m:f><m:num>{a}</m:num><m:den>{b}</m:den></m:f>"
            if name == "sqrt":
                a = self.group()
                return f'<m:rad><m:radPr><m:degHide m:val="1"/></m:radPr><m:deg/><m:e>{a}</m:e></m:rad>'
            if name in ("mathbf", "boldsymbol"):
                return _P(self.raw_group()).parse(sty="b")
            if name == "mathrm" or name == "text":
                return _P(self.raw_group()).parse(sty="p")
            if name == "mathcal":
                return _P(self.raw_group()).parse(sty="scr")
            if name == "hat":
                return f'<m:acc><m:accPr><m:chr m:val="̂"/></m:accPr><m:e>{self.group()}</m:e></m:acc>'
            if name == "tilde":
                return f'<m:acc><m:accPr><m:chr m:val="̃"/></m:accPr><m:e>{self.group()}</m:e></m:acc>'
            if name == "bar":
                return f'<m:bar><m:barPr><m:pos m:val="top"/></m:barPr><m:e>{self.group()}</m:e></m:bar>'
            if name == "argmax":
                return ("LIM", "argmax")
            if name == "cases":
                rows = self.raw_group().split("\\\\")
                es = "".join(f"<m:e>{_P(r.strip()).parse()}</m:e>" for r in rows)
                return (f'<m:d><m:dPr><m:begChr m:val="{{"/><m:endChr m:val=""/></m:dPr><m:e><m:eqArr>{es}</m:eqArr></m:e></m:d>')
            if name == "left":
                op = self.s[self.i]
                self.i += 1
                depth, j = 1, self.i
                while depth:
                    if self.s.startswith("\\left", j):
                        depth += 1
                        j += 5
                    elif self.s.startswith("\\right", j):
                        depth -= 1
                        j += 6
                    else:
                        j += 1
                body = self.s[self.i:j - 6]
                cl = self.s[j]
                self.i = j + 1
                om = {".": "", "\\{": "{", "\\|": "‖"}.get(op, op)
                cm = {".": "", "\\}": "}", "\\|": "‖"}.get(cl, cl)
                if cl == "\\":
                    cm = {"}": "}"}.get(self.s[j + 1], self.s[j + 1])
                    self.i = j + 2
                if op == "\\":
                    om = "{"
                    self.i = self.i  # đã dịch
                return (f'<m:d><m:dPr><m:begChr m:val="{om}"/><m:endChr m:val="{cm}"/></m:dPr>'
                        f'<m:e>{_P(body).parse()}</m:e></m:d>')
            if name == ",":
                return _run(" ", "p")
            if name in ("{", "}", "|", "%", "_"):
                return _run(name, "p")
            if name == "quad":
                return _run("  ", "p")
            return _run(name, "p")
        self.i += 1
        if c.isdigit() or c in "+-=<>()[]|,.;:!/*'%":
            return _run(c, "p" if not (sty in ("b",)) else "b")
        if c == "−":
            return _run(c, "p")
        return _run(c, sty)

    def parse(self, sty=None):
        out = []
        while not self.eof():
            c = self.s[self.i]
            if c == " ":
                self.i += 1
                if sty == "p" and out and not (self.eof()):
                    out.append(_run(" ", "p"))
                continue
            if c in "_^":
                self.i += 1
                arg = self.group()
                # gắn vào phần tử trước
                prev = out.pop() if out else _run("")
                if isinstance(prev, tuple) and prev[0] in ("BIG", "LIM"):
                    out.append(("NARY", prev, c, arg))
                    continue
                if isinstance(prev, tuple) and prev[0] == "NARY":
                    kind, big, c0, arg0 = prev
                    sub, sup = (arg0, arg) if c0 == "_" else (arg, arg0)
                    out.append(("NARY2", big, sub, sup))
                    continue
                if c == "_":
                    # nhìn trước ^ để tạo sSubSup
                    j = self.i
                    while j < len(self.s) and self.s[j] == " ":
                        j += 1
                    if j < len(self.s) and self.s[j] == "^":
                        self.i = j + 1
                        sup = self.group()
                        out.append(f"<m:sSubSup><m:e>{prev}</m:e><m:sub>{arg}</m:sub><m:sup>{sup}</m:sup></m:sSubSup>")
                        continue
                    out.append(f"<m:sSub><m:e>{prev}</m:e><m:sub>{arg}</m:sub></m:sSub>")
                else:
                    out.append(f"<m:sSup><m:e>{prev}</m:e><m:sup>{arg}</m:sup></m:sSup>")
                continue
            if c == "(" and False:
                pass
            # chuỗi chữ cái liên tiếp đứng (chỉ khi sty p/b), còn lại từng ký tự
            el = self.atom(sty)
            if el != "":
                out.append(el)
        # gom NARY: phần tử theo sau là biểu thức thân
        res, k = [], 0
        while k < len(out):
            el = out[k]
            if isinstance(el, tuple) and el[0] in ("NARY", "NARY2", "BIG", "LIM"):
                if el[0] == "NARY":
                    _, big, c0, arg0 = el
                    sub, sup = (arg0, "") if c0 == "_" else ("", arg0)
                elif el[0] == "NARY2":
                    _, big, sub, sup = el
                else:
                    big, sub, sup = el, "", ""
                body = out[k + 1] if k + 1 < len(out) else ""
                if isinstance(body, tuple):
                    body = ""
                    k -= 0
                else:
                    k += 1
                if big[0] == "LIM":
                    res.append(f'<m:limLow><m:e>{_run("arg max", "p")}</m:e><m:lim>{sub}</m:lim></m:limLow>')
                    if body:
                        res.append(body)
                else:
                    sh = ("" if sub else '<m:subHide m:val="1"/>') + ("" if sup else '<m:supHide m:val="1"/>')
                    res.append(f'<m:nary><m:naryPr><m:chr m:val="{big[1]}"/><m:limLoc m:val="undOvr"/>{sh}</m:naryPr>'
                               f'<m:sub>{sub}</m:sub><m:sup>{sup}</m:sup><m:e>{body}</m:e></m:nary>')
            else:
                res.append(el)
            k += 1
        return "".join(x for x in res if isinstance(x, str))


def omml(latex):
    return _P(latex).parse()


def omath_xml(latex):
    return f'<m:oMath {M} {W}>{omml(latex)}</m:oMath>'


def omathpara_xml(latex):
    return f'<m:oMathPara {M} {W}><m:oMath>{omml(latex)}</m:oMath></m:oMathPara>'


# ---------------------------------------------------------------------------
# Tài liệu
# ---------------------------------------------------------------------------

def set_font(run, size=13, bold=None, italic=None, name=FONT, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = parse_xml(f"<w:rFonts {nsdecls('w')}/>")
        rpr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(a), name)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)


class Report:
    def __init__(self, base_path):
        self.doc = Document(base_path)
        self.eq_no = {}      # chương -> số công thức
        self.fig_no = {}
        self.tab_no = {}
        self.chap = 0
        self.refs = {}       # nhãn -> số
        self.labels = {}     # nhãn công thức/hình/bảng -> chuỗi số
        self.bookmark_id = 100

    # --- đoạn văn ---------------------------------------------------------
    def _fmt(self, p, align=None, indent=True, before=0, after=6, line=1.15, left=None, keep_next=False):
        pf = p.paragraph_format
        pf.space_before, pf.space_after, pf.line_spacing = Pt(before), Pt(after), line
        if align is not None:
            p.alignment = align
        if indent:
            pf.first_line_indent = Cm(1.0)
        if left is not None:
            pf.left_indent = Cm(left)
        if keep_next:
            pf.keep_with_next = True

    def _fill(self, p, text, size=13, bold=False, italic=False):
        """text hỗ trợ: $công thức$, **đậm**, _nghiêng_ (chỉ khi bao bằng __)."""
        bold_on = False
        for part in re.split(r"(\$[^$]+\$|\*\*)", text):
            if not part:
                continue
            if part == "**":
                bold_on = not bold_on
            elif part.startswith("$") and part.endswith("$") and len(part) > 2:
                p._p.append(parse_xml(omath_xml(part[1:-1])))
            else:
                set_font(p.add_run(part), size, bold or bold_on, italic)
        return p

    def para(self, text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=True, size=13, bold=False, italic=False, after=6, left=None):
        p = self.doc.add_paragraph()
        self._fmt(p, align, indent, after=after, left=left)
        self._fill(p, text, size, bold, italic)
        return p

    def where(self, items):
        """Chú thích các thành phần của công thức vừa nêu: items là danh sách chuỗi '$ký hiệu$: ý nghĩa'."""
        p = self.doc.add_paragraph()
        self._fmt(p, WD_ALIGN_PARAGRAPH.LEFT, indent=False, after=2, keep_next=True)
        set_font(p.add_run("Trong đó:"), 13, False, True)
        for it in items:
            self.bullet(it)

    def bullet(self, text, level=0):
        p = self.doc.add_paragraph()
        self._fmt(p, WD_ALIGN_PARAGRAPH.JUSTIFY, indent=False, after=3, left=1.0 + 0.6 * level)
        p.paragraph_format.first_line_indent = Cm(-0.5)
        self._fill(p, "–  " + text)
        return p

    def heading(self, text, level):
        h = self.doc.add_paragraph(style=f"Heading {level}")
        sizes = {1: 16, 2: 14, 3: 13, 4: 13}
        h.paragraph_format.space_before = Pt(14 if level <= 2 else 10)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
        if level == 1:
            h.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = h.add_run(text)
        set_font(r, sizes[level], True, level == 4, color=(0, 0, 0))
        return h

    def page_break(self):
        self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # --- đánh số ----------------------------------------------------------
    def new_chapter(self, n):
        self.chap = n

    def next_no(self, kind, label=None):
        d = {"eq": self.eq_no, "fig": self.fig_no, "tab": self.tab_no}[kind]
        d[self.chap] = d.get(self.chap, 0) + 1
        s = f"{self.chap}.{d[self.chap]}"
        if label:
            self.labels[label] = s
        return s

    def ref(self, label):
        return self.labels.get(label, "0.0")

    # --- công thức --------------------------------------------------------
    def equation(self, latex, label=None):
        no = self.next_no("eq", label)
        t = self.doc.add_table(rows=1, cols=3)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        widths = (Cm(1.2), Cm(13.1), Cm(1.7))
        for c, w in zip(t.rows[0].cells, widths):
            c.width = w
        mid = t.rows[0].cells[1].paragraphs[0]
        mid.alignment = WD_ALIGN_PARAGRAPH.CENTER
        mid.paragraph_format.space_after = Pt(0)
        mid._p.append(parse_xml(omathpara_xml(latex)))
        rp = t.rows[0].cells[2].paragraphs[0]
        rp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        rp.paragraph_format.space_after = Pt(0)
        set_font(rp.add_run(f"({no})"), 13)
        for c in t.rows[0].cells:
            c.vertical_alignment = 1
        self._spacer(2)
        return no

    def _spacer(self, pt):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.line_spacing = Pt(pt)

    # --- hình, bảng ------------------------------------------------------------
    def figure(self, path, caption, width_cm=15.5, label=None):
        no = self.next_no("fig", label)
        if not os.path.isabs(path):
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
        p = self.doc.add_paragraph()
        self._fmt(p, WD_ALIGN_PARAGRAPH.CENTER, indent=False, before=4, after=2, keep_next=True)
        p.add_run().add_picture(path, width=Cm(width_cm))
        c = self.doc.add_paragraph()
        self._fmt(c, WD_ALIGN_PARAGRAPH.CENTER, indent=False, after=8)
        set_font(c.add_run(f"Hình {no}. "), 12, True)
        self._fill(c, caption, 12, False, False)
        return no

    def table(self, header, rows, caption, widths=None, size=11, label=None, align_first_left=True, bold_rows=()):
        no = self.next_no("tab", label)
        c = self.doc.add_paragraph()
        self._fmt(c, WD_ALIGN_PARAGRAPH.CENTER, indent=False, before=6, after=3, keep_next=True)
        set_font(c.add_run(f"Bảng {no}. "), 12, True)
        self._fill(c, caption, 12)
        t = self.doc.add_table(rows=1 + len(rows), cols=len(header))
        bd = "".join(f'<w:{e} w:val="single" w:sz="4" w:space="0" w:color="808080"/>' for e in ("top", "left", "bottom", "right", "insideH", "insideV"))
        t._tbl.tblPr.append(parse_xml(f'<w:tblBorders {nsdecls("w")}>{bd}</w:tblBorders>'))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        for ri, row in enumerate([header] + rows):
            for ci, val in enumerate(row):
                cell = t.rows[ri].cells[ci]
                if widths:
                    cell.width = Cm(widths[ci])
                p = cell.paragraphs[0]
                p.paragraph_format.space_after = Pt(1)
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.line_spacing = 1.0
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT if (ci == 0 and align_first_left) or isinstance(val, str) and len(val) > 28 else WD_ALIGN_PARAGRAPH.CENTER
                self._fill(p, str(val), size, bold=(ri == 0 or ri - 1 in bold_rows))
                if ri == 0:
                    tcPr = cell._tc.get_or_add_tcPr()
                    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="D9E2F3"/>'))
        if len(rows) > 0:
            trPr = t.rows[0]._tr.get_or_add_trPr()
            trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
        self._spacer(6)
        return no

    def code(self, text, size=10):
        for line in text.split("\n"):
            p = self.doc.add_paragraph()
            self._fmt(p, WD_ALIGN_PARAGRAPH.LEFT, indent=False, after=0, line=1.0, left=0.8)
            set_font(p.add_run(line), size, name="Consolas")
        self._spacer(6)
