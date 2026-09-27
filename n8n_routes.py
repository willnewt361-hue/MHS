"""
Blueprint-style routes for N8N workflow management (simple HTTP interface)
"""

from flask import Blueprint, request, jsonify
from n8n_workflows_service import N8NWorkflowService, WorkflowTriggerType
from flask import current_app as app

n8n_bp = Blueprint('n8n', __name__)

# Initialize service
db_url = app.config.get('DATABASE_URL', 'postgresql://postgres:##000000@localhost:5432/mengo_hub')
service = N8NWorkflowService(db_url)

@n8n_bp.route('/api/workflows', methods=['GET'])
def list_workflows():
    result = service.get_all_workflows()
    return jsonify(result), 200 if result.get('success') else 400

@n8n_bp.route('/api/workflows', methods=['POST'])
def create_workflow():
    data = request.get_json()
    result = service.create_workflow(
        data.get('workflow_name'),
        data.get('description',''),
        WorkflowTriggerType(data.get('trigger_type')),
        data.get('actions', []),
        data.get('created_by', 'system')
    )
    return jsonify(result), 201 if result.get('success') else 400

@n8n_bp.route('/api/workflows/trigger/<trigger>', methods=['POST'])
def trigger_workflow(trigger):
    data = request.get_json() or {}
    try:
        t = WorkflowTriggerType(trigger)
    except Exception:
        return jsonify({'success': False, 'error': 'Invalid trigger type'}), 400
    result = service.trigger_workflow(t, data)
    return jsonify(result), 200 if result.get('success') else 400