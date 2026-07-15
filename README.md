# AITasker SRS LaTeX Package

## Biên dịch

Dùng XeLaTeX:

```bash
xelatex main.tex
xelatex main.tex
```

Hoặc:

```bash
latexmk -xelatex main.tex
```

## Cấu trúc

- `main.tex`: file chính.
- `chapters/`: Chapter 1 đến Chapter 6.
- `figures/`: toàn bộ sơ đồ và logo.

## Lưu ý

Chapter 6 chứa bảng kết quả kiểm thử mẫu. Trước khi nộp, hãy thay PASS/FAIL và số liệu bằng kết quả chạy thực tế.
