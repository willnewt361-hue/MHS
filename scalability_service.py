"""
Phase 14: Scalability & Performance Optimization
Redis caching, database optimization, load balancing setup
"""

import logging
import json
import time
from typing import Dict, Any, Optional, List, Any as GenericType
from functools import wraps
import redis
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based caching service for scalability"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0", 
                 default_ttl: int = 3600):
        """
        Initialize cache service
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default time-to-live in seconds (1 hour)
        """
        try:
            self.redis_client = redis.from_url(redis_url)
            self.default_ttl = default_ttl
            self.redis_client.ping()
            logger.info("✅ Redis connected successfully")
        except Exception as e:
            logger.error(f"Redis connection failed: {str(e)}")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[GenericType]:
        """Get value from cache"""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None
    
    def set(self, key: str, value: GenericType, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        if not self.redis_client:
            return False
        
        try:
            ttl = ttl or self.default_ttl
            self.redis_client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False
    
    def flush_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache flush error: {str(e)}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Redis statistics"""
        if not self.redis_client:
            return {'success': False, 'error': 'Redis not connected'}
        
        try:
            info = self.redis_client.info()
            return {
                'success': True,
                'connected_clients': info.get('connected_clients'),
                'used_memory': info.get('used_memory_human'),
                'evicted_keys': info.get('evicted_keys'),
                'keyspace': info.get('db0', {})
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class PerformanceOptimizer:
    """Database and query optimization"""
    
    def __init__(self, db_connection_string: str):
        self.db_conn_string = db_connection_string
    
    def _get_connection(self):
        """Get database connection"""
        try:
            conn = psycopg2.connect(self.db_conn_string)
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            return None
    
    def analyze_slow_queries(self) -> Dict[str, Any]:
        """Analyze slow running queries"""
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get queries from pg_stat_statements (if available)
            cur.execute("""
                SELECT query, calls, total_time, mean_time, max_time
                FROM pg_stat_statements
                WHERE mean_time > 100  -- Queries taking >100ms
                ORDER BY mean_time DESC
                LIMIT 20
            """)
            
            slow_queries = cur.fetchall()
            
            return {
                'success': True,
                'slow_queries': [dict(q) for q in slow_queries]
            }
        
        except Exception as e:
            logger.warning(f"Slow query analysis error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics and health"""
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get table sizes
            cur.execute("""
                SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                FROM pg_tables
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                LIMIT 20
            """)
            
            table_sizes = [dict(t) for t in cur.fetchall()]
            
            # Get index statistics
            cur.execute("""
                SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
                FROM pg_stat_user_indexes
                ORDER BY idx_scan DESC
                LIMIT 20
            """)
            
            indexes = [dict(i) for i in cur.fetchall()]
            
            # Get connection count
            cur.execute("""
                SELECT count(*) as connection_count, max(query_start)::text as oldest_query
                FROM pg_stat_activity
                WHERE state = 'active'
            """)
            
            activity = cur.fetchone()
            
            return {
                'success': True,
                'tables': table_sizes,
                'indexes': indexes,
                'connections': activity['connection_count'] if activity else 0,
                'oldest_query': activity['oldest_query'] if activity else None
            }
        
        except Exception as e:
            logger.error(f"Database stats error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()
    
    def create_missing_indexes(self) -> Dict[str, Any]:
        """Create recommended indexes for performance"""
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            cur = conn.cursor()
            
            # Create indexes on frequently filtered columns
            indexes_to_create = [
                ("CREATE INDEX IF NOT EXISTS idx_exam_submissions_student ON exam_submissions(student_id)", "exam_submissions_student"),
                ("CREATE INDEX IF NOT EXISTS idx_exam_submissions_status ON exam_submissions(status)", "exam_submissions_status"),
                ("CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id)", "audit_logs_user"),
                ("CREATE INDEX IF NOT EXISTS idx_chat_messages_group ON chat_messages(group_id)", "chat_messages_group"),
                ("CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(created_at DESC)", "chat_messages_timestamp"),
                ("CREATE INDEX IF NOT EXISTS idx_documents_student ON document_access(student_id)", "document_access_student"),
                ("CREATE INDEX IF NOT EXISTS idx_payments_student ON transactions(student_id)", "payments_student"),
                ("CREATE INDEX IF NOT EXISTS idx_badges_student ON awarded_badges(student_id)", "badges_student"),
            ]
            
            created = []
            for index_sql, index_name in indexes_to_create:
                try:
                    cur.execute(index_sql)
                    created.append(index_name)
                except Exception as e:
                    logger.warning(f"Index creation warning: {str(e)}")
            
            conn.commit()
            
            return {'success': True, 'indexes_created': created}
        
        except Exception as e:
            logger.error(f"Index creation error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()
    
    def vacuum_database(self) -> Dict[str, Any]:
        """Run VACUUM ANALYZE to optimize database"""
        try:
            conn = self._get_connection()
            if not conn:
                return {'success': False, 'error': 'Database connection failed'}
            
            conn.autocommit = True
            cur = conn.cursor()
            
            # VACUUM ANALYZE to reclaim space and update statistics
            cur.execute("VACUUM ANALYZE")
            
            return {'success': True, 'message': 'Database optimized'}
        
        except Exception as e:
            logger.error(f"VACUUM error: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if conn:
                conn.close()


def cached(ttl: int = 3600, cache_service: Optional[CacheService] = None):
    """
    Decorator for caching function results
    
    Usage:
        @cached(ttl=1800)
        def get_student_performance(student_id):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not cache_service:
                return func(*args, **kwargs)
            
            # Generate cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached_value = cache_service.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


class LoadBalancerConfig:
    """Configuration for load balancing setup"""
    
    @staticmethod
    def get_nginx_config() -> str:
        """Generate Nginx load balancer configuration"""
        return """
# Nginx Load Balancer Configuration
# Save as /etc/nginx/sites-available/mengo-hub

upstream mengo_hub_backend {
    # Health check enabled
    server localhost:5000 max_fails=3 fail_timeout=30s;
    server localhost:5001 max_fails=3 fail_timeout=30s;
    server localhost:5002 max_fails=3 fail_timeout=30s;
    server localhost:5003 max_fails=3 fail_timeout=30s;
    
    # Keep alive connections
    keepalive 32;
}

server {
    listen 80;
    server_name mengo-hub.com www.mengo-hub.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name mengo-hub.com www.mengo-hub.com;
    
    # SSL configuration
    ssl_certificate /etc/ssl/certs/mengo-hub.crt;
    ssl_certificate_key /etc/ssl/private/mengo-hub.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
    
    location / {
        proxy_pass http://mengo_hub_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /socket.io {
        proxy_pass http://mengo_hub_backend/socket.io;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Cache static files
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://mengo_hub_backend;
        expires 30d;
        proxy_cache_valid 200 30d;
    }
}
"""
    
    @staticmethod
    def get_gunicorn_config() -> str:
        """Generate Gunicorn configuration for production"""
        return """
# Gunicorn Configuration
# Save as gunicorn_config.py

bind = "0.0.0.0:5000"
workers = 4
worker_class = "eventlet"
worker_connections = 1000
timeout = 60
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
preload_app = False
daemon = False
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
"""


class PerformanceMonitor:
    """Monitor system performance metrics"""
    
    @staticmethod
    def get_performance_report(cache_service: CacheService,
                              performance_optimizer: PerformanceOptimizer) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        
        return {
            'cache': cache_service.get_stats(),
            'database': performance_optimizer.get_database_stats(),
            'slow_queries': performance_optimizer.analyze_slow_queries(),
            'timestamp': time.time()
        }
