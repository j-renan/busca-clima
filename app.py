from dotenv import load_dotenv
from flask import Flask, render_template, request
from weather_service import get_weather_by_city

# Carrega variáveis do .env para o ambiente do SO
load_dotenv()

app = Flask(__name__)


@app.route('/', methods=["GET"])
def home():
    """Rota principal — renderiza o dashboard via Jinja2."""
    cidade = request.args.get('cidade', '').strip()
    weather = None
    error = None

    if cidade:
        result = get_weather_by_city(cidade)
        if result["error"]:
            error = result["message"]
        else:
            weather = result["data"]

    return render_template("index.html", weather=weather, error=error, cidade=cidade)


if __name__ == '__main__':
    app.run(debug=True)


