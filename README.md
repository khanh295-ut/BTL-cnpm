# BTL-cnpm
# Cấu trúc thư mục dự án

```
AITasker
│
├── frontend/                  # ReactJS Client
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── routes/
│   │   └── assets/
│   ├── package.json
│   └── vite.config.js
│
├── backend/                   # NodeJS + Express API
│   ├── src/
│   │   ├── config/
│   │   ├── controllers/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── middlewares/
│   │   ├── routes/
│   │   ├── models/
│   │   ├── utils/
│   │   └── app.py
│   │
│   ├── prisma/
│   │   └── schema.prisma
│   │
│   ├── .env
│   └── package.json
│
├── database/                  # Cơ sở dữ liệu
│   ├── schema.sql
│   ├── seed.sql
│   └── erd.png
│
├── docs/                      # Tài liệu thiết kế
│   ├── Usecase.png
│   ├── Class.png
│   ├── ERD.png
│   ├── Architecture.png
│   │
│   ├── Activity/
│   │   ├── activity1.png
│   │   ├── activity2.png
│   │   ├── activity3.png
│   │   ├── activity4.png
│   │   ├── activity5.png
│   │   └── activity6.png
│   │
│   └── Sequence/
│       ├── sequence1.png
│       ├── sequence2.png
│       ├── sequence3.png
│       ├── sequence4.png
│       ├── sequence5.png
│       └── sequence6.png
│
├── Latex/                     # Báo cáo LaTeX
│   ├── chapters/
│   │   ├── chapter1.tex
│   │   ├── chapter2.tex
│   │   ├── chapter3.tex
│   │   ├── chapter4.tex
│   │   ├── chapter5.tex
│   │   └── chapter6.tex
│   │
│   ├── figures/
│   ├── references.bib
│   ├── main.tex
│   └── main.pdf
│
├── .gitignore
├── README.md
└── LICENSE
```
Phân công công việc
Thành viên	Công việc
Hoàng Quốc Khánh	Thiết kế PostgreSQL Database
Hoàng Quốc Khánh	Xây dựng ERD
Hoàng Quốc Khánh	Use Case Diagram
Hoàng Quốc Khánh	Activity Diagram
Hoàng Quốc Khánh	Sequence Diagram
Hoàng Quốc Khánh	Class Diagram
Hoàng Quốc Khánh	Architecture Diagram
Hoàng Quốc Khánh	Báo cáo LaTeX (Chương 1,2,3)
