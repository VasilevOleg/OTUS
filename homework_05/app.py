from flask import Flask, render_template, url_for

# Инициализация Flask-приложения
app = Flask(__name__)

@app.route('/')
def index():
    # Отображаем главную страницу
    return render_template('index.html')

@app.route('/about/')
def about():
    # Отображаем страницу "О нас"
    return render_template('about.html')

if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5050,
    )
