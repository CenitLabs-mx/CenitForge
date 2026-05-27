#!/usr/bin/env python3
\"\"\"Post-generation hook para cookiecutter.\"\"\"

import os
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path.cwd()


def remove_paths(paths):
    for p in paths:
        target = PROJECT_DIR / p
        if target.exists():
            if target.is_dir():
                subprocess.run(["rm", "-rf", str(target)], check=False)
            else:
                target.unlink()
            print(f"  🗑️  Eliminado: {p}")


def main():
    print("\\n🎨 Post-generación del proyecto\\n")

    # Inicializar git si no existe
    if not (PROJECT_DIR / ".git").exists():
        print("\\n📝 Inicializando repositorio git...")
        subprocess.run("git init", shell=True, cwd=PROJECT_DIR)
        subprocess.run("git add .", shell=True, cwd=PROJECT_DIR)
        subprocess.run(
            'git commit -m "chore: initial commit from CenitForge kit"',
            shell=True, cwd=PROJECT_DIR,
        )

    print("\\n" + "=" * 60)
    print("✅ Proyecto generado exitosamente!")
    print("=" * 60)
    print(f"\\n📂 Directorio: {PROJECT_DIR}")
    print("\\n🚀 Próximos pasos:")
    print(f"   cd {PROJECT_DIR.name}")
    print("   make setup")
    print("   make validate")


if __name__ == "__main__":
    main()
