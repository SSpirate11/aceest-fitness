"""ACEest Fitness & Gym - Flask application entry point."""
import os

from flask import Flask, jsonify, render_template_string, request

from aceest import __version__, fitness

HOME_PAGE = """<!doctype html>
<html><head><title>ACEest Fitness & Gym</title>
<style>body{font-family:Arial;background:#1a1a1a;color:#eee;margin:40px}
h1{color:#d4af37}.card{background:#333;padding:16px;margin:12px 0;border-radius:8px}
code{color:#d4af37}</style></head>
<body><h1>ACEest Fitness &amp; Gym</h1><p>Version {{ version }}</p>
{% for code, p in programs.items() %}
<div class="card"><h3>{{ p.name }} ({{ code }})</h3>
<p><b>Workout:</b> {{ p.workout | join(' | ') }}</p>
<p><b>Diet:</b> {{ p.diet | join(' | ') }}</p></div>
{% endfor %}
<p>API: <code>/health</code> <code>/api/programs</code></p>
</body></html>"""


def create_app(test_config=None):
    app = Flask(__name__)
    if test_config:
        app.config.update(test_config)

    @app.errorhandler(ValueError)
    def handle_value_error(err):
        return jsonify(error=str(err)), 400

    @app.get("/")
    def home():
        return render_template_string(HOME_PAGE, version=__version__,
                                      programs=fitness.PROGRAMS)

    @app.get("/health")
    def health():
        return jsonify(status="ok", version=__version__)

    @app.get("/api/programs")
    def list_programs():
        return jsonify({code: p["name"] for code, p in fitness.PROGRAMS.items()})

    @app.get("/api/programs/<code>")
    def program_detail(code):
        program = fitness.get_program(code)
        if program is None:
            return jsonify(error=f"Program '{code}' not found"), 404
        return jsonify(program)

    @app.post("/api/calories")
    def calories():
        data = request.get_json(silent=True) or {}
        kcal = fitness.calculate_calories(data.get("weight", 0), data.get("program"))
        return jsonify(program=data["program"].upper(), calories=kcal)

    @app.post("/api/bmi")
    def bmi():
        data = request.get_json(silent=True) or {}
        value, category = fitness.calculate_bmi(data.get("weight", 0),
                                                data.get("height", 0))
        return jsonify(bmi=value, category=category)

    @app.post("/api/generate-program")
    def generate_program():
        data = request.get_json(silent=True) or {}
        return jsonify(fitness.generate_program(data.get("program"),
                                                data.get("level"),
                                                seed=data.get("seed")))

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
