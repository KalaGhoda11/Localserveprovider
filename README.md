Localserve
Overview
Localserve is a lightweight local server built with Flask, designed to quickly serve static files and
dynamic templates.
It’s a minimal starting point for small projects, demos, or testing web applications locally.
■ Features
- Serve static files (CSS, JS, images, etc.)
- Render dynamic HTML pages using Jinja2 templates
- Simple and minimal Flask setup – easy to extend
- Developer-friendly structure
■ Project Structure
Localserve/
■■■ app.py # Main Flask application
■■■ templates/ # Jinja2 HTML templates
■ ■■■ index.html
■■■ static/ # Static assets (CSS, JS, images)
■■■ README.md # Documentation (this file)
■■ Installation
1. Clone the repository:
git clone https://github.com/KalaGhoda11/Localserve.git
cd Localserve
2. (Optional) Create a virtual environment:
python -m venv venv
source venv/bin/activate # Linux/macOS
venv\Scripts\activate # Windows
3. Install dependencies:
pip install -r requirements.txt
(If missing, run: pip install flask)
4. Run the server:
python app.py
5. Open your browser at:
http://127.0.0.1:5000
■ Usage
- Modify routes in app.py to add new endpoints
- Add HTML templates under templates/
- Store static files (CSS/JS/images) under static/
Example
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
■■ Customization
Change Flask server settings in app.py:
if __name__ == "__main__":
app.run(host="0.0.0.0", port=5000, debug=True)
■ Contributing
1. Fork the repo
2. Create a new branch (feature/new-feature)
3. Commit changes
4. Push and open a Pull Request
■ License
This project is licensed under the MIT License.
■ Author
- @SCRIPT KIDDOS (https://github.com/KalaGhoda11)
