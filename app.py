# Flask entrypoint that exposes REST routes and initializes background jobs.
import logging
from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
from models import init_db, list_articles, add_favorite, list_favorites, delete_favorite
from scheduler import start_scheduler

def create_app():
    """Creates and configures the Flask application."""
    load_dotenv(override=True)
    app = Flask(__name__)

    # Simple structured logging setup.
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    app.logger.setLevel(logging.INFO)

    # Ensure database exists and schedule background updates.
    init_db()
    start_scheduler()

    # Root route serving a small UI.
    @app.get("/")
    def home():
        return render_template("index.html")

    # REST endpoint for paginated articles.
    @app.get("/api/articles")
    def api_articles():
        topic = request.args.get("topic")
        page = max(int(request.args.get("page", 1)), 1)
        limit = min(max(int(request.args.get("limit", 10)), 1), 100)
        items, total = list_articles(topic, page, limit)
        return jsonify({"items": items, "total": total, "page": page, "limit": limit})

    # Endpoint returning saved favorites.
    @app.get("/api/favorites")
    def api_list_fav():
        return jsonify(list_favorites())

    # Endpoint for adding a favorite.
    @app.post("/api/favorites")
    def api_add_fav():
        data = request.get_json(force=True, silent=True) or {}
        article_id = data.get("article_id")
        if not isinstance(article_id, int):
            return jsonify({"error": "article_id (int) required"}), 400
        rid = add_favorite(article_id)
        return jsonify({"status": "ok", "id": rid}), 201

    # Endpoint for deleting a favorite.
    @app.delete("/api/favorites/<int:article_id>")
    def api_del_fav(article_id: int):
        n = delete_favorite(article_id)
        return jsonify({"deleted": n})

    return app

# Expose the Flask app object for `flask run`.
app = create_app()

# Optional: run directly using `python app.py`
if __name__ == "__main__":
    app.run(debug=True)
