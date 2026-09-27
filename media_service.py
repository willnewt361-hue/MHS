"""
Advanced Features Service - 3D Visualization, Text Scanner/OCR, Videos, Past Papers, Offline Sync
Handles: 3D models, video management, OCR scanning, past papers, offline content sync
"""

import os
import json
import mimetypes
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, BinaryIO
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
import base64

logger = logging.getLogger(__name__)


class MediaService:
    def __init__(self, db_connection_string: str, storage_path: str = "./media_storage"):
        self.db_conn_string = db_connection_string
        self.storage_path = storage_path
        self.supported_3d_formats = ['.gltf', '.glb', '.obj', '.fbx', '.usdz']
        self.supported_video_formats = ['.mp4', '.webm', '.mov', '.mkv', '.avi']
        self.supported_image_formats = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']
        self.max_file_size = 500 * 1024 * 1024  # 500MB
        
        # Create storage directories
        os.makedirs(f"{storage_path}/3d_models", exist_ok=True)
        os.makedirs(f"{storage_path}/videos", exist_ok=True)
        os.makedirs(f"{storage_path}/transcripts", exist_ok=True)
        os.makedirs(f"{storage_path}/scanned_docs", exist_ok=True)
        os.makedirs(f"{storage_path}/past_papers", exist_ok=True)

    def _get_connection(self):
        """Get database connection"""
        try:
            conn = psycopg2.connect(self.db_conn_string)
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            return None

    # ==================== 3D MODEL MANAGEMENT ====================
    def upload_3d_model(self, model_file: BinaryIO, model_name: str, 
                       uploaded_by: str, subject: str = "") -> Dict[str, Any]:
        """
        Upload a 3D model file
        
        Args:
            model_file: File object to upload
            model_name: Name of the model
            uploaded_by: User ID uploading
            subject: Subject/topic of the model
            
        Returns:
            {'success': bool, 'model_id': str, 'error': str}
        """
        try:
            # Validate file format
            file_ext = os.path.splitext(model_file.filename)[1].lower()
            if file_ext not in self.supported_3d_formats:
                return {'success': False, 'error': f'Unsupported format. Allowed: {self.supported_3d_formats}'}
            
            # Get file size
            model_file.seek(0, 2)
            file_size = model_file.tell()
            model_file.seek(0)
            
            if file_size > self.max_file_size:
                return {'success': False, 'error': f'File too large. Max: {self.max_file_size / 1024 / 1024}MB'}
            
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            # Generate unique model ID
            model_hash = hashlib.sha256(f"{model_name}{uploaded_by}{datetime.utcnow().isoformat()}".encode()).hexdigest()[:8]
            model_id = f"3dm_{model_hash}"
            
            # Save file
            file_path = f"{self.storage_path}/3d_models/{model_id}{file_ext}"
            with open(file_path, 'wb') as f:
                f.write(model_file.read())
            
            # Generate thumbnail (simplified - just store reference)
            thumbnail_path = f"3d_models/{model_id}_thumb.jpg"
            
            # Store in database
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO three_d_models (model_id, model_name, file_path, file_size,
                                      uploaded_by, subject, thumbnail_path, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (model_id, model_name, f"3d_models/{model_id}{file_ext}", 
                 file_size, uploaded_by, subject, thumbnail_path, datetime.utcnow()))
            
            conn.commit()
            
            return {
                'success': True,
                'model_id': model_id,
                'file_size': file_size,
                'uploaded_at': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"3D model upload error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def get_3d_models(self, subject: str = "", limit: int = 20) -> Dict[str, Any]:
        """Get available 3D models"""
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            query = "SELECT * FROM three_d_models WHERE is_deleted = false"
            params = []
            
            if subject:
                query += " AND subject ILIKE %s"
                params.append(f"%{subject}%")
            
            query += " ORDER BY created_at DESC LIMIT %s"
            params.append(limit)
            
            cur.execute(query, params)
            models = cur.fetchall()
            
            return {
                'success': True,
                'models': [dict(m) for m in models],
                'total': len(models)
            }
        
        except Exception as e:
            logger.error(f"3D models retrieval error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def record_3d_model_view(self, model_id: str, viewer_id: str) -> Dict[str, Any]:
        """Record a 3D model view"""
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO three_d_model_views (model_id, viewer_id, viewed_at)
                VALUES (%s, %s, %s)
            """, (model_id, viewer_id, datetime.utcnow()))
            
            # Increment view count
            cur.execute("""
                UPDATE three_d_models SET view_count = view_count + 1
                WHERE model_id = %s
            """, (model_id,))
            
            conn.commit()
            return {'success': True}
        
        except Exception as e:
            logger.error(f"View recording error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    # ==================== VIDEO MANAGEMENT ====================
    def upload_video(self, video_file: BinaryIO, video_title: str, 
                    uploaded_by: str, subject: str = "", quality_levels: List[str] = None) -> Dict[str, Any]:
        """
        Upload a video file
        
        Args:
            video_file: File object
            video_title: Video title
            uploaded_by: User ID
            subject: Subject area
            quality_levels: ['360p', '480p', '720p', '1080p'] to transcode
            
        Returns:
            {'success': bool, 'video_id': str, 'error': str}
        """
        try:
            if not quality_levels:
                quality_levels = ['720p']
            
            # Validate format
            file_ext = os.path.splitext(video_file.filename)[1].lower()
            if file_ext not in self.supported_video_formats:
                return {'success': False, 'error': f'Unsupported format. Allowed: {self.supported_video_formats}'}
            
            # Check file size
            video_file.seek(0, 2)
            file_size = video_file.tell()
            video_file.seek(0)
            
            if file_size > self.max_file_size:
                return {'success': False, 'error': f'File too large. Max: {self.max_file_size / 1024 / 1024}MB'}
            
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            # Generate unique video ID
            video_hash = hashlib.sha256(f"{video_title}{uploaded_by}{datetime.utcnow().isoformat()}".encode()).hexdigest()[:8]
            video_id = f"vid_{video_hash}"
            
            # Save original file
            file_path = f"{self.storage_path}/videos/{video_id}_original{file_ext}"
            with open(file_path, 'wb') as f:
                f.write(video_file.read())
            
            # Store in database
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO videos (video_id, video_title, original_file_path, 
                                   uploaded_by, subject, quality_levels, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (video_id, video_title, f"videos/{video_id}_original{file_ext}",
                 uploaded_by, subject, json.dumps(quality_levels), datetime.utcnow()))
            
            conn.commit()
            
            return {
                'success': True,
                'video_id': video_id,
                'file_size': file_size,
                'quality_levels': quality_levels,
                'uploaded_at': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Video upload error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def add_video_transcript(self, video_id: str, transcript_text: str,
                            auto_generated: bool = False) -> Dict[str, Any]:
        """Add or update video transcript"""
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO video_transcripts (video_id, transcript_text, auto_generated, created_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (video_id) DO UPDATE SET
                    transcript_text = EXCLUDED.transcript_text,
                    auto_generated = EXCLUDED.auto_generated
            """, (video_id, transcript_text, auto_generated, datetime.utcnow()))
            
            conn.commit()
            return {'success': True}
        
        except Exception as e:
            logger.error(f"Transcript error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def record_video_view(self, video_id: str, viewer_id: str, 
                         duration_watched_seconds: int = 0) -> Dict[str, Any]:
        """Record video view and watch progress"""
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO video_views (video_id, viewer_id, duration_watched_seconds, viewed_at)
                VALUES (%s, %s, %s, %s)
            """, (video_id, viewer_id, duration_watched_seconds, datetime.utcnow()))
            
            # Update view count
            cur.execute("""
                UPDATE videos SET view_count = view_count + 1
                WHERE video_id = %s
            """, (video_id,))
            
            conn.commit()
            return {'success': True}
        
        except Exception as e:
            logger.error(f"View recording error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    # ==================== TEXT SCANNING & OCR ====================
    def scan_document_ocr(self, image_file: BinaryIO, document_name: str,
                         uploaded_by: str, language: str = "eng", 
                         use_premium: bool = False) -> Dict[str, Any]:
        """
        Scan document using OCR
        
        Args:
            image_file: Image file to scan
            document_name: Name for the scanned doc
            uploaded_by: User ID
            language: Language for OCR (eng, fre, spa, ara, swa, etc.)
            use_premium: Use premium OCR with formula/image recognition
            
        Returns:
            {'success': bool, 'scan_id': str, 'text': str, 'error': str}
        """
        try:
            # Validate image format
            file_ext = os.path.splitext(image_file.filename)[1].lower()
            if file_ext not in self.supported_image_formats:
                return {'success': False, 'error': f'Unsupported format. Allowed: {self.supported_image_formats}'}
            
            # Check file size
            image_file.seek(0, 2)
            file_size = image_file.tell()
            image_file.seek(0)
            
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            # Generate scan ID
            scan_hash = hashlib.sha256(f"{document_name}{uploaded_by}{datetime.utcnow().isoformat()}".encode()).hexdigest()[:8]
            scan_id = f"scan_{scan_hash}"
            
            # Save image
            file_path = f"{self.storage_path}/scanned_docs/{scan_id}_original{file_ext}"
            with open(file_path, 'wb') as f:
                f.write(image_file.read())
            
            # Perform OCR (basic implementation - would use Tesseract or cloud API)
            extracted_text = self._perform_ocr(file_path, language, use_premium)
            
            if not extracted_text:
                extracted_text = "[OCR Processing Failed - Please retry]"
            
            # Store scan record
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO scanned_documents (scan_id, document_name, image_path,
                                             extracted_text, uploaded_by, language,
                                             use_premium_ocr, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (scan_id, document_name, f"scanned_docs/{scan_id}_original{file_ext}",
                 extracted_text, uploaded_by, language, use_premium, datetime.utcnow()))
            
            conn.commit()
            
            return {
                'success': True,
                'scan_id': scan_id,
                'text': extracted_text[:500],  # Return first 500 chars
                'full_text_available': True,
                'scanned_at': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"OCR scan error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def _perform_ocr(self, image_path: str, language: str, use_premium: bool) -> str:
        """
        Perform OCR on image
        
        Implementation options:
        - Tesseract (local, free)
        - Cloud Vision APIs (Google, Azure)
        """
        try:
            try:
                # Try Tesseract first (local)
                import pytesseract
                from PIL import Image
                
                img = Image.open(image_path)
                text = pytesseract.image_to_string(img, lang=language)
                return text if text.strip() else None
            except ImportError:
                logger.warning("Tesseract not available, falling back to cloud API")
            
            # Try Google Vision (if credentials available)
            try:
                from google.cloud import vision
                client = vision.ImageAnnotatorClient()
                
                with open(image_path, 'rb') as f:
                    image = vision.Image(content=f.read())
                
                response = client.document_text_detection(image=image)
                full_text = response.full_text_annotation.text
                return full_text if full_text.strip() else None
            except Exception as e:
                logger.warning(f"Google Vision failed: {str(e)}")
            
            # Return placeholder if all fail
            return "[OCR services unavailable]"
        
        except Exception as e:
            logger.error(f"OCR error: {str(e)}")
            return None

    def export_scanned_document(self, scan_id: str, export_format: str = "pdf") -> Dict[str, Any]:
        """
        Export scanned document to different formats
        
        Args:
            scan_id: ID of scanned document
            export_format: 'pdf', 'docx', 'txt', 'xlsx'
            
        Returns:
            {'success': bool, 'file_path': str, 'error': str}
        """
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT extracted_text, document_name FROM scanned_documents
                WHERE scan_id = %s
            """, (scan_id,))
            
            doc = cur.fetchone()
            if not doc:
                return {'success': False, 'error': 'Scan not found'}
            
            # Export based on format
            if export_format.lower() == 'txt':
                export_path = f"{self.storage_path}/scanned_docs/{scan_id}_export.txt"
                with open(export_path, 'w') as f:
                    f.write(doc['extracted_text'])
            
            elif export_format.lower() == 'pdf':
                try:
                    from reportlab.lib.pagesizes import letter
                    from reportlab.pdfgen import canvas
                    
                    export_path = f"{self.storage_path}/scanned_docs/{scan_id}_export.pdf"
                    c = canvas.Canvas(export_path, pagesize=letter)
                    text_lines = doc['extracted_text'].split('\n')
                    
                    y = 750
                    for line in text_lines:
                        c.drawString(50, y, line[:80])
                        y -= 20
                        if y < 50:
                            c.showPage()
                            y = 750
                    
                    c.save()
                except ImportError:
                    return {'success': False, 'error': 'PDF export not available'}
            
            elif export_format.lower() == 'docx':
                try:
                    from docx import Document
                    
                    export_path = f"{self.storage_path}/scanned_docs/{scan_id}_export.docx"
                    doc_obj = Document()
                    doc_obj.add_heading(doc['document_name'], 0)
                    doc_obj.add_paragraph(doc['extracted_text'])
                    doc_obj.save(export_path)
                except ImportError:
                    return {'success': False, 'error': 'DOCX export not available'}
            
            else:
                return {'success': False, 'error': f'Unsupported format: {export_format}'}
            
            return {
                'success': True,
                'file_path': export_path,
                'format': export_format
            }
        
        except Exception as e:
            logger.error(f"Export error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    # ==================== PAST PAPERS REPOSITORY ====================
    def upload_past_paper(self, paper_file: BinaryIO, paper_name: str,
                         uploaded_by: str, subject: str, exam_year: int,
                         exam_type: str = "final") -> Dict[str, Any]:
        """
        Upload a past exam paper
        
        Args:
            paper_file: PDF/Word document
            paper_name: Name of paper
            uploaded_by: User ID
            subject: Subject area
            exam_year: Year of exam
            exam_type: 'midterm', 'final', 'practice', 'mock'
            
        Returns:
            {'success': bool, 'paper_id': str, 'error': str}
        """
        try:
            file_ext = os.path.splitext(paper_file.filename)[1].lower()
            if file_ext not in ['.pdf', '.docx', '.doc', '.txt']:
                return {'success': False, 'error': 'Only PDF, Word, or Text files allowed'}
            
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            # Generate paper ID
            paper_hash = hashlib.sha256(f"{paper_name}{uploaded_by}{datetime.utcnow().isoformat()}".encode()).hexdigest()[:8]
            paper_id = f"paper_{paper_hash}"
            
            # Save file
            file_path = f"{self.storage_path}/past_papers/{paper_id}{file_ext}"
            with open(file_path, 'wb') as f:
                f.write(paper_file.read())
            
            # Store in database
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO past_papers (paper_id, paper_name, file_path,
                                        subject, exam_year, exam_type, uploaded_by,
                                        created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (paper_id, paper_name, f"past_papers/{paper_id}{file_ext}",
                 subject, exam_year, exam_type, uploaded_by, datetime.utcnow()))
            
            conn.commit()
            
            return {
                'success': True,
                'paper_id': paper_id,
                'uploaded_at': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Paper upload error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def get_past_papers(self, subject: str = "", exam_year: int = None,
                       limit: int = 20) -> Dict[str, Any]:
        """Get available past papers"""
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            query = "SELECT * FROM past_papers WHERE is_deleted = false"
            params = []
            
            if subject:
                query += " AND subject ILIKE %s"
                params.append(f"%{subject}%")
            
            if exam_year:
                query += " AND exam_year = %s"
                params.append(exam_year)
            
            query += " ORDER BY exam_year DESC LIMIT %s"
            params.append(limit)
            
            cur.execute(query, params)
            papers = cur.fetchall()
            
            return {
                'success': True,
                'papers': [dict(p) for p in papers],
                'total': len(papers)
            }
        
        except Exception as e:
            logger.error(f"Papers retrieval error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    # ==================== OFFLINE SYNC ====================
    def queue_for_offline_sync(self, student_id: str, content_type: str,
                              content_id: str) -> Dict[str, Any]:
        """
        Queue content for offline download/sync
        
        Args:
            student_id: Student ID
            content_type: 'document', 'video', 'audio', 'paper'
            content_id: ID of the content
            
        Returns:
            {'success': bool, 'sync_id': str, 'error': str}
        """
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            sync_hash = hashlib.sha256(f"{student_id}{content_type}{content_id}{datetime.utcnow().isoformat()}".encode()).hexdigest()[:8]
            sync_id = f"sync_{sync_hash}"
            
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO offline_sync_queue (sync_id, student_id, content_type,
                                              content_id, status, queued_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (sync_id, student_id, content_type, content_id, 'queued', datetime.utcnow()))
            
            conn.commit()
            
            return {
                'success': True,
                'sync_id': sync_id,
                'status': 'queued',
                'queued_at': datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Offline sync error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def get_sync_status(self, student_id: str) -> Dict[str, Any]:
        """Get offline sync status for a student"""
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT sync_id, content_type, content_id, status, queued_at,
                       synced_at, error_message
                FROM offline_sync_queue
                WHERE student_id = %s
                ORDER BY queued_at DESC
                LIMIT 50
            """, (student_id,))
            
            syncs = cur.fetchall()
            
            # Calculate stats
            pending = sum(1 for s in syncs if s['status'] == 'queued')
            synced = sum(1 for s in syncs if s['status'] == 'synced')
            failed = sum(1 for s in syncs if s['status'] == 'failed')
            
            return {
                'success': True,
                'syncs': [dict(s) for s in syncs],
                'stats': {
                    'pending': pending,
                    'synced': synced,
                    'failed': failed,
                    'total': len(syncs)
                }
            }
        
        except Exception as e:
            logger.error(f"Sync status error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()

    def process_offline_syncs(self, batch_size: int = 10) -> Dict[str, Any]:
        """
        Process pending offline syncs (called by background job)
        
        Returns:
            {'success': bool, 'processed': int, 'failed': int, 'error': str}
        """
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get pending syncs
            cur.execute("""
                SELECT sync_id, student_id, content_type, content_id
                FROM offline_sync_queue
                WHERE status = 'queued'
                ORDER BY queued_at ASC
                LIMIT %s
            """, (batch_size,))
            
            pending_syncs = cur.fetchall()
            processed = 0
            failed = 0
            
            for sync in pending_syncs:
                try:
                    # Download/sync content based on type
                    # In production, this would actually download the files
                    
                    cur.execute("""
                        UPDATE offline_sync_queue
                        SET status = 'synced', synced_at = %s
                        WHERE sync_id = %s
                    """, (datetime.utcnow(), sync['sync_id']))
                    
                    processed += 1
                
                except Exception as e:
                    cur.execute("""
                        UPDATE offline_sync_queue
                        SET status = 'failed', error_message = %s
                        WHERE sync_id = %s
                    """, (str(e), sync['sync_id']))
                    
                    failed += 1
            
            conn.commit()
            
            return {
                'success': True,
                'processed': processed,
                'failed': failed
            }
        
        except Exception as e:
            logger.error(f"Sync processing error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()
