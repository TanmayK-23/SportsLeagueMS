# 🏟️ Sports League Management System (SLMS)

A premium, high-performance web application built with **Flask** and **MySQL**, featuring a state-of-the-art **Glassmorphism** interface inspired by Raycast.

![Design System](https://img.shields.io/badge/Design-Raycast_Inspired-FF6363?style=for-the-badge)
![Tech Stack](https://img.shields.io/badge/Tech-Flask_%7C_MySQL-55b3ff?style=for-the-badge)

## ✨ Features

- **Premium UI/UX**: Full-width glassmorphism interface with real-time blur, multi-layered shadows, and obsidian-dark aesthetics.
- **Dynamic Player Database**: Browse cricket and football players with a fast, responsive search and role-based filtering system.
- **Real-time Statistics**: Live row counters and status badges that update instantly as you filter data.
- **Seamless Registration**: Multi-panel registration flow with sport-to-position mapping and validation.
- **Human-readable Data**: Automatically formatted dates (e.g., *7 July 1981*) for a better user experience.

## 🚀 Tech Stack

- **Backend**: Python / Flask
- **Database**: MySQL
- **Frontend**: Vanilla HTML5, CSS3 (Advanced Glassmorphism), JavaScript (ES6+)
- **Typography**: Inter (with full OpenType features enabled)
- **Design System**: Detailed in `DESIGN.md`

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd SL-DBMS
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### 3. Database Configuration
1. Ensure MySQL is running on your system.
2. Create the database:
   ```sql
   CREATE DATABASE SportsLeagueDB;
   ```
3. Import your schema (if available) or create the `Country` and `Player` tables.
4. Update the connection details in `app.py`:
   ```python
   db = mysql.connector.connect(
       host="localhost",
       user="root",
       password="YOUR_PASSWORD",
       database="SportsLeagueDB"
   )
   ```

### 4. Run the Application
```bash
python app.py
```
Visit `http://127.0.0.1:5000` in your browser.

## 🎨 Design Principles

This project follows a strict design philosophy modeled after **Raycast**:
- **Background**: Near-Black Blue-tint (`#07080a`)
- **Glass Effect**: `backdrop-filter: blur(24px)` with multi-layered inset highlights.
- **Typography**: Positive letter-spacing (+0.2px) for readability on dark surfaces.
- **Color Palette**: Raycast Red (`#FF6363`) for accents and Raycast Blue for interactive elements.

---
Developed as a DBMS Mini Project • 2026
