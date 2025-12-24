#!/usr/bin/env python3
"""
Script de configuración inicial para Tuniforme.
Genera SECRET_KEY y valida configuración de variables de entorno.
"""
import os
import secrets
import sys
from pathlib import Path


def generate_secret_key():
    """Genera una SECRET_KEY segura para Django."""
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return ''.join(secrets.choice(chars) for i in range(50))


def check_env_file():
    """Verifica si existe el archivo .env"""
    env_path = Path('.env')
    env_example_path = Path('.env.example')
    
    if not env_path.exists():
        print("⚠️  Archivo .env no encontrado")
        if env_example_path.exists():
            print("📝 Copiando .env.example a .env...")
            with open(env_example_path, 'r') as src:
                content = src.read()
            
            # Generar SECRET_KEY automáticamente
            new_secret = generate_secret_key()
            content = content.replace('your_secret_key_here', new_secret)
            
            with open(env_path, 'w') as dst:
                dst.write(content)
            
            print("✅ Archivo .env creado con SECRET_KEY generada")
            print(f"\n🔑 Tu SECRET_KEY: {new_secret}\n")
            print("⚠️  AHORA DEBES EDITAR .env Y CONFIGURAR:")
            print("   - EMAIL_HOST_USER (tu email)")
            print("   - EMAIL_HOST_PASSWORD (app password de Gmail)")
            print("   - TRANSBANK_API_KEY (si usas producción)")
            print("   - TRANSBANK_API_SECRET (si usas producción)")
            print("   - DATABASE_URL (PostgreSQL en producción)")
        else:
            print("❌ No se encontró .env.example")
            return False
    else:
        print("✅ Archivo .env encontrado")
    
    return True


def validate_env_vars():
    """Valida que las variables críticas estén configuradas."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv no instalado. Ejecuta: pip install python-dotenv")
        return False
    
    required_vars = [
        'SECRET_KEY',
        'DEBUG',
        'ALLOWED_HOSTS',
        'EMAIL_HOST_USER',
        'EMAIL_HOST_PASSWORD',
    ]
    
    missing = []
    default_values = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        elif 'your_' in value or 'here' in value:
            default_values.append(var)
    
    if missing:
        print(f"\n❌ Variables faltantes en .env: {', '.join(missing)}")
        return False
    
    if default_values:
        print(f"\n⚠️  Variables con valores por defecto (DEBES CAMBIARLAS): {', '.join(default_values)}")
        return False
    
    print("\n✅ Todas las variables críticas están configuradas")
    return True


def check_logs_directory():
    """Verifica que existe el directorio de logs."""
    logs_dir = Path('logs')
    if not logs_dir.exists():
        print("📁 Creando directorio logs/...")
        logs_dir.mkdir(exist_ok=True)
        (logs_dir / '.gitkeep').touch()
        print("✅ Directorio logs/ creado")
    else:
        print("✅ Directorio logs/ existe")


def main():
    print("=" * 60)
    print("🔧 Configuración Inicial de Tuniforme")
    print("=" * 60)
    print()
    
    # 1. Verificar .env
    print("1️⃣  Verificando archivo .env...")
    if not check_env_file():
        print("\n❌ Error al configurar .env")
        return 1
    
    print()
    
    # 2. Validar variables
    print("2️⃣  Validando variables de entorno...")
    validate_env_vars()
    
    print()
    
    # 3. Verificar directorio de logs
    print("3️⃣  Verificando directorio de logs...")
    check_logs_directory()
    
    print()
    print("=" * 60)
    print("🎯 Próximos pasos:")
    print("=" * 60)
    print("1. Edita .env con tus credenciales reales")
    print("2. Ejecuta: python manage.py migrate")
    print("3. Ejecuta: python manage.py createsuperuser")
    print("4. Ejecuta: python manage.py runserver")
    print()
    print("📖 Para más información, lee README.md")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
