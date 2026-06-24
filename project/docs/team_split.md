# Phân chia công việc — Nhóm 3 người

Mục tiêu: reproduce paper Nagatani 2006 + viết slide + báo cáo.

## Vai trò

| Thành viên | Mảng phụ trách | File chính |
|---|---|---|
| **Người A — Simulator** | Cài đặt và kiểm thử non-linear map; tự tin demo lại từ đầu trên bảng | `src/nagatani/simulation.py`, `tests/test_simulation.py`, `docs/derivation.md` |
| **Người B — Phân tích & phase diagram** | Mean/RMS, transition detection, Fig. 6/7/8 | `src/nagatani/analysis.py`, `experiments/fig6_*`, `experiments/fig7_*`, `experiments/fig8_*` |
| **Người C — Reproduction & viết** | Fig. 2/3/4/5, notebook, tổng hợp slide & báo cáo | `experiments/fig2_*` … `fig5_*`, `notebooks/reproduction.ipynb`, slide báo cáo |

## Mốc thời gian gợi ý

| Tuần | Việc |
|---|---|
| 1 | A xong simulator + test; B/C chạy được trên máy mình; mọi người đọc paper kỹ |
| 2 | A xong derivation, B xong fig6+7, C xong fig2+3 |
| 3 | B xong fig8 (phase diagram), C xong fig4+5 + notebook |
| 4 | Tổng hợp: viết báo cáo (10 trang), làm slide (~15 trang), dry-run thuyết trình |

## Định nghĩa "DONE"

Mỗi figure được coi là xong khi:
1. Script `experiments/figN_*.py` chạy được, output PNG vào `results/`.
2. Hình giống paper về định tính (so sánh side-by-side trong báo cáo).
3. Có 1 đoạn ~150 từ giải thích quan sát.

## Báo cáo

Cấu trúc đề xuất:
1. Tóm tắt paper (1 trang)
2. Mô hình toán + dẫn xuất Eq. 5 (2 trang) — **Người A**
3. Phương pháp simulation (event-driven heap) (1 trang) — **Người A**
4. Reproduction Fig. 2–5 (2 trang) — **Người C**
5. Reproduction Fig. 6–7 (1 trang) — **Người B**
6. Phase diagram Fig. 8 + thảo luận (1 trang) — **Người B**
7. Kết luận, hạn chế, hướng mở rộng (1 trang) — cả nhóm
