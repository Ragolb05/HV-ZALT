import streamlit as st
import pandas as pd
from datetime import date, datetime
import os
from streamlit_drawable_canvas import st_canvas

# Importamos las funciones desde tu archivo database.py
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

# 1. Inicialización de la base de datos al arrancar
create_tables()

# ==================== FUNCIONES AUXILIARES ====================

def obtener_ip_usuario():
    """Intenta obtener IP (limitado en Streamlit Cloud)."""
    try:
        return os.environ.get('REMOTE_ADDR', 'No disponible')
    except:
        return "No disponible"

def obtener_navegador():
    """Obtiene información del navegador."""
    try:
        return "Navegador interno Streamlit"
    except:
        return "No disponible"

def formulario_asignacion(accion_tipo="nueva", nombre_equipo_editar=None, id_tecnico=None):
    """Formulario reutilizable para crear o actualizar hojas de vida."""
    
    if accion_tipo == "nueva":
        st.markdown("### 1. Identificación del Equipo")
        nombre_equipo = st.text_input("Nombre del Equipo (ID Único)", placeholder="Ej: ZLT-BOD-01").upper()
        datos_cargados = None
    else:
        st.markdown("### 1. Equipo a Actualizar")
        nombre_equipo = nombre_equipo_editar
        datos_cargados, _ = get_hoja_vida_actual(nombre_equipo)
        st.info(f"ℹ️ Actualizando equipo: **{nombre_equipo}**")
    
    st.divider()
    
    st.markdown("### 2. Información del Usuario")
    u1, u2, u3, u4 = st.columns(4)
    nombre_usuario = u1.text_input("Nombre Usuario", 
                                    value=datos_cargados['nombre_usuario'] if datos_cargados else "")
    cc = u2.text_input("Número de documento (CC)", 
                       value=datos_cargados['cc'] if datos_cargados else "")
    cargo = u3.text_input("Cargo", 
                         value=datos_cargados['cargo'] if datos_cargados else "")
    fecha_asig = u4.date_input("Fecha de Asignación", 
                              value=datetime.strptime(datos_cargados['fecha_asignacion'], '%Y-%m-%d').date() 
                              if datos_cargados and datos_cargados['fecha_asignacion'] else date.today())
    
    u5, u6, u7 = st.columns(3)
    area = u5.selectbox("Área de Ubicación", 
                       [" ", "Bodega", "Administrativo", "Servicio Técnico", "Gerencia"],
                       index=0 if not datos_cargados else [" ", "Bodega", "Administrativo", "Servicio Técnico", "Gerencia"].index(datos_cargados['area']),
                       key=f"area_{accion_tipo}")
    ciudad = u6.text_input("Ciudad", 
                          value=datos_cargados['ciudad'] if datos_cargados else "")
    correo_usuario = u7.text_input("Correo Electrónico", 
                                   value=datos_cargados['correo_usuario'] if datos_cargados else "",
                                   placeholder="usuario@empresa.com")

    st.divider()
    
    st.markdown("### 3. Información del Equipo (Periféricos y CPU)")
    
    lista_hardware = []
    
    for i in range(1, 6):
        st.markdown(f"**Elemento #{i}**")
        h1, h2, h3, h4, h5 = st.columns(5)
        
        t = h1.selectbox(f"Tipo {i}", [" ", "Portátil", "Escritorio", "Servidor"], key=f"t{i}_{accion_tipo}")
        e = h2.selectbox(f"Elemento {i}", [" ", "CPU", "Monitor", "Mouse", "Teclado", "UPS", "Impresora"], key=f"e{i}_{accion_tipo}")
        m = h3.text_input(f"Marca {i}", key=f"m{i}")
        mo = h4.text_input(f"Modelo {i}", key=f"mo{i}")
        se = h5.text_input(f"Serial {i}", key=f"se{i}").upper()
        
        if se:
            lista_hardware.append({
                'tipo': t,
                'elemento': e,
                'marca': m,
                'modelo': mo,
                'serial': se
            })
        
        if i < 5:
            st.markdown("---")

    st.divider()
    
    st.markdown("### 4. Especificaciones Técnicas y Red")
    s1, s2, s3, s4 = st.columns(4)
    so = s1.selectbox("S.O.", ["Windows 10", "Windows 11", "Linux", "macOS"],
                     index=["Windows 10", "Windows 11", "Linux", "macOS"].index(datos_cargados['sistema_operativo']) if datos_cargados and datos_cargados['sistema_operativo'] in ["Windows 10", "Windows 11", "Linux", "macOS"] else 1,
                     key=f"so_{accion_tipo}")
    arq = s2.selectbox("Arquitectura", ["64 bits", "32 bits"],
                      index=["64 bits", "32 bits"].index(datos_cargados['arquitectura']) if datos_cargados and datos_cargados['arquitectura'] in ["64 bits", "32 bits"] else 0,
                      key=f"arq_{accion_tipo}")
    ofim = s3.selectbox("Ofimática", ["Microsoft Office", "Libre Office"],
                       index=["Microsoft Office", "Libre Office"].index(datos_cargados['software_ofimatica']) if datos_cargados and datos_cargados['software_ofimatica'] in ["Microsoft Office", "Libre Office"] else 0,
                       key=f"ofim_{accion_tipo}")
    v_ofim = s4.text_input("Versión Office", 
                           value=datos_cargados['v_office'] if datos_cargados else "")
    
    s5, s6, s7, s8 = st.columns(4)
    m_disco = s5.text_input("Marca Disco Duro", 
                           value=datos_cargados['md_duro'] if datos_cargados else "")
    c_disco = s6.text_input("Capacidad Disco", 
                           value=datos_cargados['cd_duro'] if datos_cargados else "")
    m_ram = s7.text_input("Marca RAM", 
                         value=datos_cargados['m_ram'] if datos_cargados else "")
    c_ram = s8.selectbox("Capacidad RAM", ["4GB", "8GB", "12GB", "16GB", "32GB"],
                        index=["4GB", "8GB", "12GB", "16GB", "32GB"].index(datos_cargados['c_ram']) if datos_cargados and datos_cargados['c_ram'] in ["4GB", "8GB", "12GB", "16GB", "32GB"] else 1,
                        key=f"cram_{accion_tipo}")

    s9, s10, s11, s12 = st.columns(4)
    t_proc = s9.text_input("Tipo de Procesador", 
                          value=datos_cargados['t_procesador'] if datos_cargados else "",
                          placeholder="Ej: Intel i7-10700K")
    user_red = s10.text_input("Usuario de Red", 
                             value=datos_cargados['user_red'] if datos_cargados else "")
    ip_fija = s11.text_input("IP Fija", 
                            value=datos_cargados['dir_ip'] if datos_cargados else "")
    antivirus = s12.text_input("Antivirus", 
                              value=datos_cargados['anti'] if datos_cargados else "")
    
    s13 = st.text_input("Versión Antivirus", 
                       value=datos_cargados['v_anti'] if datos_cargados else "")

    st.divider()

    st.markdown("### 5. Aplicaciones instaladas en el equipo")
    apps = st.text_area("Aplicaciones", 
                       value=datos_cargados['apps'] if datos_cargados else "",
                       placeholder="Excel, Teams, etc.")

    st.divider()

    st.markdown("### 6. Observaciones adicionales")
    obs = st.text_area("Observaciones adicionales", 
                      value=datos_cargados['obs'] if datos_cargados else "")
    
    st.divider()

    st.info("En atención al trabajo que será desempeñado ZALT S.A.S en su calidad de EMPLEADOR hace entrega a EL TRABAJADOR de los elementos descritos en este documento en calidad de comodato gratuito.  EL TRABAJADOR manifiesta de manera expresa que ha recibido los anteriores elementos, a titulo de comodato gratuito, en perfecto estado de funcionamiento y se compromete a cuidar de los recursos asignados, a hacer uso de ellos para los fines establecidos y a retornarlos en el mismo estado salvo por el deterioro natural de los mismos.")

    st.markdown("### 7. Firmas Digitales 🔐")
    
    # Firma Empleado
    st.markdown("**FIRMA DEL EMPLEADO**")
    f1, f2, f3 = st.columns(3)
    nombre_empleado = f1.text_input("Nombre del Empleado", key=f"nombre_empleado_firma_{accion_tipo}")
    cc_empleado = f2.text_input("Documento Empleado", key=f"cc_empleado_firma_{accion_tipo}")
    cargo_empleado = f3.text_input("Cargo Empleado", key=f"cargo_empleado_firma_{accion_tipo}")
    
    # Checkboxes de consentimiento (CRÍTICO)
    checkbox_col1, checkbox_col2 = st.columns(2)
    with checkbox_col1:
        consentimiento_recibido = st.checkbox(
            "✅ Confirmo que he RECIBIDO los equipos en BUEN ESTADO",
            key=f"consent_empleado_{accion_tipo}"
        )
    with checkbox_col2:
        responsabilidad_aceptada = st.checkbox(
            "✅ ACEPTO responsabilidad de cuidado y devolución en el mismo estado",
            key=f"resp_empleado_{accion_tipo}"
        )
    
    # Opción de firma dibujada para el empleado
    st.markdown("**Firma Electrónica (Opcional)**")
    tab1_emp, tab2_emp = st.tabs(["📝 Sin firma dibujada", "✍️ Dibujar firma"])
    
    firma_empleado_canvas = None
    with tab2_emp:
        st.info("📱 Puedes dibujar tu firma aquí. Si accedes desde un celular, dibuja con tu dedo.")
        
        firma_empleado_canvas = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=2,
            stroke_color="#000000",
            background_color="#ffffff",
            height=150,
            width=400,
            drawing_mode="freedraw",
            key=f"firma_emp_canvas_{accion_tipo}",
        )
        
        if firma_empleado_canvas.image_data is not None:
            st.success("✅ Firma capturada correctamente")
    
    st.divider()
    
    # Firma Técnico Helpdesk
    st.markdown("**FIRMA DEL ANALISTA HELPDESK**")
    
    # Selector de técnico (si existen registrados)
    tecnicos = get_tecnicos_activos()
    if tecnicos:
        tecnico_seleccionado = st.selectbox(
            "Seleccionar Analista Helpdesk",
            options=[(t['id'], t['nombre']) for t in tecnicos],
            format_func=lambda x: x[1],
            key=f"tecnico_selector_{accion_tipo}"
        )
        id_tecnico_sistema = tecnico_seleccionado[0]
        nombre_tecnico_default = tecnico_seleccionado[1]
    else:
        id_tecnico_sistema = None
        nombre_tecnico_default = ""
        st.warning("⚠️ No hay técnicos registrados en el sistema. Ingrese datos manualmente.")
    
    f4, f5, f6 = st.columns(3)
    nombre_tecnico = f4.text_input("Nombre del Analista Helpdesk", 
                                   value=nombre_tecnico_default,
                                   key=f"nombre_tecnico_firma_{accion_tipo}")
    cc_tecnico = f5.text_input("Documento Técnico", key=f"cc_tecnico_firma_{accion_tipo}")
    cargo_tecnico = f6.text_input("Cargo Técnico", key=f"cargo_tecnico_firma_{accion_tipo}")
    
    # PIN opcional para firma técnica (extra seguridad)
    st.markdown("**Seguridad de Firma Técnica (Opcional)**")
    usar_pin = st.checkbox("Usar PIN de 4 dígitos para mayor seguridad", key=f"usar_pin_{accion_tipo}")
    pin_tecnico = None
    if usar_pin:
        pin_col1, pin_col2 = st.columns(2)
        with pin_col1:
            pin_ingreso = st.text_input("Ingrese PIN (4 dígitos)", type="password", key=f"pin_input_{accion_tipo}")
            if pin_ingreso and (not pin_ingreso.isdigit() or len(pin_ingreso) != 4):
                st.error("❌ El PIN debe contener exactamente 4 dígitos")
                pin_tecnico = None
            elif pin_ingreso:
                pin_tecnico = pin_ingreso
    
    # Opción de firma dibujada para el técnico
    st.markdown("**Firma Electrónica (Opcional)**")
    tab1_tec, tab2_tec = st.tabs(["📝 Sin firma dibujada", "✍️ Dibujar firma"])
    
    firma_tecnico_canvas = None
    with tab2_tec:
        st.info("📱 Puedes dibujar tu firma aquí. Si accedes desde un celular, dibuja con tu dedo.")
        
        firma_tecnico_canvas = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=2,
            stroke_color="#000000",
            background_color="#ffffff",
            height=150,
            width=400,
            drawing_mode="freedraw",
            key=f"firma_tec_canvas_{accion_tipo}",
        )
        
        if firma_tecnico_canvas.image_data is not None:
            st.success("✅ Firma capturada correctamente")
    
    st.divider()
    
    st.divider()
    
    return {
        'nombre_equipo': nombre_equipo,
        'nombre_usuario': nombre_usuario,
        'cc': cc,
        'cargo': cargo,
        'area': area,
        'ciudad': ciudad,
        'correo_usuario': correo_usuario,
        'fecha_asignacion': str(fecha_asig),
        'sistema_operativo': so,
        'arquitectura': arq,
        'software_ofimatica': ofim,
        'v_office': v_ofim,
        'md_duro': m_disco,
        'cd_duro': c_disco,
        'm_ram': m_ram,
        'c_ram': c_ram,
        't_procesador': t_proc,
        'user_red': user_red,
        'dir_ip': ip_fija,
        'anti': antivirus,
        'v_anti': s13,
        'apps': apps,
        'obs': obs,
        'lista_hardware': lista_hardware,
        'nombre_empleado': nombre_empleado,
        'cc_empleado': cc_empleado,
        'cargo_empleado': cargo_empleado,
        'consentimiento_recibido': consentimiento_recibido,
        'responsabilidad_aceptada': responsabilidad_aceptada,
        'firma_empleado_canvas': firma_empleado_canvas.image_data if firma_empleado_canvas and firma_empleado_canvas.image_data is not None else None,
        'nombre_tecnico': nombre_tecnico,
        'cc_tecnico': cc_tecnico,
        'cargo_tecnico': cargo_tecnico,
        'id_tecnico_sistema': id_tecnico_sistema,
        'pin_tecnico': pin_tecnico,
        'firma_tecnico_canvas': firma_tecnico_canvas.image_data if firma_tecnico_canvas and firma_tecnico_canvas.image_data is not None else None
    }

def main():
    st.set_page_config(layout="wide", page_title="Inventario IT ZALT", page_icon="💻")
    
    st.title("🖥️ Sistema de Gestión de Inventario IT")
    st.subheader("Hoja de Vida Digital y Control de Asignaciones")

    # Menú lateral mejorado
    menu = [
        "📝 Asignar Nuevo Equipo", 
        "🔄 Actualizar Equipo", 
        "🔍 Consultar Equipo", 
        "📊 Ver Inventario",
        "📜 Ver Historial de Cambios",
        "👥 Gestionar Técnicos"
    ]
    choice = st.sidebar.selectbox("Menú Principal", menu)

    if choice == "📝 Asignar Nuevo Equipo":
        st.subheader("📝 Registro de Nueva Hoja de Vida")
        
        with st.form(key='form_asignacion_nueva'):
            datos_formulario = formulario_asignacion(accion_tipo="nueva")
            
            submit = st.form_submit_button(label='💾 Guardar Hoja de Vida Completa')
            
            if submit:
                # Validaciones
                errores = []
                if not datos_formulario['nombre_equipo']:
                    errores.append("El Nombre del Equipo es obligatorio")
                if not datos_formulario['nombre_usuario']:
                    errores.append("El Nombre del Usuario es obligatorio")
                if not datos_formulario['cc']:
                    errores.append("El Documento (CC) del usuario es obligatorio")
                if datos_formulario['cc'] and not validar_documento(datos_formulario['cc']):
                    errores.append("Documento inválido (debe ser números, 6-20 dígitos)")
                if datos_formulario['correo_usuario'] and not validar_correo(datos_formulario['correo_usuario']):
                    errores.append("Correo inválido")
                if datos_formulario['dir_ip'] and not validar_ip(datos_formulario['dir_ip']):
                    errores.append("IP inválida")
                if not datos_formulario['lista_hardware']:
                    errores.append("Debe registrar al menos un periférico o CPU con su Serial")
                if not datos_formulario['nombre_empleado']:
                    errores.append("El nombre del empleado que firma es obligatorio")
                if not datos_formulario['cc_empleado']:
                    errores.append("El documento del empleado es obligatorio")
                if not datos_formulario['consentimiento_recibido']:
                    errores.append("El empleado debe confirmar que recibió los equipos en buen estado")
                if not datos_formulario['responsabilidad_aceptada']:
                    errores.append("El empleado debe aceptar la responsabilidad de cuidado")
                if not datos_formulario['nombre_tecnico']:
                    errores.append("El nombre del técnico es obligatorio")
                if not datos_formulario['cc_tecnico']:
                    errores.append("El documento del técnico es obligatorio")
                
                if errores:
                    for error in errores:
                        st.error(f"❌ {error}")
                else:
                    try:
                        # Guardar hoja de vida
                        cabecera_db = {k: v for k, v in datos_formulario.items() 
                                      if k not in ['lista_hardware', 'nombre_empleado', 'cc_empleado', 
                                                   'cargo_empleado', 'consentimiento_recibido', 
                                                   'responsabilidad_aceptada', 'nombre_tecnico', 
                                                   'cc_tecnico', 'cargo_tecnico', 'id_tecnico_sistema', 'pin_tecnico']}
                        
                        id_version = insert_hoja_completa(
                            cabecera_db,
                            datos_formulario['lista_hardware'],
                            datos_formulario['id_tecnico_sistema']
                        )
                        
                        # Guardar firma del empleado
                        guardar_firma_digital(
                            id_version,
                            datos_formulario['nombre_equipo'],
                            'empleado',
                            datos_formulario['nombre_empleado'],
                            datos_formulario['cc_empleado'],
                            datos_formulario['consentimiento_recibido'],
                            datos_formulario['responsabilidad_aceptada'],
                            ip_dispositivo=obtener_ip_usuario(),
                            navegador=obtener_navegador()
                        )
                        
                        # Guardar firma del técnico
                        guardar_firma_digital(
                            id_version,
                            datos_formulario['nombre_equipo'],
                            'tecnico',
                            datos_formulario['nombre_tecnico'],
                            datos_formulario['cc_tecnico'],
                            True,  # El técnico acepta por defecto
                            True,
                            pin=datos_formulario['pin_tecnico'],
                            ip_dispositivo=obtener_ip_usuario(),
                            navegador=obtener_navegador()
                        )
                        
                        st.success(f"✅ ¡Guardado! Hoja de Vida '{datos_formulario['nombre_equipo']}' creada con {len(datos_formulario['lista_hardware'])} periféricos.")
                        st.balloons()
                    except ValueError as err:
                        st.error(f"❌ Error: {err}")
                    except Exception as err:
                        st.error(f"❌ Error al guardar: {err}")

    elif choice == "🔄 Actualizar Equipo":
        st.subheader("🔄 Actualizar Hoja de Vida Existente")
        
        busqueda = st.text_input("Ingrese el nombre del equipo a actualizar (ej: ZLT-BOD-01):").upper()
        
        if busqueda:
            cab, hard = get_hoja_vida_actual(busqueda)
            if not cab:
                st.error(f"❌ No se encontró el equipo '{busqueda}'")
            else:
                st.success(f"✅ Equipo encontrado: {busqueda}")
                st.info(f"Versión actual: {cab['version_numero']}")
                
                with st.form(key='form_actualizacion'):
                    datos_formulario = formulario_asignacion(accion_tipo="actualizar", 
                                                            nombre_equipo_editar=busqueda)
                    
                    submit = st.form_submit_button(label='💾 Guardar Actualización')
                    
                    if submit:
                        # Validaciones similares
                        errores = []
                        if datos_formulario['cc'] and not validar_documento(datos_formulario['cc']):
                            errores.append("Documento inválido")
                        if datos_formulario['correo_usuario'] and not validar_correo(datos_formulario['correo_usuario']):
                            errores.append("Correo inválido")
                        if datos_formulario['dir_ip'] and not validar_ip(datos_formulario['dir_ip']):
                            errores.append("IP inválida")
                        if not datos_formulario['lista_hardware']:
                            errores.append("Debe registrar al menos un periférico")
                        if not datos_formulario['nombre_tecnico']:
                            errores.append("El nombre del técnico es obligatorio")
                        
                        if errores:
                            for error in errores:
                                st.error(f"❌ {error}")
                        else:
                            try:
                                cabecera_db = {k: v for k, v in datos_formulario.items() 
                                              if k not in ['lista_hardware', 'nombre_empleado', 'cc_empleado', 
                                                           'cargo_empleado', 'consentimiento_recibido', 
                                                           'responsabilidad_aceptada', 'nombre_tecnico', 
                                                           'cc_tecnico', 'cargo_tecnico', 'id_tecnico_sistema', 'pin_tecnico']}
                                
                                id_version_nueva = actualizar_hoja_vida(
                                    busqueda,
                                    cabecera_db,
                                    datos_formulario['lista_hardware'],
                                    datos_formulario['id_tecnico_sistema']
                                )
                                
                                guardar_firma_digital(
                                    id_version_nueva,
                                    busqueda,
                                    'tecnico',
                                    datos_formulario['nombre_tecnico'],
                                    datos_formulario['cc_tecnico'],
                                    True,
                                    True,
                                    pin=datos_formulario['pin_tecnico'],
                                    ip_dispositivo=obtener_ip_usuario(),
                                    navegador=obtener_navegador()
                                )
                                
                                st.success(f"✅ ¡Actualizado! Equipo '{busqueda}' versión {id_version_nueva} creada.")
                                st.balloons()
                            except Exception as err:
                                st.error(f"❌ Error al actualizar: {err}")

    elif choice == "🔍 Consultar Equipo":
        st.subheader("🔍 Consultar por Nombre del Equipo")
        busqueda = st.text_input("Ingrese el nombre del equipo a buscar (ej: ZLT-BOD-01):").upper()
        
        if busqueda:
            cab, hard = get_hoja_vida_actual(busqueda)
            if cab:
                st.success(f"✅ Equipo encontrado: {cab['nombre_equipo']}")
                
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.write(f"**Usuario:** {cab['nombre_usuario']}")
                    st.write(f"**Documento:** {cab['cc']}")
                    st.write(f"**Correo:** {cab['correo_usuario'] or 'N/A'}")
                    st.write(f"**Área:** {cab['area']}")
                with col_info2:
                    st.write(f"**S.O.:** {cab['sistema_operativo']} {cab['arquitectura']}")
                    st.write(f"**RAM:** {cab['c_ram']}")
                    st.write(f"**Procesador:** {cab['t_procesador'] or 'N/A'}")
                    st.write(f"**IP:** {cab['dir_ip']}")
                
                st.write(f"**Versión:** {cab['version_numero']} | **Estado:** {cab['estado']} | **Tipo:** {cab['tipo_asignacion']}")
                st.write(f"**Fecha Asignación:** {cab['fecha_asignacion']}")
                
                st.divider()
                st.subheader("📋 Detalle de Periféricos Asignados")
                if hard:
                    df_hard = pd.DataFrame([dict(h) for h in hard])
                    st.table(df_hard[['elemento', 'marca', 'modelo', 'serial']])
                else:
                    st.warning("No hay elementos de hardware registrados para este equipo.")
                
                # Mostrar firmas
                st.divider()
                st.subheader("🔐 Firmas Digitales")
                firmas = get_firmas_equipo(busqueda, cab['id_version'])
                if firmas:
                    for firma in firmas:
                        col_f1, col_f2 = st.columns(2)
                        with col_f1:
                            st.write(f"**Tipo:** {firma['tipo_firma']}")
                            st.write(f"**Firmante:** {firma['nombre_firmante']}")
                            st.write(f"**Documento:** {firma['documento_firmante']}")
                        with col_f2:
                            st.write(f"**Fecha/Hora:** {firma['fecha_firma']}")
                            st.write(f"**Consentimiento:** {'✅ Sí' if firma['consentimiento_recibido'] else '❌ No'}")
                            st.write(f"**Responsabilidad:** {'✅ Aceptada' if firma['responsabilidad_aceptada'] else '❌ No'}")
                else:
                    st.info("No hay firmas registradas para esta versión.")
            else:
                st.error("❌ No se encontró ningún equipo con ese nombre.")

    elif choice == "📊 Ver Inventario":
        st.subheader("📊 Inventario de Equipos (Últimas Versiones)")
        hojas = get_todas_hojas_actuales()
        if hojas:
            df_hojas = pd.DataFrame([dict(h) for h in hojas])
            # Seleccionar columnas relevantes
            columnas_mostrar = ['nombre_equipo', 'nombre_usuario', 'area', 'estado', 
                               'sistema_operativo', 'c_ram', 'dir_ip', 'fecha_asignacion']
            df_hojas_display = df_hojas[[col for col in columnas_mostrar if col in df_hojas.columns]]
            st.dataframe(df_hojas_display, use_container_width=True)
            
            csv = df_hojas_display.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar Inventario (CSV)", data=csv, 
                             file_name="inventario_it.csv", mime="text/csv")
        else:
            st.info("Aún no hay equipos registrados.")

    elif choice == "📜 Ver Historial de Cambios":
        st.subheader("📜 Historial de Cambios")
        
        busqueda = st.text_input("Ingrese nombre del equipo para ver su historial:").upper()
        
        if busqueda:
            historial = get_historial_cambios(busqueda)
            if historial:
                st.success(f"Historial de **{busqueda}**")
                
                for cambio in historial:
                    with st.expander(f"{cambio['tipo_cambio'].upper()} - {cambio['fecha_cambio']}"):
                        col_h1, col_h2 = st.columns(2)
                        with col_h1:
                            st.write(f"**Tipo de Cambio:** {cambio['tipo_cambio']}")
                            st.write(f"**Campo:** {cambio['campo_modificado'] or 'N/A'}")
                            st.write(f"**Técnico:** {cambio['nombre_tecnico'] or 'Sistema'}")
                        with col_h2:
                            st.write(f"**Antes:** {cambio['valor_anterior'] or 'N/A'}")
                            st.write(f"**Después:** {cambio['valor_nuevo'] or 'N/A'}")
                            st.write(f"**Notas:** {cambio['notas'] or '-'}")
            else:
                st.info("No hay cambios registrados para este equipo.")

    elif choice == "👥 Gestionar Técnicos":
        st.subheader("👥 Gestionar Técnicos del Sistema")
        
        tab1, tab2 = st.tabs(["Registrar Técnico", "Ver Técnicos"])
        
        with tab1:
            with st.form(key='form_tecnico'):
                st.markdown("**Registrar nuevo analista helpdesk**")
                nom_tec = st.text_input("Nombre del Técnico")
                doc_tec = st.text_input("Documento (CC)")
                cargo_tec = st.text_input("Cargo")
                email_tec = st.text_input("Email", placeholder="tecnico@empresa.com")
                
                submit_tec = st.form_submit_button("Registrar Técnico")
                
                if submit_tec:
                    errores = []
                    if not nom_tec:
                        errores.append("Nombre es obligatorio")
                    if not doc_tec or not validar_documento(doc_tec):
                        errores.append("Documento inválido")
                    if not cargo_tec:
                        errores.append("Cargo es obligatorio")
                    
                    if errores:
                        for error in errores:
                            st.error(f"❌ {error}")
                    else:
                        try:
                            registrar_tecnico(nom_tec, doc_tec, cargo_tec, email_tec or None)
                            st.success(f"✅ Técnico '{nom_tec}' registrado exitosamente")
                        except ValueError as err:
                            st.error(f"❌ {err}")
                        except Exception as err:
                            st.error(f"❌ Error: {err}")
        
        with tab2:
            tecnicos = get_tecnicos_activos()
            if tecnicos:
                df_tecn = pd.DataFrame([dict(t) for t in tecnicos])
                st.dataframe(df_tecn[['nombre', 'documento', 'cargo', 'email']], use_container_width=True)
            else:
                st.info("No hay técnicos registrados.")

if __name__ == '__main__':
    main()