from flask import Blueprint, jsonify, render_template
from twinelib.data import data

twine_story_bp = Blueprint('twinestory', __name__)

@twine_story_bp.route('/')
def index():
    # Renders the main game page (HTML + JS)
    return render_template('story.html')

@twine_story_bp.route('/scene/<scene_name>', methods=['GET'])
def get_scene(scene_name):
    for passage in data["passages"]:
        if passage["name"] == scene_name:
            return jsonify(passage)
    return jsonify({"error": "Scene not found"}), 404
