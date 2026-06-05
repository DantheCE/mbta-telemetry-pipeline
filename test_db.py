import os
import psycopg2

dsn = os.getenv('DB_DSN', 'postgresql://postgres.fzarqlqpltusfackdqdo:QA88z4JDVUEELAsk@aws-1-us-east-1.pooler.supabase.com:6543/postgres')
conn = psycopg2.connect(dsn)
with conn.cursor() as cur:
    cur.execute('SELECT NOW(), MAX(created_at), (NOW() - MAX(created_at)), (NOW() - MAX(created_at)) < INTERVAL ''5 minutes'' FROM vehicle_positions;')
    res = cur.fetchone()
    print('NOW():', res[0])
    print('MAX(created_at):', res[1])
    print('Difference:', res[2])
    print('Is Healthy (< 5m):', res[3])
conn.close()
