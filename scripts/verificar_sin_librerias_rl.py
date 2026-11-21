"""Comprueba importaciones de bibliotecas de RL mediante AST (Python estándar).

Uso: python scripts/verificar_sin_librerias_rl.py
Es una revisión estática, no una prueba matemática de corrección del algoritmo.
"""
from __future__ import annotations

import ast
from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
BANNED = frozenset({
    'gym', 'gymnasium', 'stable_baselines', 'stable_baselines3', 'sb3_contrib',
    'rllib', 'ray', 'tianshou', 'cleanrl', 'mushroom_rl', 'pettingzoo',
    'acme', 'dopamine', 'torchrl', 'tf_agents', 'rlberry', 'rlax',
})
SCAN_DIRS = ('src', 'scripts', 'tests')


def forbidden_module(name: str) -> bool:
    return name.split('.')[0].replace('-', '_').lower() in BANNED


def violations_in_source(text: str, path: str = '<texto>') -> list[str]:
    """Detecta imports directos y dinámicos con nombres literales."""
    tree = ast.parse(text, filename=path)
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if forbidden_module(alias.name):
                    violations.append(f'{path}:{node.lineno}: import {alias.name}')
        elif isinstance(node, ast.ImportFrom):
            if node.module and forbidden_module(node.module):
                violations.append(f'{path}:{node.lineno}: from {node.module} import ...')
        elif isinstance(node, ast.Call) and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
            fn = node.func
            dynamic = (isinstance(fn, ast.Name) and fn.id == '__import__') or (
                isinstance(fn, ast.Attribute) and fn.attr == 'import_module'
                and isinstance(fn.value, ast.Name) and fn.value.id == 'importlib')
            if dynamic and forbidden_module(node.args[0].value):
                violations.append(f'{path}:{node.lineno}: import dinámico {node.args[0].value}')
    return violations


def scan_project(root: Path = ROOT) -> tuple[list[str], int]:
    violations: list[str] = []
    checked = 0
    for dirname in SCAN_DIRS:
        folder = root / dirname
        if not folder.exists():
            continue
        for path in sorted(folder.rglob('*.py')):
            if any(part in ('__pycache__', '.venv') for part in path.parts):
                continue
            checked += 1
            violations.extend(violations_in_source(path.read_text(encoding='utf-8'), str(path.relative_to(root))))
    pyproject = root / 'pyproject.toml'
    if pyproject.exists():
        with pyproject.open('rb') as file:
            config = tomllib.load(file)
        project = config.get('project', {})
        declared = list(project.get('dependencies', []))
        for group in project.get('optional-dependencies', {}).values():
            declared.extend(group)
        for dep in declared:
            # Analiza el nombre de paquete antes de extras, versiones y marcadores.
            import re
            match = re.match(r'\s*([a-zA-Z][\w.-]*)', dep)
            if match and forbidden_module(match.group(1)):
                violations.append(f'pyproject.toml: dependencia prohibida: {dep}')
    return violations, checked


def main() -> int:
    found, checked = scan_project()
    print(f'[Auditoría sin librerías RL] Archivos Python revisados: {checked}')
    if found:
        for issue in found:
            print('ERROR:', issue)
        return 1
    print('OK: no se detectaron dependencias ni importaciones conocidas de bibliotecas RL.')
    print('Algoritmos: implementados localmente en src/digimon_rl/agents.py')
    print('Nota: el análisis estático no certifica el comportamiento matemático del código.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
