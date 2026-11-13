"""
Sinh 3 hình draw.io cho PHƯƠNG PHÁP MỚI (đồ thị mức yêu cầu), sửa theo các bảng nhận xét của cô (Hình 1.1, 2.1, 2.4):
  report/figures/v2_hinh_1_1_cv_jd_pipeline.drawio, v2_hinh_2_1_kien_truc.drawio, v2_hinh_2_4_huan_luyen.drawio
Mở bằng draw.io, File -> Export as -> PNG (300 dpi, bỏ chọn "Include a copy of my diagram") vào report/figures/<cùng tên>.png.
Thông số trong hình lấy đúng từ code: src/modeling/train_req.py (run, pair_loss), src/modeling/req_model.py, src/representation/req_graph.py.
Chạy: python report/figures_drawio.py
"""
import os
from xml.sax.saxutils import escape

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
FONT = "fontFamily=Times New Roman;"
C = {"io": ("#F2F2F2", "#7F7F7F"), "prep": ("#DAE8FC", "#6C8EBF"), "graph": ("#E1D5E7", "#9673A6"), "score": ("#D5E8D4", "#82B366"),
     "level": ("#FFE6CC", "#D79B00"), "rank": ("#F8CECC", "#B85450"), "label": ("#FFF2CC", "#D6B656")}


class D:
    def __init__(self, name, w, h):
        self.name, self.w, self.h, self.cells, self.n = name, w, h, [], 0

    def _id(self):
        self.n += 1
        return f"c{self.n}"

    def box(self, x, y, w, h, title, body="", kind="prep", dashed=False, size=13, shape="rounded=1;arcSize=8;"):
        f, s = C[kind]
        v = f"<b>{escape(title)}</b>" + (f"<br>{body}" if body else "")
        st = f"{shape}whiteSpace=wrap;html=1;fillColor={f};strokeColor={s};strokeWidth=1.5;{FONT}fontSize={size};" + ("dashed=1;" if dashed else "")
        return self._v(v, st, x, y, w, h)

    def diamond(self, x, y, w, h, title, body="", kind="label"):
        return self.box(x, y, w, h, title, body, kind, shape="rhombus;")

    def frame(self, x, y, w, h, title="", color="#777777", align="center"):
        st = f"rounded=1;arcSize=3;dashed=1;fillColor=none;strokeColor={color};strokeWidth=1.5;verticalAlign=top;align={align};html=1;{FONT}fontSize=14;spacingTop=6;spacingRight=10;fontColor={color};"
        return self._v(f"<b>{escape(title)}</b>" if title else "", st, x, y, w, h)

    def text(self, x, y, w, h, t, size=12, italic=True, align="center", color="#333333"):
        st = f"text;html=1;align={align};verticalAlign=middle;{FONT}fontSize={size};fontColor={color};" + ("fontStyle=2;" if italic else "")
        return self._v(t, st, x, y, w, h)

    def _v(self, v, st, x, y, w, h):
        i = self._id()
        self.cells.append(f'<mxCell id="{i}" value="{escape(v, {chr(34): "&quot;"})}" style="{st}" vertex="1" parent="1">'
                          f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return i

    def edge(self, a, b, label="", dashed=False, pts=(), ex=None, ey=None, nx=None, ny=None):
        i = self._id()
        st = f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;endFill=1;strokeColor=#333333;strokeWidth=1.5;{FONT}fontSize=12;fontStyle=2;labelBackgroundColor=#FFFFFF;"
        st += "dashed=1;" if dashed else ""
        for k, v in (("exitX", ex), ("exitY", ey), ("entryX", nx), ("entryY", ny)):
            if v is not None:
                st += f"{k}={v};"
        geo = '<mxGeometry relative="1" as="geometry">' + (
            "<Array as=\"points\">" + "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in pts) + "</Array>" if pts else "") + "</mxGeometry>"
        self.cells.append(f'<mxCell id="{i}" value="{escape(label)}" style="{st}" edge="1" parent="1" source="{a}" target="{b}">{geo}</mxCell>')

    def legend(self, y, items, x0=20, step=None):
        self.text(x0, y, 110, 30, "<b>Chú giải màu:</b>", 13, italic=False, align="left", color="#000000")
        step = step or (self.w - 150) // len(items)
        for k, (kind, t) in enumerate(items):
            x = x0 + 120 + k * step
            f, s = C[kind]
            self._v("", f"rounded=1;html=1;fillColor={f};strokeColor={s};strokeWidth=1.5;" + ("dashed=1;" if kind == "label" else ""), x, y + 5, 22, 20)
            self.text(x + 28, y, step - 32, 30, t, 13, italic=False, align="left", color="#000000")

    def save(self):
        xml = (f'<mxfile host="app.diagrams.net"><diagram name="{self.name}" id="{self.name}"><mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" '
               f'guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{self.w}" pageHeight="{self.h}" math="0" shadow="0">'
               '<root><mxCell id="0"/><mxCell id="1" parent="0"/>' + "".join(self.cells) + "</root></mxGraphModel></diagram></mxfile>")
        p = os.path.join(OUT, self.name + ".drawio")
        open(p, "w", encoding="utf-8").write(xml)
        return p


def hinh_1_1():
    d = D("v2_hinh_1_1_cv_jd_pipeline", 1180, 800)
    d.frame(20, 20, 290, 690, "Đầu vào (Input)")
    d.frame(370, 20, 440, 690, "Xử lý (Process)")
    d.frame(870, 20, 290, 690, "Đầu ra (Output)")
    i1 = d.box(40, 150, 250, 120, "Một JD (j) và tập CV ứng viên (c)", "văn bản tiếng Việt, tiếng Anh<br>hoặc song ngữ; lặp cho mọi cặp (c, j)", "io")
    i2 = d.box(40, 470, 250, 120, "Nhãn mức phù hợp y", "y = 0, 1, 2, 3 (tùy chọn:<br>chỉ dùng khi huấn luyện, đánh giá)", "label", dashed=True)
    X, W, H = 390, 400, 100
    s1 = d.box(X, 65, W, H, "Bước 1. Trích xuất yêu cầu và mục", "JD → yêu cầu (nội dung, loại, bắt buộc/ưu tiên, số năm);<br>CV → mục (nội dung, loại, số năm, cấp độ)", "prep")
    s2 = d.box(X, 190, W, H, "Bước 2. Biểu diễn từng yêu cầu, từng mục", "embedding đa ngữ cho mỗi yêu cầu / mục<br>(chuẩn hóa kỹ năng theo ESCO: tùy chọn)", "prep")
    s3 = d.box(X, 315, W, H, "Bước 3. Đối sánh mức yêu cầu, tính điểm", "đồ thị yêu cầu–mục; độ phủ từng yêu cầu,<br>cộng có trọng số, phạt thiếu cấp độ/số năm → s(c, j)", "score")
    s4 = d.box(X, 440, W, H, "Bước 4. Phân mức, sinh diễn giải", "quy điểm về mức 0–3; yêu cầu đã / chưa đáp ứng<br>và bằng chứng lấy từ chính các cạnh của đồ thị", "level")
    s5 = d.box(X, 565, W, H, "Bước 5. Xếp hạng CV theo từng JD", "gom điểm các cặp cùng một JD,<br>sắp xếp CV theo điểm giảm dần", "rank")
    for a, b in ((s1, s2), (s2, s3), (s3, s4), (s4, s5)):
        d.edge(a, b)
    d.edge(i1, s1, nx=0, ny=0.5)
    d.edge(i2, s3, "huấn luyện", dashed=True, ex=1, ey=0.3, nx=0, ny=0.6)
    d.edge(i2, s4, "chọn ngưỡng, đánh giá", dashed=True, ex=1, ey=0.7, nx=0, ny=0.6)
    o1 = d.box(890, 320, 250, 90, "Điểm phù hợp s(c, j)", "của từng cặp", "score")
    o2 = d.box(890, 425, 250, 70, "Mức phù hợp (0–3)", "của từng cặp", "level")
    o3 = d.box(890, 505, 250, 70, "Lời diễn giải", "yêu cầu đã / chưa đáp ứng, bằng chứng", "level")
    o4 = d.box(890, 590, 250, 80, "Danh sách CV của mỗi JD", "xếp theo điểm giảm dần", "rank")
    d.edge(s3, o1, nx=0, ny=0.5)
    d.edge(s4, o2, ex=1, ey=0.4, nx=0, ny=0.5)
    d.edge(s4, o3, ex=1, ey=0.6, nx=0, ny=0.5)
    d.edge(s5, o4, nx=0, ny=0.5)
    d.legend(730, [("io", "Dữ liệu vào"), ("prep", "Trích xuất, biểu diễn"), ("score", "Tính điểm"), ("level", "Phân mức, diễn giải"),
                   ("rank", "Xếp hạng"), ("label", "Nhãn (tùy chọn)")], step=170)
    return d.save()


def hinh_2_1():
    d = D("v2_hinh_2_1_kien_truc", 1500, 1090)
    W, H = 300, 150
    x = [30, 380, 730, 1080]
    inp = d.box(x[0], 60, W, H, "Văn bản JD j và tập CV {cᵢ}", "lặp cho mọi cặp (cᵢ, j) ở M1–M4;<br>M5–M7 dùng kết quả của các cặp", "io")
    m1 = d.box(x[1], 60, W, H, "M1. Trích xuất (LLM, schema JSON)",
               "JD → yêu cầu: nội dung, loại, bắt buộc/ưu tiên,<br>số năm tối thiểu; CV → mục: nội dung, loại,<br>số năm, cấp độ; cấp độ và tổng số năm; cache", "prep")
    m2 = d.box(x[2], 60, W, H, "M2. Biểu diễn từng yêu cầu / mục",
               "ESCO (tùy chọn, τ = 0,85) → BGE-M3 (1024 chiều)<br>+ one-hot loại, cờ bắt buộc, số năm", "prep")
    m3 = d.box(x[3], 60, W, H, "M3. Đồ thị mức yêu cầu",
               "nút: yêu cầu JD, mục CV, 4 nút cấp độ/số năm;<br>cạnh khớp: yêu cầu → mục cùng loại,<br>top-m = 3 theo cosine (thuộc tính = cosine)", "graph")
    m4 = d.box(x[3], 290, W, 190, "M4. Mô hình chấm điểm",
               "điểm cạnh = MLP(yêu cầu, mục) + đường tắt cosine;<br>độ phủ c_r = max trên cạnh của yêu cầu r;<br>trọng số w_r = attention (theo cờ bắt buộc);<br>s = k·Σ w_r·σ(c_r) + b − phạt thiếu<br>cấp độ / số năm", "score")
    m5 = d.box(x[2], 290, W, H, "M5. Phân mức 0–3", "quy điểm s về mức 0–3<br>theo phân vị trong từng JD", "level")
    m7 = d.box(x[2], 470, W, H + 20, "M7. Diễn giải từ đồ thị",
               "yêu cầu đã đáp ứng (σ(c_r) ≥ 0,5) / chưa;<br>bằng chứng = mục CV của cạnh có điểm<br>cao nhất; mức quan trọng = w_r", "level")
    m6 = d.box(x[1], 290, W, H, "M6. Xếp hạng", "gom các cặp cùng một JD;<br>sắp CV theo s giảm dần", "rank")
    out = d.box(x[0], 470, W, 170, "Đầu ra",
                "điểm s và mức (0–3) của từng cặp;<br>danh sách CV của mỗi JD;<br>lời diễn giải: yêu cầu đã / chưa<br>đáp ứng kèm bằng chứng", "io")
    for a, b in ((inp, m1), (m1, m2), (m2, m3), (m3, m4)):
        d.edge(a, b)
    d.edge(m4, m5, "s", nx=1, ny=0.5, ex=0, ey=0.3)
    d.edge(m4, m7, "w_r, c_r, điểm cạnh", ex=0, ey=0.75, nx=1, ny=0.5)
    d.edge(m5, m6, "s, mức")
    d.edge(m6, out, "danh sách xếp hạng", ex=0.5, ey=1, nx=0.5, ny=0)
    d.edge(m7, out, "lời diễn giải", ex=0, ey=0.6, nx=1, ny=0.6)
    for xx, t in ((x[1], "Bước 1"), (x[2], "Bước 2"), (x[3], "Bước 3")):
        d.text(xx + W - 90, 32, 90, 24, t, 12, color="#666666")
    d.text(x[3] + W - 90, 262, 90, 24, "Bước 3", 12, color="#666666")
    d.text(x[2] + W - 90, 262, 90, 24, "Bước 4", 12, color="#666666")
    d.text(x[2] + W - 90, 442, 90, 24, "Bước 4", 12, color="#666666")
    d.text(x[1] + W - 90, 262, 90, 24, "Bước 5", 12, color="#666666")
    d.frame(20, 700, 1460, 250, "Chỉ dùng khi có nhãn (huấn luyện, chọn mô hình, đánh giá)", align="center")
    y = d.box(40, 770, 250, 130, "Nhãn y", "y = 0, 1, 2, 3<br>(mức phù hợp của cặp)", "label", dashed=True)
    tr = d.box(1110, 770, 340, 130, "Huấn luyện M4", "loss xếp hạng RankNet theo từng JD:<br>cặp (CV tốt hơn, CV kém hơn) cùng JD,<br>trọng số = chênh nhãn; AdamW", "label", dashed=True)
    va = d.box(730, 770, 330, 130, "Validation (15% JD của tập huấn luyện)", "dừng sớm theo val loss;<br>chọn cấu hình theo NDCG@10 validation", "label", dashed=True)
    ev = d.box(350, 770, 330, 130, "Đánh giá (tập kiểm tra, chấm một lần)", "NDCG@5/10, MAP, MRR, Recall@5,<br>Spearman, QWK; paired bootstrap, Holm", "label", dashed=True)
    d.edge(y, ev, dashed=True, ex=0.5, ey=1, nx=0.5, ny=1, pts=((165, 925), (515, 925)))
    d.edge(y, va, dashed=True, ex=0.5, ey=1, nx=0.5, ny=1, pts=((165, 925), (895, 925)))
    d.edge(y, tr, dashed=True, ex=0.5, ey=1, nx=0.5, ny=1, pts=((165, 925), (1280, 925)))
    d.edge(tr, m4, "cập nhật tham số", dashed=True, ex=0.5, ey=0, nx=0.5, ny=1)
    d.edge(out, ev, "điểm, mức, danh sách", dashed=True, ex=0.5, ey=1, nx=0.5, ny=0, pts=((180, 680), (515, 680)))
    d.legend(980, [("io", "Đầu vào / đầu ra"), ("prep", "Trích xuất, biểu diễn"), ("graph", "Dựng đồ thị"), ("score", "Tính điểm"),
                   ("level", "Phân mức, diễn giải"), ("rank", "Xếp hạng"), ("label", "Chỉ dùng khi có nhãn")], step=195)
    return d.save()


def hinh_2_4():
    d = D("v2_hinh_2_4_huan_luyen", 1500, 1170)
    i0 = d.box(30, 20, 360, 110, "Dữ liệu huấn luyện", "đồ thị cặp (CV, JD) và nhãn y; tập huấn luyện<br>tách 85% JD train / 15% JD validation", "io")
    i1 = d.box(460, 20, 480, 110, "Khởi tạo tham số θ",
               "mặc định PyTorch; đường tắt cosine: lớp cuối MLP cạnh = 0,<br>hệ số 10, ngưỡng 0,5 (bắt đầu đúng như MaxSim);<br>phạt cấp độ / số năm: trọng số 0", "io")
    d.edge(i0, i1)
    d.frame(20, 170, 1460, 760, "Vòng epoch: tối đa 80 epoch", align="right")
    d.frame(40, 220, 1420, 290, "Vòng lô: mỗi lô gom mọi cặp của 8 JD", color="#6C8EBF", align="right")
    f = d.box(60, 300, 290, 160, "Lan truyền xuôi", "chiếu nút → điểm từng cạnh khớp<br>→ max theo yêu cầu (c_r)<br>→ attention w_r → điểm s", "prep")
    l = d.box(390, 300, 290, 160, "Hàm mất mát RankNet", "mọi cặp (i, j) cùng JD có y_i > y_j:<br>softplus(−(s_i − s_j)),<br>trọng số y_i − y_j", "level")
    b = d.box(720, 300, 250, 160, "Lan truyền ngược", "tính gradient của L theo θ", "rank")
    u = d.box(1010, 300, 250, 160, "Cập nhật tham số", "AdamW: η = 0,001;<br>weight decay = 0,0001", "score")
    c = d.diamond(1290, 320, 150, 120, "Còn lô?")
    d.edge(i1, f, ex=0.5, ey=1, nx=0.5, ny=0, pts=((700, 150), (205, 150)))
    for a_, b_ in ((f, l), (l, b), (b, u), (u, c)):
        d.edge(a_, b_)
    d.edge(c, f, "Có: lô kế tiếp", ex=0.5, ey=0, nx=0.5, ny=0, pts=((1365, 270), (205, 270)))
    v = d.box(1150, 580, 300, 130, "Đánh giá validation", "val loss (RankNet) trên<br>toàn bộ tập validation", "graph")
    s = d.box(760, 580, 330, 130, "Lưu trạng thái tốt nhất", "nếu val loss giảm hơn 10⁻⁴<br>so với tốt nhất; ngược lại<br>tăng bộ đếm epoch không cải thiện", "graph")
    e = d.diamond(330, 560, 360, 170, "Dừng sớm?", "12 epoch liên tiếp không cải thiện<br>hoặc đã đủ 80 epoch")
    d.edge(c, v, "Không: hết epoch", ex=0.5, ey=1, nx=0.5, ny=0)
    d.edge(v, s)
    d.edge(s, e)
    d.edge(e, f, "Không: epoch kế", ex=0, ey=0.5, nx=0, ny=0.6, pts=((50, 645), (50, 396)))
    o = d.box(330, 980, 360, 120, "Kết thúc huấn luyện", "nạp lại trạng thái tốt nhất → mô hình chấm điểm;<br>NDCG@10 validation để chọn cấu hình", "io")
    d.edge(e, o, "Có: dừng", ex=0.5, ey=1, nx=0.5, ny=0)
    d.text(760, 760, 690, 120, "Ký hiệu: s = điểm phù hợp của cặp (logit, không giới hạn);<br>y = mức phù hợp của cặp (nhãn của bộ dữ liệu); c_r = độ phủ (logit) của yêu cầu r;<br>"
           "w_r = trọng số attention của yêu cầu r (tổng bằng 1 trong mỗi đồ thị).", 13, italic=False, align="left", color="#000000")
    d.legend(1120, [("io", "Dữ liệu / kết quả"), ("prep", "Lan truyền xuôi"), ("level", "Hàm mất mát"), ("rank", "Lan truyền ngược"),
                    ("score", "Cập nhật tham số"), ("graph", "Validation"), ("label", "Điều kiện rẽ nhánh")], step=190)
    return d.save()


if __name__ == "__main__":
    for fn in (hinh_1_1, hinh_2_1, hinh_2_4):
        print(fn())
