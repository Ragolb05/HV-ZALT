# 🖥️ Sistema de Gestión de Inventario IT - ZALT

Sistema web para la gestión digital de hojas de vida de equipos IT con firmas electrónicas.

## 📋 Características

- ✅ Registro de equipos con información técnica detallada
- ✅ Firmas electrónicas dibujadas (empleado + técnico)
- ✅ Historial de cambios y actualizaciones
- ✅ Gestión de técnicos helpdesk
- ✅ Validaciones de datos (IP, correo, documentos)
- ✅ Responsivo para dispositivos móviles

## 🚀 Instalación Local

### Requisitos:
- Python 3.8+
- pip

### Pasos:

```bash
# Clonar el repositorio
git clone https://github.com/Ragolb05/HV.git
cd HV

# Crear virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
streamlit run app.py
```

## 📱 Acceso desde dispositivo móvil (misma red)

1. En tu PC: `streamlit run app.py`
2. Busca "Network URL" en la salida
3. Desde tu celular accede a esa URL
4. ¡Listo! Puedes usar la app y firmar desde tu móvil

## 🌐 Deploy en Streamlit Cloud

1. Sube este repo a GitHub
2. Ve a https://share.streamlit.io
3. Conecta tu repo de GitHub
4. Selecciona: main branch → app.py
5. ¡Tu app estará en línea!

## 📁 Estructura del Proyecto

```
HV/
├── app.py                 # Aplicación principal
├── database.py           # Funciones de BD
├── requirements.txt      # Dependencias
├── .streamlit/
│   └── config.toml      # Configuración Streamlit
└── .gitignore           # Archivos a ignorar en Git
```

## 🔐 Base de Datos

Usa SQLite (incluida). La BD se crea automáticamente al iniciar.

## 👨‍💻 Autor

ZALT S.A.S - Sistema de Gestión IT

## 📝 Licencia

MIT
