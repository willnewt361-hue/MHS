"""
Routes for mobile app integration
"""

from flask import Blueprint, request, jsonify, session
from mobile_service import MobileService
from flask import current_app as app

mobile_bp = Blueprint('mobile', __name__)

db_url = app.config.get('DATABASE_URL', 'postgresql://postgres:##000000@localhost:5432/mengo_hub')
service = MobileService(db_url)

@mobile_bp.route('/api/mobile/register_device', methods=['POST'])
def register_device():
    data = request.get_json()
    user_id = session.get('user_id') or data.get('user_id')
    device_token = data.get('device_token')
    platform = data.get('platform', 'android')
    result = service.register_device(user_id, device_token, platform)
    return jsonify(result), 200 if result.get('success') else 400

@mobile_bp.route('/api/mobile/sync', methods=['GET'])
def sync():
    user_id = session.get('user_id') or request.args.get('user_id')
    last_sync = request.args.get('last_sync')
    result = service.sync_user_content(user_id, last_sync)
    return jsonify(result), 200 if result.get('success') else 400

@mobile_bp.route('/api/mobile/offline_event', methods=['POST'])
def offline_event():
    user_id = session.get('user_id') or request.json.get('user_id')
    event = request.get_json()
    result = service.submit_offline_event(user_id, event)
    return jsonify(result), 201 if result.get('success') else 400