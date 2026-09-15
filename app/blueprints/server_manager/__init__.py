import datetime
import json
import uuid

from flask import Blueprint, jsonify, render_template, request

from ...config import Config
from ...models import Medium, db
from .utils import (
    authenticate_jellyfin,
    fetch_jellyfin_libraries,
    fetch_media_from_library,
    load_servers,
    save_servers,
)


server_bp = Blueprint("server", __name__, template_folder="../templates", url_prefix="/servers")

@server_bp.route("/", methods=["GET"])
def list_servers():
    servers = load_servers(Config)
    return render_template("servers.html", servers=servers)

@server_bp.route("/add", methods=["POST"])
def add_server():
    data = request.form
    server_url = data.get("server_url")
    username = data.get("username")
    password = data.get("password")

    if not all([server_url, username, password]):
        return jsonify({"error": "Missing credentials!"}), 400

    try:
        access_token, user_id = authenticate_jellyfin(server_url, username, password)
        libraries = fetch_jellyfin_libraries(server_url, access_token, user_id)
        media_libraries = [
            lib for lib in libraries
            if lib.get("CollectionType") in ["movies", "tvshows"]
        ]
        if not media_libraries:
            return jsonify({"error": "No library for movies or tvshows found."}), 400
    except Exception as e:
        return jsonify({"error": f"Connection failed: {str(e)}"}), 400

    server_id = str(uuid.uuid4())
    servers = load_servers(Config)
    servers.append({
        "id": server_id,
        "url": server_url,
        "username": username,
        "password": password,
        "access_token": access_token,
        "user_id": user_id,
        "libraries": media_libraries
    })
    save_servers(servers, Config)

    return jsonify({"success": True, "server_id": server_id})

@server_bp.route("/<server_id>/delete", methods=["POST"])
def delete_server(server_id):
    """Löscht einen Server."""
    servers = load_servers(Config)
    servers = [s for s in servers if s["id"] != server_id]
    save_servers(servers, Config)
    return jsonify({"success": True})

@server_bp.route("/<server_id>/fetch", methods=["POST"])
def fetch_media(server_id):
    servers = load_servers(Config)
    server = next((s for s in servers if s["id"] == server_id), None)
    if not server:
        return jsonify({"error": "Server not found!"}), 404

    try:
        access_token = server["access_token"]
        # user_id = server["user_id"]
        libraries = server["libraries"]

        for library in libraries:
            library_id = library["Id"]
            library_type = library["CollectionType"]
            media_type = "Movie" if library_type == "movies" else "Series"

            media_items = fetch_media_from_library(
                server["url"], access_token, library_id, media_type
            )

            for item in media_items:
                unique_id = item.get("ProviderIds", {}).get("Tmdb") or f"{item['Name']}_{item.get('ProductionYear', '')}"

                existing_media = Medium.query.get(unique_id)
                if existing_media:

                    if existing_media.last_updated < item.get("DateLastModified", existing_media.last_updated):
                        existing_media.title = item["Name"]
                        existing_media.year = item.get("ProductionYear")
                        existing_media.poster_url = item.get("PrimaryImageTag")
                        existing_media.last_updated = datetime.utcnow()
                        db.session.commit()
                else:
                    new_media = Medium(
                        id=unique_id,
                        title=item["Name"],
                        year=item.get("ProductionYear"),
                        type=media_type,
                        poster_url=item.get("PrimaryImageTag"),
                        jellyfin_servers=json.dumps([server_id]),
                        tmdb_id=item.get("ProviderIds", {}).get("Tmdb"),
                        imdb_id=item.get("ProviderIds", {}).get("Imdb")
                    )
                    db.session.add(new_media)
                    db.session.commit()

        return jsonify({"success": True, "fetched": len(media_items)})
    except Exception as e:
        return jsonify({"error": f"Error fetching: {str(e)}"}), 500
