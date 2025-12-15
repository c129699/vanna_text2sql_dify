"""
Gunicorn 配置文件
用于生产环境部署
"""
import multiprocessing
import os

# 修复 tokenizers 并行性警告
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')

# 服务器配置
bind = os.environ.get('GUNICORN_BIND', '0.0.0.0:2523')
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = os.environ.get('GUNICORN_WORKER_CLASS', 'sync')
worker_connections = int(os.environ.get('GUNICORN_WORKER_CONNECTIONS', '1000'))
timeout = int(os.environ.get('GUNICORN_TIMEOUT', '120'))
keepalive = int(os.environ.get('GUNICORN_KEEPALIVE', '5'))

# 日志配置
accesslog = os.environ.get('GUNICORN_ACCESS_LOG', '-')  # '-' 表示输出到 stdout
errorlog = os.environ.get('GUNICORN_ERROR_LOG', '-')    # '-' 表示输出到 stderr
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程配置
daemon = False
pidfile = os.environ.get('GUNICORN_PIDFILE', None)
umask = 0
user = os.environ.get('GUNICORN_USER', None)
group = os.environ.get('GUNICORN_GROUP', None)
tmp_upload_dir = None

# 性能优化
preload_app = True  # 预加载应用，减少内存使用
max_requests = int(os.environ.get('GUNICORN_MAX_REQUESTS', '1000'))  # 每个 worker 处理请求数上限
max_requests_jitter = int(os.environ.get('GUNICORN_MAX_REQUESTS_JITTER', '50'))  # 随机抖动，避免同时重启

# 安全配置
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# 其他配置
proc_name = os.environ.get('GUNICORN_PROC_NAME', 'vanna_text2sql')
forwarded_allow_ips = '*'  # 允许的代理 IP，生产环境建议设置为具体 IP

