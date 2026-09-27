"""
Chat & Communication Service Module
Handles group chats, direct messages, file sharing, and feature toggles
"""

import os
import json
from datetime import datetime
import psycopg2
import psycopg2.extras

class ChatService:
    def __init__(self, db_connection):
        self.db = db_connection
        self.upload_folder = 'uploads/chat'
        os.makedirs(self.upload_folder, exist_ok=True)
        
    def create_group_chat(self, group_name, created_by, group_type='general', description=""):
        """Create a new group chat"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                INSERT INTO chat_groups (group_name, description, created_by, group_type, is_active)
                VALUES (%s, %s, %s, %s, 1)
                RETURNING id
            """, (group_name, description, created_by, group_type))
            
            group_id = cur.fetchone()['id']
            
            # Add creator as member
            cur.execute("""
                INSERT INTO chat_group_members (group_id, user_id, role)
                VALUES (%s, %s, 'admin')
            """, (group_id, created_by))
            
            self.db.commit()
            cur.close()
            
            return {'success': True, 'group_id': group_id}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def add_group_member(self, group_id, user_id, role='member'):
        """Add member to group"""
        try:
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO chat_group_members (group_id, user_id, role)
                VALUES (%s, %s, %s)
                ON CONFLICT (group_id, user_id) DO NOTHING
            """, (group_id, user_id, role))
            
            self.db.commit()
            cur.close()
            
            return {'success': True}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def send_group_message(self, group_id, sender_id, message_text, file_data=None):
        """Send message to group"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            file_path = None
            file_name = None
            message_type = 'text'
            
            if file_data:
                message_type = file_data.get('type', 'file')
                file_name = file_data.get('name')
                file_content = file_data.get('content')
                
                if file_content:
                    file_path = os.path.join(self.upload_folder, f"{group_id}_{file_name}")
                    with open(file_path, 'wb') as f:
                        f.write(file_content)
            
            cur.execute("""
                INSERT INTO chat_messages 
                (group_id, sender_id, message_text, message_type, file_path, file_name)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, created_at
            """, (group_id, sender_id, message_text, message_type, file_path, file_name))
            
            result = cur.fetchone()
            message_id = result['id']
            
            self.db.commit()
            cur.close()
            
            return {'success': True, 'message_id': message_id, 'timestamp': result['created_at']}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def send_direct_message(self, sender_id, recipient_id, message_text, file_data=None):
        """Send direct message to user"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            file_path = None
            file_name = None
            message_type = 'text'
            
            if file_data:
                message_type = file_data.get('type', 'file')
                file_name = file_data.get('name')
                file_content = file_data.get('content')
                
                if file_content:
                    file_path = os.path.join(self.upload_folder, 
                        f"dm_{sender_id}_{recipient_id}_{file_name}")
                    with open(file_path, 'wb') as f:
                        f.write(file_content)
            
            cur.execute("""
                INSERT INTO chat_messages 
                (sender_id, recipient_id, message_text, message_type, file_path, file_name)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, created_at
            """, (sender_id, recipient_id, message_text, message_type, file_path, file_name))
            
            result = cur.fetchone()
            message_id = result['id']
            
            self.db.commit()
            cur.close()
            
            return {'success': True, 'message_id': message_id, 'timestamp': result['created_at']}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_group_messages(self, group_id, limit=50, offset=0):
        """Get messages from group"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                SELECT id, sender_id, message_text, message_type, file_path, file_name, 
                    is_read, created_at, edited_at
                FROM chat_messages
                WHERE group_id = %s AND deleted_at IS NULL
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (group_id, limit, offset))
            
            messages = cur.fetchall()
            cur.close()
            
            return {'success': True, 'messages': [dict(m) for m in messages]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_direct_messages(self, user_id, other_user_id, limit=50, offset=0):
        """Get direct messages between two users"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                SELECT id, sender_id, recipient_id, message_text, message_type, 
                    file_path, file_name, is_read, created_at, edited_at
                FROM chat_messages
                WHERE deleted_at IS NULL
                AND ((sender_id = %s AND recipient_id = %s) OR 
                     (sender_id = %s AND recipient_id = %s))
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (user_id, other_user_id, other_user_id, user_id, limit, offset))
            
            messages = cur.fetchall()
            
            # Mark as read
            cur.execute("""
                UPDATE chat_messages SET is_read = 1, read_at = CURRENT_TIMESTAMP
                WHERE recipient_id = %s AND sender_id = %s AND is_read = 0
            """, (user_id, other_user_id))
            
            self.db.commit()
            cur.close()
            
            return {'success': True, 'messages': [dict(m) for m in messages]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def mark_message_read(self, message_id):
        """Mark message as read"""
        try:
            cur = self.db.cursor()
            cur.execute("""
                UPDATE chat_messages 
                SET is_read = 1, read_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (message_id,))
            
            self.db.commit()
            cur.close()
            
            return {'success': True}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def edit_message(self, message_id, sender_id, new_text):
        """Edit a sent message"""
        try:
            cur = self.db.cursor()
            cur.execute("""
                UPDATE chat_messages 
                SET message_text = %s, edited_at = CURRENT_TIMESTAMP
                WHERE id = %s AND sender_id = %s AND deleted_at IS NULL
            """, (new_text, message_id, sender_id))
            
            if cur.rowcount == 0:
                cur.close()
                return {'success': False, 'error': 'Message not found or cannot edit'}
            
            self.db.commit()
            cur.close()
            
            return {'success': True}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def delete_message(self, message_id, sender_id):
        """Soft delete a message"""
        try:
            cur = self.db.cursor()
            cur.execute("""
                UPDATE chat_messages 
                SET deleted_at = CURRENT_TIMESTAMP
                WHERE id = %s AND sender_id = %s
            """, (message_id, sender_id))
            
            self.db.commit()
            cur.close()
            
            return {'success': True}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def add_message_reaction(self, message_id, user_id, emoji):
        """Add emoji reaction to message"""
        try:
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO chat_reactions (message_id, user_id, emoji)
                VALUES (%s, %s, %s)
                ON CONFLICT (message_id, user_id, emoji) DO NOTHING
            """, (message_id, user_id, emoji))
            
            self.db.commit()
            cur.close()
            
            return {'success': True}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_user_groups(self, user_id):
        """Get groups user is member of"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                SELECT cg.id, cg.group_name, cg.description, cg.group_type, 
                    cgm.role, cg.created_at
                FROM chat_groups cg
                JOIN chat_group_members cgm ON cg.id = cgm.group_id
                WHERE cgm.user_id = %s AND cg.is_active = 1
                ORDER BY cg.created_at DESC
            """, (user_id,))
            
            groups = cur.fetchall()
            cur.close()
            
            return {'success': True, 'groups': [dict(g) for g in groups]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Feature Toggle Management
    def toggle_feature(self, feature_name, is_enabled, disabled_message=None, disabled_until=None):
        """Toggle a feature (chat, DMs, etc.) globally"""
        try:
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO feature_toggles 
                (feature_name, is_enabled, is_global, disabled_message, disabled_until, updated_at)
                VALUES (%s, %s, 1, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (feature_name) DO UPDATE SET
                    is_enabled = EXCLUDED.is_enabled,
                    disabled_message = EXCLUDED.disabled_message,
                    disabled_until = EXCLUDED.disabled_until,
                    updated_at = CURRENT_TIMESTAMP
            """, (feature_name, 1 if is_enabled else 0, disabled_message, disabled_until))
            
            self.db.commit()
            cur.close()
            
            return {'success': True}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def is_feature_enabled(self, feature_name):
        """Check if feature is enabled"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                SELECT is_enabled, disabled_message, disabled_until
                FROM feature_toggles
                WHERE feature_name = %s
            """, (feature_name,))
            
            result = cur.fetchone()
            cur.close()
            
            if result:
                if result['is_enabled']:
                    return {'enabled': True}
                else:
                    message = result['disabled_message'] or "Feature is disabled at this time"
                    return {
                        'enabled': False, 
                        'message': message,
                        'until': result['disabled_until']
                    }
            
            # Feature not configured - enable by default
            return {'enabled': True}
        except Exception as e:
            return {'enabled': True, 'error': str(e)}

# Initialize service
chat_service = None

def init_chat_service(db_connection):
    global chat_service
    chat_service = ChatService(db_connection)
    return chat_service
