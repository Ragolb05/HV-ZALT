#!/usr/bin/env python
"""Script de prueba para verificar imports y sintaxis"""

try:
    print("Probando imports...")
    from database import (
        create_tables,
        insert_hoja_completa,
        actualizar_hoja_vida,
        get_hoja_vida_actual,
        get_todas_hojas_actuales,
        get_historial_cambios,
        guardar_firma_digital,
        get_firmas_equipo,
        registrar_tecnico,
        get_tecnicos_activos,
        get_tecnico_por_id,
        validar_correo,
        validar_documento,
        validar_ip,
        validar_serial
    )
    print("✓ database.py importado correctamente")
    
    # Pruebas rápidas de funciones
    print("\nProbando validaciones...")
    assert validar_correo("test@empresa.com") == True
    assert validar_correo("") == True  # Opcional
    assert validar_documento("1234567890") == True
    assert validar_documento("123") == False
    assert validar_ip("192.168.1.1") == True
    assert validar_ip("999.999.999.999") == False
    print("✓ Validaciones funcionan correctamente")
    
    print("\n✅ Todos los imports y pruebas pasaron con éxito!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
