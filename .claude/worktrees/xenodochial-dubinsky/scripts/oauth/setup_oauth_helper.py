#!/usr/bin/env python3
"""
HELPER: Configurar OAuth desde CERO
Te guía paso a paso para crear OAuth client correcto
"""
import os
import sys
from pathlib import Path
import json

def print_separator():
    print("\n" + "="*70)

def print_step(number, title):
    print(f"\n🔹 PASO {number}: {title}")
    print("-"*70)

def check_current_config():
    """Check what account is currently configured"""
    print_separator()
    print("🔍 VERIFICANDO CONFIGURACIÓN ACTUAL")
    print_separator()
    
    # Check credentials.json
    creds_path = Path("data/credentials/credentials.json")
    if creds_path.exists():
        try:
            with open(creds_path, 'r') as f:
                creds = json.load(f)
            
            # Try to find which account it's configured for
            if 'installed' in creds:
                client_id = creds['installed'].get('client_id', 'Unknown')
                print(f"\n✅ credentials.json encontrado")
                print(f"   Client ID: {client_id[:40]}...")
                
                # Check if it mentions an email
                auth_uri = creds['installed'].get('auth_uri', '')
                if 'fbmark' in str(creds).lower():
                    print(f"   ⚠️  Parece configurado para: fbmark@gmail.com")
                elif 'markalvati' in str(creds).lower():
                    print(f"   ✅ Parece configurado para: markalvati@gmail.com")
                else:
                    print(f"   ⚠️  No se puede determinar la cuenta")
                    
        except Exception as e:
            print(f"❌ Error leyendo credentials.json: {e}")
    else:
        print("❌ credentials.json NO ENCONTRADO")
        print(f"   Ubicación esperada: {creds_path}")
    
    # Check .env
    if Path(".env").exists():
        with open(".env", 'r') as f:
            env_content = f.read()
        
        if 'markalvati' in env_content:
            print("\n✅ .env configurado para: markalvati@gmail.com")
        elif 'fbmark' in env_content:
            print("\n⚠️  .env configurado para: fbmark@gmail.com")
    
    # Check token.json
    token_path = Path("data/credentials/token.json")
    if token_path.exists():
        print(f"\n⚠️  token.json existe (probablemente inválido)")
        print(f"   Se eliminará al crear OAuth nuevo")

def show_google_cloud_steps():
    """Show step-by-step instructions for Google Cloud Console"""
    
    print_separator()
    print("📝 GUÍA COMPLETA: CREAR OAUTH CLIENT NUEVO")
    print_separator()
    
    print_step(1, "Ir a Google Cloud Console")
    print("""
    1. Abre: https://console.cloud.google.com/
    2. Inicia sesión con: markalvati@gmail.com ⭐ (IMPORTANTE)
    3. Si no tienes proyecto, crea uno nuevo:
       - Nombre sugerido: "AI Job Foundry"
       - NO necesitas billing/facturación
    """)
    input("\n✅ Presiona Enter cuando hayas iniciado sesión...")
    
    print_step(2, "Habilitar APIs necesarias")
    print("""
    1. En el menú (☰), ve a: "APIs y servicios" > "Biblioteca"
    2. Busca y HABILITA estas APIs:
       
       a) Gmail API
          - Busca: "Gmail API"
          - Click "HABILITAR"
          - Espera unos segundos
       
       b) Google Sheets API
          - Busca: "Google Sheets API"
          - Click "HABILITAR"
          - Espera unos segundos
    
    ✅ Ambas APIs deben mostrar "Administrar" en lugar de "Habilitar"
    """)
    input("\n✅ Presiona Enter cuando hayas habilitado ambas APIs...")
    
    print_step(3, "Configurar Pantalla de Consentimiento")
    print("""
    1. Ve a: "APIs y servicios" > "Pantalla de consentimiento de OAuth"
    2. Selecciona: "Externo" (External)
    3. Click "CREAR"
    
    4. Llena el formulario:
       - Nombre de la app: "AI Job Foundry"
       - Correo de asistencia: markalvati@gmail.com
       - Dominios autorizados: (dejar vacío)
       - Correo de desarrollador: markalvati@gmail.com
    
    5. Click "GUARDAR Y CONTINUAR"
    
    6. En "Alcances" (Scopes):
       Click "AGREGAR O QUITAR ALCANCES"
       Busca y selecciona:
       ✅ Gmail API > ../auth/gmail.readonly
       ✅ Gmail API > ../auth/gmail.modify
       ✅ Gmail API > ../auth/gmail.labels
       ✅ Google Sheets API > ../auth/spreadsheets
       
       Click "ACTUALIZAR"
       Click "GUARDAR Y CONTINUAR"
    
    7. En "Usuarios de prueba":
       Click "AGREGAR USUARIOS"
       Agrega: markalvati@gmail.com
       Click "AGREGAR"
       Click "GUARDAR Y CONTINUAR"
    
    8. Resumen:
       Click "VOLVER AL PANEL"
    """)
    input("\n✅ Presiona Enter cuando hayas configurado la pantalla...")
    
    print_step(4, "Crear Credenciales OAuth")
    print("""
    1. Ve a: "APIs y servicios" > "Credenciales"
    2. Click "CREAR CREDENCIALES" (arriba)
    3. Selecciona: "ID de cliente de OAuth 2.0"
    
    4. Configuración:
       - Tipo de aplicación: "Aplicación de escritorio"
       - Nombre: "AI Job Foundry Desktop"
    
    5. Click "CREAR"
    
    6. Aparecerá ventana "Cliente de OAuth creado":
       ⭐ Click en "DESCARGAR JSON"
       ⭐ GUARDA EL ARCHIVO (se descarga como client_secret_xxx.json)
    """)
    input("\n✅ Presiona Enter cuando hayas DESCARGADO el JSON...")
    
    print_step(5, "Reemplazar credentials.json")
    print("""
    1. Abre la carpeta de descargas
    2. Busca el archivo: client_secret_XXXXX.json
    3. COPIA ese archivo
    4. PEGA en: C:\\Users\\MSI\\Desktop\\ai-job-foundry\\data\\credentials\\
    5. RENOMBRA a: credentials.json
    
    ⚠️  IMPORTANTE: Reemplaza el credentials.json anterior
    """)
    
    creds_dir = Path("data/credentials")
    creds_path = creds_dir / "credentials.json"
    
    print(f"\n📁 Ruta completa donde pegar:")
    print(f"   {creds_path.absolute()}")
    
    input("\n✅ Presiona Enter cuando hayas reemplazado credentials.json...")
    
    # Verify new file
    if creds_path.exists():
        try:
            with open(creds_path, 'r') as f:
                creds = json.load(f)
            
            if 'installed' in creds:
                print("\n✅ Nuevo credentials.json detectado")
                client_id = creds['installed'].get('client_id', 'Unknown')
                print(f"   Client ID: {client_id[:50]}...")
            else:
                print("\n⚠️  Formato inusual, pero continuemos...")
        except Exception as e:
            print(f"\n⚠️  Error leyendo archivo: {e}")
            print("   Pero continuaremos de todas formas...")
    else:
        print("\n⚠️  credentials.json no encontrado aún")
        print("   Asegúrate de haberlo copiado a la carpeta correcta")

def verify_env_config():
    """Verify .env has correct email"""
    print_separator()
    print("📧 VERIFICANDO CONFIGURACIÓN DE EMAIL")
    print_separator()
    
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env no encontrado")
        return
    
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    needs_update = False
    new_lines = []
    
    for line in lines:
        if 'GMAIL_ADDRESS=' in line:
            if 'markalvati@gmail.com' in line:
                print("✅ GMAIL_ADDRESS configurado correctamente")
                new_lines.append(line)
            else:
                print("⚠️  GMAIL_ADDRESS no es markalvati@gmail.com")
                new_lines.append("GMAIL_ADDRESS=markalvati@gmail.com\n")
                needs_update = True
        elif 'LINKEDIN_EMAIL=' in line:
            if 'markalvati@gmail.com' in line:
                print("✅ LINKEDIN_EMAIL configurado correctamente")
                new_lines.append(line)
            else:
                print("⚠️  LINKEDIN_EMAIL no es markalvati@gmail.com")
                new_lines.append("LINKEDIN_EMAIL=markalvati@gmail.com\n")
                needs_update = True
        else:
            new_lines.append(line)
    
    if needs_update:
        print("\n🔧 Actualizando .env con cuenta correcta...")
        with open(env_path, 'w') as f:
            f.writelines(new_lines)
        print("✅ .env actualizado")

def final_instructions():
    """Show final steps"""
    print_separator()
    print("🎯 ÚLTIMOS PASOS")
    print_separator()
    
    print("""
    Ahora que tienes el OAuth client nuevo:
    
    1. Ejecuta:
       py reauthenticate_gmail.py
    
    2. Se abrirá navegador
       ⚠️  ASEGÚRATE DE SELECCIONAR: markalvati@gmail.com
       (NO fbmark@gmail.com)
    
    3. Acepta TODOS los permisos:
       ✅ Ver, editar, crear y eliminar todos tus correos
       ✅ Ver y editar tus hojas de cálculo
    
    4. Verás "Autenticación exitosa"
    
    5. Luego ejecuta:
       py process_bulletins.py
       O
       py control_center.py → Opción 4
    """)

def main():
    """Main helper flow"""
    print_separator()
    print("🔐 OAUTH SETUP HELPER")
    print("   Configurar OAuth desde CERO con cuenta correcta")
    print_separator()
    
    print("""
    Este helper te guiará para:
    1. Crear OAuth client NUEVO en Google Cloud
    2. Configurar para markalvati@gmail.com (cuenta correcta)
    3. Reemplazar credentials.json antiguo
    4. Re-autenticar correctamente
    """)
    
    response = input("\n¿Continuar? (s/n): ").strip().lower()
    if response != 's':
        print("Cancelado")
        return
    
    # Check current config
    check_current_config()
    
    # Show Google Cloud steps
    show_google_cloud_steps()
    
    # Verify env
    verify_env_config()
    
    # Final instructions
    final_instructions()
    
    print_separator()
    print("✅ CONFIGURACIÓN COMPLETA")
    print_separator()
    print("""
    Próximo paso:
    py reauthenticate_gmail.py
    
    ⚠️  Selecciona markalvati@gmail.com en el navegador
    """)

if __name__ == "__main__":
    main()
