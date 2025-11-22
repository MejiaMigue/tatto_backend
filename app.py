from flask import Flask, jsonify
from flask_cors import CORS
from models import db
from config import Config

# Importar blueprints
from routes.clientes import clientes_bp
from routes.tatuadores import tatuadores_bp
from routes.citas import citas_bp

app = Flask(__name__)
app.config.from_object(Config)
app.url_map.strict_slashes = False

# ✅ Configuración CORS para producción
CORS(app, origins=["https://tatto-frontend-topaz.vercel.app"])

db.init_app(app)

# Registrar blueprints
app.register_blueprint(clientes_bp, url_prefix="/api/clientes")
app.register_blueprint(tatuadores_bp, url_prefix="/api/tatuadores")
app.register_blueprint(citas_bp, url_prefix="/api/citas")

@app.route("/")
def home():
    return "✅ Flask está funcionando y conectado a la BD"

@app.route("/api/health")
def health():
    return {"status": "ok"}

@app.route("/api/debug")
def debug():
    return jsonify({
        "rules": [str(rule) for rule in app.url_map.iter_rules()]
    })

@app.route("/api/init-db")
def init_db():
    with app.app_context():
        db.create_all()
    return {"status": "Tablas creadas"}

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
