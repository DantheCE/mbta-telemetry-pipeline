import os
import urllib.parse
import psycopg2

DB_DSN = os.getenv("DB_DSN")

def get_db_connection(dsn: str = None):
    if dsn is None:
        dsn = DB_DSN
        
    if not dsn:
        raise ValueError("DB_DSN is empty or not provided")
        
    dsn = dsn.strip().strip('\'"').strip()
    if dsn.startswith("jdbc:"):
        dsn = dsn[5:]
        
    if dsn.startswith("postgres://") or dsn.startswith("postgresql://"):
        scheme, rest = dsn.split("://", 1)
        if "/" in rest:
            auth_host, dbname = rest.rsplit("/", 1)
        else:
            auth_host, dbname = rest, ""
            
        if "@" in auth_host:
            auth, host_port = auth_host.rsplit("@", 1)
        else:
            auth, host_port = "", auth_host
            
        user_pass = auth.split(":", 1)
        user = user_pass[0] if len(user_pass) > 0 else ""
        password = user_pass[1] if len(user_pass) > 1 else ""
        
        host_port_split = host_port.split(":", 1)
        host = host_port_split[0] if len(host_port_split) > 0 else ""
        port = host_port_split[1] if len(host_port_split) > 1 else ""
        
        return psycopg2.connect(
            dbname=dbname,
            user=urllib.parse.unquote(user),
            password=urllib.parse.unquote(password),
            host=host,
            port=port
        )
    return psycopg2.connect(dsn)
