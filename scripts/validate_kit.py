#!/usr/bin/env python3
"""
CenitForge Kit Validator
Checks the structural integrity of the generated kit repository.
"""

import sys
from pathlib import Path

# Reconfigure stdout to use UTF-8 to prevent encoding errors on Windows when printing emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CRITICAL_FILES = [
    "README.md",
    "ARCHITECTURE.md",
    "INDEX.md",
    "QUICKSTART.md",
    "Makefile",
    "cookiecutter.json",
    "LICENSE",
    "docs/plan-maestro-v5.md",
    "scripts/bootstrap.sh",
    "scripts/validate-kit.sh",
    "scripts/new-project.sh",
    "scripts/generate-index.sh",
    ".gitignore",
    ".gitattributes",
]

def main():
    print("🔍 Validando integridad del kit CenitForge (Versión Python)...")
    print("====================================================================")
    
    root = Path(__file__).parent.parent
    errors = 0
    
    print("\n📋 Comprobación de archivos críticos:")
    for rel_path in CRITICAL_FILES:
        target = root / rel_path
        if target.exists():
            print(f"  ✅ {rel_path} - Presente ({target.stat().st_size} bytes)")
        else:
            print(f"  ❌ {rel_path} - FALTA")
            errors += 1
            
    # Verificar que la plantilla de cookiecutter esté presente
    template_dir = root / "templates" / "{{cookiecutter.project_slug}}"
    print("\n📦 Comprobación de plantilla Cookiecutter:")
    if template_dir.exists() and template_dir.is_dir():
        print(f"  ✅ Plantilla de proyecto - Presente en {template_dir.relative_to(root)}")
        # Contar archivos dentro de la plantilla
        template_files = list(template_dir.rglob("*"))
        file_count = sum(1 for f in template_files if f.is_file())
        dir_count = sum(1 for f in template_files if f.is_dir())
        print(f"     - {file_count} archivos de plantilla")
        print(f"     - {dir_count} directorios de plantilla")
        if file_count < 40:
            print("  ⚠️ Advertencia: El número de archivos en la plantilla es bajo. Revisa la extracción.")
    else:
        print("  ❌ Plantilla de proyecto - FALTA")
        errors += 1
        
    total_files = sum(1 for f in root.rglob("*") if f.is_file() and not ".git/" in str(f.as_posix()))
    print(f"\n📊 Archivos totales en el repositorio del kit: {total_files}")
    
    print("====================================================================")
    if errors == 0:
        print("✅ Validación PASSED - El kit está completo y listo para producción.")
        sys.exit(0)
    else:
        print(f"❌ Validación FAILED - Se encontraron {errors} errores estructurales.")
        sys.exit(1)

if __name__ == "__main__":
    main()
