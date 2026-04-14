import os
from flask import Flask, render_template
from flask_cors import CORS
from config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH
from routes.upload import upload_bp
from routes.flashcards import flashcards_bp
from routes.chatbot import chatbot_bp

app = Flask(__name__)
CORS(app)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# Register blueprints
app.register_blueprint(upload_bp)
app.register_blueprint(flashcards_bp)
app.register_blueprint(chatbot_bp)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, port=5000)
