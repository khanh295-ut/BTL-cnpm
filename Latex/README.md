# Báo cáo đồ án CNPM - AIConnect

## Cấu trúc thư mục
```
Bao cao cnpm/
├── main.tex              <- File chính, compile file này
├── references.bib        <- Tài liệu tham khảo
├── chapters/
│   ├── cover.tex         <- Trang bìa
│   ├── chapter1.tex      <- Chương 1: Giới thiệu
│   ├── chapter2.tex      <- Chương 2: Phân tích yêu cầu
│   ├── chapter3.tex      <- Chương 3: Thiết kế
│   ├── chapter4.tex      <- Chương 4: Cài đặt
│   ├── chapter5.tex      <- Chương 5: Kiểm thử
│   └── chapter6.tex      <- Chương 6: Kết luận
├── figures/              <- Đặt hình ảnh .png/.jpg vào đây
└── appendix/
    └── appendix_a.tex    <- Phụ lục A
```

## Hướng dẫn sử dụng

### Compile
- Mở VS Code, nhấn Ctrl+Alt+B
- Hoặc chạy: xelatex main.tex

### Chỉnh sửa thông tin cá nhân
1. Mở `chapters/cover.tex`
2. Thay tên thành viên và MSSV thực tế
3. Thay tên lớp học

### Thêm hình ảnh
- Đặt file .png/.jpg vào thư mục `figures/`
- Trong .tex dùng: \includegraphics[width=0.8\textwidth]{figures/ten_file.png}

### Tắt cảnh báo cSpell tiếng Việt
Nhấn Ctrl+Shift+P -> "cSpell: Disable for workspace"
