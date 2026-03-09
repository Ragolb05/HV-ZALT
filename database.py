import sqlite3
from datetime import datetime
import hashlib

# Nombre del archivo de base de datos
DB_NAME = 'inventario_it.db'

def create_connection():
    """Establece una conexión con la base de datos SQLite."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Crea las tablas relacionales para el sistema versionado con auditoría."""
    conn = create_connection()
    cursor = conn.cursor()
    
    # Tabla 1: Usuarios Técnicos (Profesionales que pueden firmar)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios_tecnicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            documento TEXT UNIQUE NOT NULL,
            cargo TEXT NOT NULL,
            email TEXT,
            activo INTEGER DEFAULT 1,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabla 2: Hoja de Vida (Versionada - permite histórico)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hojas_vida (
            id_version INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_equipo TEXT NOT NULL,
            version_numero INTEGER NOT NULL,
            nombre_usuario TEXT NOT NULL,
            cc TEXT,
            cargo TEXT,
            area TEXT,
            ciudad TEXT,
            correo_usuario TEXT,
            fecha_asignacion TEXT,
            sistema_operativo TEXT,
            arquitectura TEXT,
            software_ofimatica TEXT,
            v_office TEXT,
            md_duro TEXT,
            cd_duro TEXT,
            m_ram TEXT,
            c_ram TEXT,
            t_procesador TEXT,
            user_red TEXT,
            dir_ip TEXT,
            anti TEXT,
            v_anti TEXT,
            apps TEXT,
            obs TEXT,
            tipo_asignacion TEXT DEFAULT 'permanente',
            estado TEXT DEFAULT 'activo',
            id_tecnico_responsable INTEGER,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_tecnico_responsable) REFERENCES usuarios_tecnicos(id),
            UNIQUE(nombre_equipo, version_numero)
        )
    """)

    # Tabla 3: Detalle de Hardware (Mejorada con timestamp)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_hardware (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_version INTEGER NOT NULL,
            nombre_equipo TEXT NOT NULL,
            tipo_equipo TEXT,
            elemento TEXT,
            marca TEXT,
            modelo TEXT,
            serial TEXT,
            fecha_instalacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            id_tecnico_instalacion INTEGER,
            FOREIGN KEY (id_version) REFERENCES hojas_vida(id_version),
            FOREIGN KEY (id_tecnico_instalacion) REFERENCES usuarios_tecnicos(id)
        )
    """)

    # Tabla 4: Historial de Cambios (AUDITORÍA COMPLETA)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_cambios (
            id_cambio INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_equipo TEXT NOT NULL,
            tipo_cambio TEXT NOT NULL,
            campo_modificado TEXT,
            valor_anterior TEXT,
            valor_nuevo TEXT,
            fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            id_tecnico INTEGER,
            id_version_anterior INTEGER,
            id_version_nueva INTEGER,
            notas TEXT,
            FOREIGN KEY (id_tecnico) REFERENCES usuarios_tecnicos(id),
            FOREIGN KEY (id_version_anterior) REFERENCES hojas_vida(id_version),
            FOREIGN KEY (id_version_nueva) REFERENCES hojas_vida(id_version)
        )
    """)

    # Tabla 5: Firmas Digitales (SEGURIDAD)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS firmas_digitales (
            id_firma INTEGER PRIMARY KEY AUTOINCREMENT,
            id_version INTEGER NOT NULL,
            nombre_equipo TEXT NOT NULL,
            tipo_firma TEXT NOT NULL,
            nombre_firmante TEXT NOT NULL,
            documento_firmante TEXT NOT NULL,
            fecha_firma TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            consentimiento_recibido INTEGER DEFAULT 0,
            responsabilidad_aceptada INTEGER DEFAULT 0,
            hash_firma TEXT,
            pin_verificacion TEXT,
            ip_dispositivo TEXT,
            navegador TEXT,
            email_confirmacion_enviado INTEGER DEFAULT 0,
            codigo_verificacion TEXT,
            FOREIGN KEY (id_version) REFERENCES hojas_vida(id_version)
        )
    """)

    conn.commit()
    conn.close()

# ==================== FUNCIONES DE VALIDACIÓN ====================

def validar_correo(correo):
    """Valida formato básico de correo."""
    if not correo:
        return True  # Opcional
    return '@' in correo and '.' in correo.split('@')[1] if '@' in correo else False

def validar_documento(doc):
    """Valida que sea número y tenga longitud válida."""
    if not doc:
        return False
    return doc.isdigit() and 6 <= len(doc) <= 20

def validar_ip(ip):
    """Valida formato IPv4."""
    if not ip:
        return True  # Opcional
    partes = ip.split('.')
    if len(partes) != 4:
        return False
    return all(x.isdigit() and 0 <= int(x) <= 255 for x in partes)

def validar_serial(serial):
    """Valida que serial no esté vacío."""
    return bool(serial.strip())

# ==================== FUNCIONES DE LECTURA/ESCRITURA ====================

def insert_hoja_completa(cabecera, lista_hardware, id_tecnico=None):
    """Inserta una nueva hoja de vida (versión 1) con auditoría."""
    conn = create_connection()
    cursor = conn.cursor()
    try:
        # Obtener siguiente versión para este equipo
        cursor.execute("SELECT MAX(version_numero) FROM hojas_vida WHERE nombre_equipo = ?", 
                      (cabecera['nombre_equipo'],))
        result = cursor.fetchone()
        version_numero = 1 if result[0] is None else result[0] + 1
        
        # Insertar en hojas_vida
        columnas = list(cabecera.keys()) + ['version_numero', 'id_tecnico_responsable']
        placeholders = ', '.join(['?'] * len(columnas))
        valores = list(cabecera.values()) + [version_numero, id_tecnico]
        
        query_h = f"INSERT INTO hojas_vida ({', '.join(columnas)}) VALUES ({placeholders})"
        cursor.execute(query_h, valores)
        id_version = cursor.lastrowid

        # Insertar elementos en detalle_hardware
        query_d = """
            INSERT INTO detalle_hardware (id_version, nombre_equipo, tipo_equipo, elemento, marca, modelo, serial)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        for item in lista_hardware:
            cursor.execute(query_d, (
                id_version,
                cabecera['nombre_equipo'],
                item.get('tipo', ''),
                item.get('elemento', ''),
                item.get('marca', ''),
                item.get('modelo', ''),
                item.get('serial', '')
            ))
        
        # Registrar en historial
        cursor.execute("""
            INSERT INTO historial_cambios 
            (nombre_equipo, tipo_cambio, id_tecnico, id_version_nueva)
            VALUES (?, ?, ?, ?)
        """, (cabecera['nombre_equipo'], 'nueva_asignacion', id_tecnico, id_version))
        
        conn.commit()
        return id_version
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def actualizar_hoja_vida(nombre_equipo, datos_nuevos, lista_hardware, id_tecnico=None):
    """Actualiza una hoja de vida creando nueva versión con auditoría."""
    conn = create_connection()
    cursor = conn.cursor()
    try:
        # Obtener versión actual
        cursor.execute("""
            SELECT * FROM hojas_vida 
            WHERE nombre_equipo = ? 
            ORDER BY version_numero DESC LIMIT 1
        """, (nombre_equipo,))
        version_actual = cursor.fetchone()
        
        if not version_actual:
            raise ValueError(f"Equipo {nombre_equipo} no existe")
        
        nuevo_numero_version = version_actual['version_numero'] + 1
        
        # Crear nueva versión con datos actualizados
        datos_nuevos['nombre_equipo'] = nombre_equipo
        datos_nuevos['version_numero'] = nuevo_numero_version
        datos_nuevos['id_tecnico_responsable'] = id_tecnico
        
        columnas = list(datos_nuevos.keys())
        placeholders = ', '.join(['?'] * len(columnas))
        valores = list(datos_nuevos.values())
        
        query = f"INSERT INTO hojas_vida ({', '.join(columnas)}) VALUES ({placeholders})"
        cursor.execute(query, valores)
        id_version_nueva = cursor.lastrowid

        # Insertar nuevo hardware
        query_d = """
            INSERT INTO detalle_hardware (id_version, nombre_equipo, tipo_equipo, elemento, marca, modelo, serial)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        for item in lista_hardware:
            cursor.execute(query_d, (
                id_version_nueva,
                nombre_equipo,
                item.get('tipo', ''),
                item.get('elemento', ''),
                item.get('marca', ''),
                item.get('modelo', ''),
                item.get('serial', '')
            ))
        
        # Registrar cambios en historial
        cursor.execute("""
            INSERT INTO historial_cambios 
            (nombre_equipo, tipo_cambio, id_tecnico, id_version_anterior, id_version_nueva)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre_equipo, 'actualizacion', id_tecnico, version_actual['id_version'], id_version_nueva))
        
        conn.commit()
        return id_version_nueva
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_hoja_vida_actual(nombre_equipo):
    """Obtiene la versión actual (más reciente) de una hoja de vida."""
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM hojas_vida 
        WHERE nombre_equipo = ? 
        ORDER BY version_numero DESC LIMIT 1
    """, (nombre_equipo,))
    cabecera = cursor.fetchone()
    
    if cabecera:
        cursor.execute("""
            SELECT * FROM detalle_hardware 
            WHERE id_version = ? 
            ORDER BY id ASC
        """, (cabecera['id_version'],))
        hardware = cursor.fetchall()
    else:
        hardware = []
    
    conn.close()
    return cabecera, hardware

def get_todas_hojas_actuales():
    """Obtiene la versión actual de TODAS las hojas de vida."""
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM hojas_vida hv
        WHERE id_version = (
            SELECT id_version FROM hojas_vida 
            WHERE nombre_equipo = hv.nombre_equipo 
            ORDER BY version_numero DESC LIMIT 1
        )
        ORDER BY nombre_equipo
    """)
    res = cursor.fetchall()
    conn.close()
    return res

def get_historial_cambios(nombre_equipo):
    """Obtiene el historial de cambios de un equipo."""
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT hc.*, ut.nombre as nombre_tecnico
        FROM historial_cambios hc
        LEFT JOIN usuarios_tecnicos ut ON hc.id_tecnico = ut.id
        WHERE hc.nombre_equipo = ?
        ORDER BY hc.fecha_cambio DESC
    """, (nombre_equipo,))
    res = cursor.fetchall()
    conn.close()
    return res

# ==================== FUNCIONES DE FIRMA DIGITAL ====================

def generar_hash_firma(nombre_firmante, documento, pin, timestamp):
    """Genera hash SHA256 para firma digital."""
    datos = f"{nombre_firmante}|{documento}|{pin}|{timestamp}"
    return hashlib.sha256(datos.encode()).hexdigest()

def guardar_firma_digital(id_version, nombre_equipo, tipo_firma, nombre_firmante, 
                         documento_firmante, consentimiento, responsabilidad, 
                         pin=None, ip_dispositivo=None, navegador=None):
    """Guarda firma digital con validaciones."""
    conn = create_connection()
    cursor = conn.cursor()
    try:
        timestamp = datetime.now().isoformat()
        hash_firma = generar_hash_firma(nombre_firmante, documento_firmante, pin or "", timestamp)
        
        cursor.execute("""
            INSERT INTO firmas_digitales 
            (id_version, nombre_equipo, tipo_firma, nombre_firmante, documento_firmante,
             consentimiento_recibido, responsabilidad_aceptada, hash_firma, 
             pin_verificacion, ip_dispositivo, navegador, fecha_firma)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_version, nombre_equipo, tipo_firma, nombre_firmante, documento_firmante,
              int(consentimiento), int(responsabilidad), hash_firma, pin, ip_dispositivo, navegador, timestamp))
        
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_firmas_equipo(nombre_equipo, id_version=None):
    """Obtiene las firmas de un equipo (versión específica o la última)."""
    conn = create_connection()
    cursor = conn.cursor()
    
    if id_version:
        cursor.execute("""
            SELECT * FROM firmas_digitales 
            WHERE nombre_equipo = ? AND id_version = ?
            ORDER BY fecha_firma DESC
        """, (nombre_equipo, id_version))
    else:
        cursor.execute("""
            SELECT * FROM firmas_digitales 
            WHERE nombre_equipo = ?
            ORDER BY fecha_firma DESC
        """, (nombre_equipo,))
    
    res = cursor.fetchall()
    conn.close()
    return res

# ==================== FUNCIONES DE USUARIOS TÉCNICOS ====================

def registrar_tecnico(nombre, documento, cargo, email=None):
    """Registra un nuevo usuario técnico."""
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO usuarios_tecnicos (nombre, documento, cargo, email)
            VALUES (?, ?, ?, ?)
        """, (nombre, documento, cargo, email))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError(f"El técnico con documento {documento} ya existe")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_tecnicos_activos():
    """Obtiene lista de técnicos activos."""
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM usuarios_tecnicos WHERE activo = 1 ORDER BY nombre")
    res = cursor.fetchall()
    conn.close()
    return res

def get_tecnico_por_id(id_tecnico):
    """Obtiene datos de un técnico por ID."""
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM usuarios_tecnicos WHERE id = ?", (id_tecnico,))
    res = cursor.fetchone()
    conn.close()
    return res

# Ejecutar creación de tablas al importar
create_tables()