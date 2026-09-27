"""
Document Management Service Module
Handles document uploads, categorization, versioning, and access control
"""

import os
import json
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
import psycopg2
import psycopg2.extras

class DocumentService:
    def __init__(self, db_connection):
        self.db = db_connection
        self.upload_folder = 'uploads/documents'
        self.allowed_extensions = {'pdf', 'docx', 'doc', 'txt'}
        os.makedirs(self.upload_folder, exist_ok=True)
        
    def upload_document(self, file, subject, academic_level, document_type, teacher_id, 
                       title=None, description=""):
        """Upload a document"""
        try:
            if not self.allowed_file(file.filename):
                return {'success': False, 'error': 'File type not allowed'}
            
            filename = secure_filename(file.filename)
            file_ext = filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{datetime.now().timestamp()}_{filename}"
            file_path = os.path.join(self.upload_folder, unique_filename)
            
            file.save(file_path)
            file_size = os.path.getsize(file_path)
            
            if title is None:
                title = filename.rsplit('.', 1)[0]
            
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                INSERT INTO documents (filename, file_path, file_size, file_type, 
                    document_type, subject, academic_level, uploaded_by, title, 
                    description, version)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (filename, file_path, file_size, file_ext, document_type, subject, 
                  academic_level, teacher_id, title, description, 1))
            
            doc_id = cur.fetchone()['id']
            self.db.commit()
            cur.close()
            
            return {'success': True, 'document_id': doc_id, 'filename': filename}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def allowed_file(self, filename):
        """Check if file extension is allowed"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def grant_document_access(self, document_id, student_id, access_level='view'):
        """Grant access to a document for a student"""
        try:
            cur = self.db.cursor()
            cur.execute("""
                INSERT INTO document_access (document_id, student_id, access_level)
                VALUES (%s, %s, %s)
                ON CONFLICT (document_id, student_id) 
                DO UPDATE SET access_level = EXCLUDED.access_level
            """, (document_id, student_id, access_level))
            
            self.db.commit()
            cur.close()
            
            return {'success': True}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def grant_bulk_access(self, document_id, student_list, access_level='view'):
        """Grant access to multiple students"""
        try:
            cur = self.db.cursor()
            
            for student_id in student_list:
                cur.execute("""
                    INSERT INTO document_access (document_id, student_id, access_level)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (document_id, student_id) 
                    DO UPDATE SET access_level = EXCLUDED.access_level
                """, (document_id, student_id, access_level))
            
            self.db.commit()
            cur.close()
            
            return {'success': True}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_accessible_documents(self, user_id, filters=None):
        """Get documents accessible to a user"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            query = """
                SELECT d.id, d.title, d.filename, d.document_type, d.subject, 
                    d.academic_level, d.uploaded_by, d.file_size, d.download_count, 
                    d.created_at, da.access_level
                FROM documents d
                LEFT JOIN document_access da ON d.id = da.document_id AND da.student_id = %s
                WHERE (d.is_public = 1 OR da.access_level IS NOT NULL)
            """
            params = [user_id]
            
            if filters:
                if filters.get('subject'):
                    query += " AND d.subject = %s"
                    params.append(filters['subject'])
                if filters.get('academic_level'):
                    query += " AND d.academic_level = %s"
                    params.append(filters['academic_level'])
                if filters.get('document_type'):
                    query += " AND d.document_type = %s"
                    params.append(filters['document_type'])
            
            query += " ORDER BY d.created_at DESC"
            
            cur.execute(query, params)
            documents = cur.fetchall()
            cur.close()
            
            return {'success': True, 'documents': [dict(d) for d in documents]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def download_document(self, document_id, student_id):
        """Record document download"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            # Check access
            cur.execute("""
                SELECT d.* FROM documents d
                LEFT JOIN document_access da ON d.id = da.document_id
                WHERE d.id = %s AND (d.is_public = 1 OR 
                    (da.student_id = %s AND da.access_level IN ('view', 'download')))
            """, (document_id, student_id))
            
            doc = cur.fetchone()
            if not doc:
                cur.close()
                return {'success': False, 'error': 'Access denied'}
            
            # Record download
            cur.execute("""
                INSERT INTO document_downloads (document_id, student_id)
                VALUES (%s, %s)
            """, (document_id, student_id))
            
            # Update download count
            cur.execute("""
                UPDATE documents SET download_count = download_count + 1 
                WHERE id = %s
            """, (document_id,))
            
            self.db.commit()
            cur.close()
            
            return {'success': True, 'file_path': doc['file_path']}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def update_document_version(self, document_id, new_file, teacher_id):
        """Create a new version of a document"""
        try:
            if not self.allowed_file(new_file.filename):
                return {'success': False, 'error': 'File type not allowed'}
            
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            # Get current document
            cur.execute("SELECT * FROM documents WHERE id = %s", (document_id,))
            doc = cur.fetchone()
            
            if not doc:
                cur.close()
                return {'success': False, 'error': 'Document not found'}
            
            # Save new file
            filename = secure_filename(new_file.filename)
            file_ext = filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{datetime.now().timestamp()}_{filename}"
            file_path = os.path.join(self.upload_folder, unique_filename)
            
            new_file.save(file_path)
            file_size = os.path.getsize(file_path)
            new_version = doc['version'] + 1
            
            # Create version record
            cur.execute("""
                INSERT INTO document_versions (document_id, version, file_path, uploaded_by)
                VALUES (%s, %s, %s, %s)
            """, (document_id, new_version, file_path, teacher_id))
            
            # Update main document
            cur.execute("""
                UPDATE documents 
                SET filename = %s, file_path = %s, file_size = %s, 
                    file_type = %s, version = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (filename, file_path, file_size, file_ext, new_version, document_id))
            
            self.db.commit()
            cur.close()
            
            return {'success': True, 'new_version': new_version}
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_document_versions(self, document_id):
        """Get all versions of a document"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                SELECT dv.id, dv.version, dv.uploaded_by, dv.uploaded_at
                FROM document_versions dv
                WHERE dv.document_id = %s
                ORDER BY dv.version DESC
            """, (document_id,))
            
            versions = cur.fetchall()
            cur.close()
            
            return {'success': True, 'versions': [dict(v) for v in versions]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_document_stats(self, document_id):
        """Get document statistics"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                SELECT d.id, d.title, d.filename, d.file_size, d.download_count, 
                    d.created_at, d.updated_at, COUNT(da.student_id) as access_count
                FROM documents d
                LEFT JOIN document_access da ON d.id = da.document_id
                WHERE d.id = %s
                GROUP BY d.id
            """, (document_id,))
            
            stats = cur.fetchone()
            cur.close()
            
            if stats:
                return {'success': True, 'stats': dict(stats)}
            return {'success': False, 'error': 'Document not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def search_documents(self, query, user_id, document_type=None):
        """Search documents"""
        try:
            cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            
            search_pattern = f"%{query}%"
            
            sql = """
                SELECT d.id, d.title, d.filename, d.document_type, d.subject, 
                    d.academic_level, d.file_size, d.created_at
                FROM documents d
                LEFT JOIN document_access da ON d.id = da.document_id
                WHERE (d.is_public = 1 OR da.student_id = %s)
                AND (d.title ILIKE %s OR d.filename ILIKE %s OR d.description ILIKE %s)
            """
            params = [user_id, search_pattern, search_pattern, search_pattern]
            
            if document_type:
                sql += " AND d.document_type = %s"
                params.append(document_type)
            
            sql += " ORDER BY d.created_at DESC LIMIT 50"
            
            cur.execute(sql, params)
            results = cur.fetchall()
            cur.close()
            
            return {'success': True, 'results': [dict(r) for r in results]}
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Initialize service
document_service = None

def init_document_service(db_connection):
    global document_service
    document_service = DocumentService(db_connection)
    return document_service
