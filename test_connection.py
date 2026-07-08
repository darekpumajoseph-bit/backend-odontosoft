# test_connection.py
import psycopg2

print("=== Probando conexión a PostgreSQL ===\n")

try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="ProyectoApi",  # ← Cambiado a ProyectoApi
        user="postgres",
        password="123456"
    )
    print("✅ Conexión exitosa a PostgreSQL")
    print("✅ Base de datos: ProyectoApi")
    
    # Verificar las tablas existentes
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    
    print("\n📋 Tablas encontradas en ProyectoApi:")
    for table in tables:
        print(f"   - {table[0]}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nPosibles soluciones:")
    print("1. Asegúrate que PostgreSQL esté corriendo")
    print("2. Verifica que la contraseña sea '123456'")
    print("3. Verifica que la base de datos 'ProyectoApi' exista")