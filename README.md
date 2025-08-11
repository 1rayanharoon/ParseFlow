  # 📄 PDF Parser – Modern Web UI  
A lightweight, **drag-and-drop** PDF-to-JSON parser with an elegant, responsive interface and a full **find & replace** JSON editor.

---

## 🚀 Features  
- **Instant Upload** – drag-and-drop or click-to-browse PDFs (≤ 50 MB).  
- **Live Parsing** – powered by ChatDoc API (or built-in mock mode) to extract text, tables, metadata and layout.  
- **Interactive JSON Editor**  
  - Syntax-highlighted view.  
  - **Search & Replace** with ↑/↓ navigation inside the editor.  
  - **Download / Copy** JSON or plain text.  
- **Responsive Design** – works on desktop, tablet & mobile.  
- **Zero-Setup Mock Mode** – works offline for demos or prototyping.

---

## 🏗️ Tech Stack  
| Front-end | Back-end |
|-----------|----------|
| HTML5, CSS3, ES6 | Python 3, Flask |
| Flexbox + CSS Grid | ChatDoc API |
| Vanilla JS (no build step) | `flask-cors`, `python-dotenv` |

---

## ⚙️ Quick Start (Local)

### 1. Clone & install
```bash
git clone (https://github.com/1rayanharoon/ParseFlow.git)
cd pdf-parser-ui
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment
Create `.env` in the **backend** folder:
```
chatdoc_api_key=YOUR_CHATDOC_API_KEY
```

### 3. Run
```bash
python app.py
```
Visit `http://localhost:8000` and drop a PDF.

---

## 🧪 Mock Mode (No API Key)
Set `USE_MOCK = true` in the front-end script to parse synthetic data instantly.

---

## 📁 Project Layout
```
pdf-parser-ui/
├── app.py                # Flask backend
├── requirements.txt      # Python deps
├── templates/index.html            # Single-page front-end
├── README.md             # this file
└── .env.example          # copy to .env
```

---

## 🧑‍💻 Contributing
1. Fork the repo.  
2. Create a feature branch `git checkout -b feat/xyz`.  
3. Commit & push.  
4. Open a Pull Request.

---

## 📄 License  
MIT © Rayan Haroon(https://github.com/1rayanharoon)

---

