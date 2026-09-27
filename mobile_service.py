"""
Mobile Service - Backend support for mobile applications (API helpers, sync, push)
"""

import logging
from typing import Dict, Any
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

class MobileService:
    def __init__(self, db_connection_string: str):
        self.db_conn_string = db_connection_string

    def _get_connection(self):
        try:
            conn = psycopg2.connect(self.db_conn_string)
            return conn
        except Exception as e:
            logger.error(f"DB connect error: {e}")
            return None

    def register_device(self, user_id: str, device_token: str, platform: str) -> Dict[str, Any]:
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'DB connection failed'}
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO mobile_devices (user_id, device_token, platform, registered_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (device_token) DO UPDATE SET user_id = EXCLUDED.user_id, platform = EXCLUDED.platform
            """, (user_id, device_token, platform, datetime.utcnow()))
            conn.commit()
            return {'success': True}
        except Exception as e:
            logger.error(f"register_device error: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def sync_user_content(self, user_id: str, last_sync: str = None) -> Dict[str, Any]:
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'DB connection failed'}
            cur = conn.cursor(cursor_factory=RealDictCursor)
            # Fetch content changed since last_sync
            if last_sync:
                cur.execute("""
                    SELECT id, content_type, content_id, changed_at FROM offline_sync_queue
                    WHERE student_id = %s AND queued_at > %s
                    ORDER BY queued_at ASC
                    LIMIT 200
                """, (user_id, last_sync))
            else:
                cur.execute("""
                    SELECT id, content_type, content_id, queued_at as changed_at FROM offline_sync_queue
                    WHERE student_id = %s
                    ORDER BY queued_at ASC
                    LIMIT 200
                """, (user_id,))
            items = cur.fetchall()
            return {'success': True, 'items': [dict(i) for i in items]}
        except Exception as e:
            logger.error(f"sync_user_content error: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def submit_offline_event(self, user_id: str, event: Dict[str, Any]) -> Dict[str, Any]:
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'DB connection failed'}
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO mobile_offline_events (user_id, event_type, payload_json, created_at)
                VALUES (%s, %s, %s, %s)
            """, (user_id, event.get('type'), json.dumps(event.get('payload', {})), datetime.utcnow()))
            conn.commit()
            return {'success': True}
        except Exception as e:
            logger.error(f"submit_offline_event error: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()