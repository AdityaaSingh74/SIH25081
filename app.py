from flask import Flask, render_template, request
from src.backend.models.model import predict_result

app = Flask(__name__, template_folder="src/frontend/templates", static_folder="src/frontend/static")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    input_data = request.form["user_input"]
    prediction = predict_result(input_data)
    return render_template("result.html", prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)
