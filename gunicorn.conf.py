# Configuração do Gunicorn para produção no Render

import os

# Bind
bind = f"0.0.0.0:{os.environ.get('PORT', 10000)}"

# Workers
workers = 2
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000

# Timeouts
timeout = 120
keepalive = 5

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Process naming
proc_name = "firebird-api"

# Preload app
preload_app = True

# Max requests per worker
max_requests = 1000
max_requests_jitter = 100