"""
Mô hình GNN mức yêu cầu (HeteroConv + GATv2) với bước tổng hợp coverage:
  điểm khớp từng cạnh (req,item) -> với mỗi yêu cầu lấy MAX trên các mục CV khớp -> cộng có trọng số bằng attention
  (softmax theo từng đồ thị, thay λ_t đặt tay) -> trừ phạt đơn điệu theo khoảng thiếu về cấp độ/số năm (chỉ khi CV thấp hơn JD).
Cờ ablation/biến thể: skip (đường tắt cosine), agg ('max'|'mean'), attn (False = trọng số đều), spec (False = bỏ nút cấp độ/số năm).
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GATv2Conv, HeteroConv
from torch_geometric.utils import scatter, softmax


def mlp(i, h, o):
    return nn.Sequential(nn.Linear(i, h), nn.ReLU(), nn.Dropout(0.1), nn.Linear(h, o))


class ReqGNN(nn.Module):
    def __init__(self, dims, hidden=64, layers=2, agg="max", attn=True, spec=True, skip=False, ctx=(), spec_feat=False, use_req=True):
        """ctx: nhóm cạnh ngữ cảnh thêm vào truyền tin: 'doc' (yêu cầu–yêu cầu, mục–mục), 'any' (khớp khác loại), 'spec' (cấp độ/số năm → nút).
        spec_feat: đối chứng KHÔNG truyền tin cho 'spec': nối thẳng đặc trưng cấp độ/số năm của JD vào mỗi yêu cầu, của CV vào mỗi mục."""
        super().__init__()
        self.agg, self.attn, self.spec, self.skip, self.H, self.spec_feat, self.use_req = agg, attn, spec, skip, hidden, spec_feat, use_req
        if spec_feat:
            dims = {**dims, "req": dims["req"] + 2 * dims["spec"], "item": dims["item"] + 2 * dims["spec"]}
        self.proj = nn.ModuleDict({k: nn.Sequential(nn.Linear(d, hidden), nn.LayerNorm(hidden), nn.ReLU()) for k, d in dims.items()})
        g = lambda e: GATv2Conv(hidden, hidden, heads=2, concat=False, edge_dim=e, add_self_loops=False)
        rels = [("req", "match", "item"), ("item", "rev_match", "req")]
        groups = {"doc": [("req", "ctx", "req"), ("item", "ctx", "item")], "any": [("req", "any", "item"), ("item", "rev_any", "req")],
                  "spec": [("spec", "jd_ctx", "req"), ("spec", "cv_ctx", "item")]}
        rels += [r for c in ctx for r in groups[c]]
        self.convs = nn.ModuleList([HeteroConv({**{r: g(1) for r in rels}, ("spec", "cmp", "spec"): g(2)}, aggr="sum") for _ in range(layers)])
        self.edge_mlp = mlp(3 * hidden + 1, hidden, 1)
        self.w_mlp = mlp(hidden + 1, hidden, 1)          # +1: cờ bắt buộc/ưu tiên
        if skip:                                           # đường tắt cosine: bắt đầu từ MaxSim, MLP chỉ hiệu chỉnh
            nn.init.zeros_(self.edge_mlp[-1].weight), nn.init.zeros_(self.edge_mlp[-1].bias)
            self.sc, self.c0 = nn.Parameter(torch.tensor(10.0)), nn.Parameter(torch.tensor(0.5))
        self.pen_w = nn.Parameter(torch.zeros(2))         # trọng số phạt (cấp độ, số năm) >= 0 qua softplus
        self.k = nn.Parameter(torch.tensor(6.0))
        self.b = nn.Parameter(torch.tensor(-3.0))

    def forward(self, d):
        x = {k: d[k].x for k in self.proj}
        if not self.use_req:                              # ablation: bỏ phân biệt bắt buộc/ưu tiên (coi mọi yêu cầu như nhau)
            x["req"] = x["req"].clone()
            x["req"][:, -2] = 0.0
        if self.spec_feat:                                # 4 nút spec mỗi đồ thị theo thứ tự (cấp JD, cấp CV, năm JD, năm CV)
            sp = d["spec"].x.view(-1, 4, d["spec"].x.size(1))
            x["req"] = torch.cat([x["req"], sp[:, [0, 2]].flatten(1)[d["req"].batch]], 1)
            x["item"] = torch.cat([x["item"], sp[:, [1, 3]].flatten(1)[d["item"].batch]], 1)
        h = {k: self.proj[k](x[k]) for k in self.proj}
        for conv in self.convs:
            o = conv(h, {t: d[t].edge_index for t in d.edge_types}, edge_attr_dict={t: d[t].edge_attr for t in d.edge_types})
            h = {k: F.relu(o[k]) + h[k] if k in o else h[k] for k in h}
        ei, cos = d["req", "match", "item"].edge_index, d["req", "match", "item"].edge_attr
        s = self.edge_mlp(torch.cat([h["req"][ei[0]], h["item"][ei[1]], h["req"][ei[0]] * h["item"][ei[1]], cos], 1)).squeeze(-1)
        if self.skip:
            s = s + self.sc * (cos.squeeze(-1) - self.c0)
        n = h["req"].size(0)
        c = scatter(s, ei[0], 0, dim_size=n, reduce="max" if self.agg == "max" else "mean")
        c = torch.where(torch.bincount(ei[0], minlength=n) > 0, c, torch.full_like(c, -4.0))  # yêu cầu không có mục cùng loại
        req_batch = d["req"].batch
        flag = d["req"].x[:, -2:-1] * float(self.use_req)  # cột 'required' (sau one-hot loại, trước years)
        w = softmax(self.w_mlp(torch.cat([h["req"], flag], 1)).squeeze(-1), req_batch) if self.attn else \
            1.0 / torch.bincount(req_batch)[req_batch].float()
        self.last = (w, c, s)                             # để diễn giải: trọng số, độ phủ (logit), điểm từng cạnh khớp
        cov = scatter(w * torch.sigmoid(c), req_batch, 0, dim_size=int(req_batch.max()) + 1, reduce="sum")
        out = self.k * cov + self.b
        if self.spec:
            gap = d["spec", "cmp", "spec"].edge_attr[:, 1].view(-1, 2)   # max(0, JD − CV): chỉ phạt khi CV thấp hơn JD
            out = out - (F.softplus(self.pen_w) * gap).sum(1)
        return out
