"""
Audio & Music Service Module
Handles audio uploads, playlists, music overlays, and streaming
"""

import os
import json
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
import psycopg2
import psycopg2.extras

class AudioService:
    def __init__(self, db_connection):
        self.db = db_connection
        self.upload_folder = 'uploads/audio'
        os.makedirs(self.upload_folder, exist_ok=True)
        
    def upload_audio_file(self, file, audio_type, category, user_id, filename=None):
        """Upload an audio file"""
        try:
            if filename is None:
                filename = secure_filename(file.filename)
            
            file_path = os.path.join(self.upload_folder, filename)
            file.save(file_path)
            
            file_size = os.path.getsize(file_path)
            
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                INSERT INTO audio_files (filename, file_path, file_size, audio_type, category, uploaded_by)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (filename, file_path, file_size, audio_type, category, user_id))
            
            audio_id = cur.fetchone()['id']
            self.db.commit()
            cur.close()
            
            return {
                'success': True,
                'audio_id': audio_id,
                'filename': filename,
                'file_size': file_size
            }
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def create_playlist(self, playlist_name, user_id, is_public=True, description=""):
        """Create a new playlist"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                INSERT INTO playlists (playlist_name, description, created_by, is_public)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (playlist_name, description, user_id, 1 if is_public else 0))
            
            playlist_id = cur.fetchone()['id']
            self.db.commit()
            cur.close()
            
            return {'success': True, 'playlist_id': playlist_id}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def add_audio_to_playlist(self, playlist_id, audio_id, position=None):
        """Add audio file to playlist"""
        try:
            cur = self.db.cursor()
            
            if position is None:
                cur.execute("SELECT MAX(position) FROM playlist_items WHERE playlist_id = %s", (playlist_id,))
                result = cur.fetchone()
                position = (result[0] or 0) + 1
            
            cur.execute("""
                INSERT INTO playlist_items (playlist_id, audio_id, position)
                VALUES (%s, %s, %s)
            """, (playlist_id, audio_id, position))
            
            self.db.commit()
            cur.close()
            
            return {'success': True}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def create_music_overlay(self, overlay_name, audio_id, frequency, environment_type, description=""):
        """Create a music overlay (nature sounds, binaural beats, etc.)"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                INSERT INTO music_overlays (overlay_name, description, base_frequency, 
                    environment_type, audio_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (overlay_name, description, frequency, environment_type, audio_id))
            
            overlay_id = cur.fetchone()['id']
            self.db.commit()
            cur.close()
            
            return {'success': True, 'overlay_id': overlay_id}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_playlists(self, user_id):
        """Get user's playlists"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                SELECT id, playlist_name, description, is_public, created_at
                FROM playlists
                WHERE created_by = %s OR is_public = 1
                ORDER BY created_at DESC
            """, (user_id,))
            
            playlists = cur.fetchall()
            cur.close()
            
            return {'success': True, 'playlists': [dict(p) for p in playlists]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_playlist_items(self, playlist_id):
        """Get items in a playlist"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                SELECT pi.id, pi.position, af.id as audio_id, af.filename, af.duration_seconds
                FROM playlist_items pi
                JOIN audio_files af ON pi.audio_id = af.id
                WHERE pi.playlist_id = %s
                ORDER BY pi.position
            """, (playlist_id,))
            
            items = cur.fetchall()
            cur.close()
            
            return {'success': True, 'items': [dict(i) for i in items]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_music_overlays(self, environment_type=None):
        """Get available music overlays"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            if environment_type:
                cur.execute("""
                    SELECT id, overlay_name, description, base_frequency, environment_type
                    FROM music_overlays
                    WHERE environment_type = %s AND is_active = 1
                """, (environment_type,))
            else:
                cur.execute("""
                    SELECT id, overlay_name, description, base_frequency, environment_type
                    FROM music_overlays
                    WHERE is_active = 1
                """)
            
            overlays = cur.fetchall()
            cur.close()
            
            return {'success': True, 'overlays': [dict(o) for o in overlays]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def record_audio_playback(self, user_id, audio_id, duration_played, completed=False):
        """Record audio playback history"""
        try:
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO audio_playback_history (student_id, audio_id, play_duration_seconds, completed)
                VALUES (%s, %s, %s, %s)
            """, (user_id, audio_id, duration_played, 1 if completed else 0))
            
            # Update audio view count
            cur.execute("UPDATE audio_files SET view_count = view_count + 1 WHERE id = %s", (audio_id,))
            
            self.db.commit()
            cur.close()
            
            return {'success': True}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_audio_stats(self, audio_id):
        """Get audio file statistics"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                SELECT id, filename, file_size, duration_seconds, audio_type, 
                    view_count, created_at
                FROM audio_files
                WHERE id = %s
            """, (audio_id,))
            
            stats = cur.fetchone()
            cur.close()
            
            if stats:
                return {'success': True, 'stats': dict(stats)}
            return {'success': False, 'error': 'Audio not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Initialize service
audio_service = None

def init_audio_service(db_connection):
    global audio_service
    audio_service = AudioService(db_connection)
    return audio_service
