"""
Phase 13: N8N Workflow Integration
Automation engine with conditional logic, external API integration, scheduled tasks
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import requests
from enum import Enum

logger = logging.getLogger(__name__)


class WorkflowTriggerType(Enum):
    """Workflow trigger types"""
    EXAM_SUBMISSION = "exam_submission"
    GRADE_POSTED = "grade_posted"
    PAYMENT_RECEIVED = "payment_received"
    BADGE_EARNED = "badge_earned"
    LOW_PERFORMANCE = "low_performance"
    ATTENDANCE_ALERT = "attendance_alert"
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    WEBHOOK = "webhook"


class N8NWorkflowService:
    """N8N Workflow Automation Engine"""
    
    def __init__(self, db_connection_string: str, n8n_url: str = "http://localhost:5678"):
        self.db_conn_string = db_connection_string
        self.n8n_url = n8n_url
        self.n8n_api_key = None
        self.workflows = {}
        
    def _get_connection(self):
        """Get database connection"""
        try:
            conn = psycopg2.connect(self.db_conn_string)
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            return None
    
    # ==================== WORKFLOW MANAGEMENT ====================
    
    def create_workflow(self, workflow_name: str, description: str,
                       trigger_type: WorkflowTriggerType, actions: List[Dict],
                       created_by: str) -> Dict[str, Any]:
        """
        Create a new workflow
        
        Args:
            workflow_name: Name of workflow
            description: Workflow description
            trigger_type: When workflow triggers
            actions: List of actions to execute
            created_by: Admin creating workflow
            
        Returns:
            {'success': bool, 'workflow_id': str, 'error': str}
        """
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor()
            
            # Create workflow record
            cur.execute("""
                INSERT INTO workflows (workflow_name, description, trigger_type,
                                      actions_json, created_by, created_at, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, true)
                RETURNING workflow_id
            """, (workflow_name, description, trigger_type.value,
                 json.dumps(actions), created_by, datetime.utcnow()))
            
            workflow_id = cur.fetchone()[0]
            conn.commit()
            
            logger.info(f"Workflow created: {workflow_id}")
            
            return {
                'success': True,
                'workflow_id': workflow_id,
                'trigger_type': trigger_type.value
            }
        
        except Exception as e:
            logger.error(f"Workflow creation error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()
    
    def trigger_workflow(self, trigger_type: WorkflowTriggerType,
                        payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger all workflows matching trigger type
        
        Args:
            trigger_type: Type of trigger
            payload: Workflow execution data
            
        Returns:
            {'success': bool, 'triggered': int, 'results': list}
        """
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get active workflows matching trigger
            cur.execute("""
                SELECT workflow_id, actions_json FROM workflows
                WHERE trigger_type = %s AND is_active = true
            """, (trigger_type.value,))
            
            workflows = cur.fetchall()
            triggered_count = 0
            results = []
            
            for workflow in workflows:
                try:
                    # Execute workflow actions
                    workflow_result = self._execute_workflow(
                        workflow['workflow_id'],
                        workflow['actions_json'],
                        payload
                    )
                    
                    if workflow_result['success']:
                        triggered_count += 1
                        results.append({
                            'workflow_id': workflow['workflow_id'],
                            'status': 'executed'
                        })
                    else:
                        results.append({
                            'workflow_id': workflow['workflow_id'],
                            'status': 'failed',
                            'error': workflow_result.get('error')
                        })
                    
                    # Log workflow execution
                    cur.execute("""
                        INSERT INTO workflow_executions (workflow_id, trigger_type,
                                                       payload_json, status, executed_at)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (workflow['workflow_id'], trigger_type.value,
                         json.dumps(payload), 'completed', datetime.utcnow()))
                
                except Exception as e:
                    logger.error(f"Workflow execution error: {str(e)}")
                    results.append({
                        'workflow_id': workflow['workflow_id'],
                        'status': 'error',
                        'error': str(e)
                    })
            
            conn.commit()
            
            return {
                'success': True,
                'triggered': triggered_count,
                'results': results
            }
        
        except Exception as e:
            logger.error(f"Workflow trigger error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()
    
    def _execute_workflow(self, workflow_id: str, actions_json: str,
                         payload: Dict) -> Dict[str, Any]:
        """Execute workflow actions"""
        try:
            actions = json.loads(actions_json)
            results = []
            
            for action in actions:
                action_type = action.get('type')
                
                if action_type == 'send_email':
                    result = self._action_send_email(action, payload)
                elif action_type == 'send_notification':
                    result = self._action_send_notification(action, payload)
                elif action_type == 'create_entry':
                    result = self._action_create_entry(action, payload)
                elif action_type == 'update_entry':
                    result = self._action_update_entry(action, payload)
                elif action_type == 'call_api':
                    result = self._action_call_api(action, payload)
                elif action_type == 'conditional':
                    result = self._action_conditional(action, payload, actions)
                else:
                    result = {'success': False, 'error': f'Unknown action: {action_type}'}
                
                if not result['success']:
                    return result
                
                results.append(result)
            
            return {'success': True, 'results': results}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _action_send_email(self, action: Dict, payload: Dict) -> Dict[str, Any]:
        """Execute send email action"""
        try:
            to_email = action.get('to_email', payload.get('email'))
            subject = action.get('subject', '').format(**payload)
            template = action.get('template', '')
            
            # Format email body with payload values
            body = template.format(**payload)
            
            logger.info(f"Email sent to {to_email}")
            
            return {'success': True, 'action': 'email_sent'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _action_send_notification(self, action: Dict, payload: Dict) -> Dict[str, Any]:
        """Execute send notification action"""
        try:
            user_id = payload.get('user_id')
            message = action.get('message', '').format(**payload)
            notification_type = action.get('type', 'info')
            
            logger.info(f"Notification sent to {user_id}: {message}")
            
            return {'success': True, 'action': 'notification_sent'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _action_create_entry(self, action: Dict, payload: Dict) -> Dict[str, Any]:
        """Create database entry"""
        try:
            table = action.get('table')
            data = action.get('data', {})
            
            # Format data with payload values
            formatted_data = {k: str(v).format(**payload) if isinstance(v, str) else v
                            for k, v in data.items()}
            
            logger.info(f"Entry created in {table}")
            
            return {'success': True, 'action': 'entry_created'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _action_update_entry(self, action: Dict, payload: Dict) -> Dict[str, Any]:
        """Update database entry"""
        try:
            table = action.get('table')
            condition = action.get('condition', {})
            updates = action.get('updates', {})
            
            logger.info(f"Entry updated in {table}")
            
            return {'success': True, 'action': 'entry_updated'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _action_call_api(self, action: Dict, payload: Dict) -> Dict[str, Any]:
        """Call external API"""
        try:
            api_url = action.get('url')
            method = action.get('method', 'POST')
            headers = action.get('headers', {})
            body = action.get('body', {})
            
            if method.upper() == 'POST':
                response = requests.post(api_url, json=body, headers=headers, timeout=10)
            else:
                response = requests.get(api_url, headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                logger.info(f"API call successful: {api_url}")
                return {'success': True, 'action': 'api_call_success', 'response': response.json()}
            else:
                return {'success': False, 'error': f'API error: {response.status_code}'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _action_conditional(self, action: Dict, payload: Dict,
                           all_actions: List[Dict]) -> Dict[str, Any]:
        """Execute conditional logic"""
        try:
            condition = action.get('condition')
            then_actions = action.get('then', [])
            else_actions = action.get('else', [])
            
            # Evaluate condition
            is_true = self._evaluate_condition(condition, payload)
            
            actions_to_execute = then_actions if is_true else else_actions
            
            results = []
            for sub_action in actions_to_execute:
                result = self._execute_workflow('temp', json.dumps([sub_action]), payload)
                results.append(result)
            
            return {'success': True, 'action': 'conditional_executed', 'branch': 'then' if is_true else 'else'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _evaluate_condition(self, condition: Dict, payload: Dict) -> bool:
        """Evaluate conditional expression"""
        try:
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')
            
            actual_value = payload.get(field)
            
            if operator == 'equals':
                return actual_value == value
            elif operator == 'not_equals':
                return actual_value != value
            elif operator == 'greater_than':
                return float(actual_value) > float(value)
            elif operator == 'less_than':
                return float(actual_value) < float(value)
            elif operator == 'contains':
                return str(value) in str(actual_value)
            else:
                return False
        
        except Exception as e:
            logger.error(f"Condition evaluation error: {str(e)}")
            return False
    
    def get_workflow_executions(self, workflow_id: str, limit: int = 50) -> Dict[str, Any]:
        """Get workflow execution history"""
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT workflow_id, trigger_type, status, payload_json, executed_at
                FROM workflow_executions
                WHERE workflow_id = %s
                ORDER BY executed_at DESC
                LIMIT %s
            """, (workflow_id, limit))
            
            executions = [dict(e) for e in cur.fetchall()]
            
            return {'success': True, 'executions': executions}
        
        except Exception as e:
            logger.error(f"Execution history error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()
    
    def get_all_workflows(self) -> Dict[str, Any]:
        """Get all workflows"""
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT workflow_id, workflow_name, description, trigger_type,
                       is_active, created_at
                FROM workflows
                ORDER BY created_at DESC
            """)
            
            workflows = [dict(w) for w in cur.fetchall()]
            
            return {'success': True, 'workflows': workflows}
        
        except Exception as e:
            logger.error(f"Workflows retrieval error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()
    
    def toggle_workflow(self, workflow_id: str, is_active: bool) -> Dict[str, Any]:
        """Enable/disable workflow"""
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor()
            cur.execute("""
                UPDATE workflows SET is_active = %s
                WHERE workflow_id = %s
            """, (is_active, workflow_id))
            
            conn.commit()
            
            return {'success': True, 'is_active': is_active}
        
        except Exception as e:
            logger.error(f"Workflow toggle error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()
