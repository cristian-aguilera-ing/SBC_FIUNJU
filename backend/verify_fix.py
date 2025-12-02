#!/usr/bin/env python3
"""
Script para verificar que la lógica de selección de materias funciona correctamente
para planes mixtos como "1 Muy Difícil + 1 Fácil"
"""

# Simulamos la estructura de datos que devuelve la query de materias_habilitadas
materias_habilitadas = [
    {"uri": "mat1", "label": "Análisis Matemático II", "dificultad": 4, "es_obligatoria": True, "desbloquea_count": 5, "anio": 2, "creditos": 6, "es_cursando": False},
    {"uri": "mat2", "label": "Física Mecánica", "dificultad": 4, "es_obligatoria": True, "desbloquea_count": 4, "anio": 2, "creditos": 6, "es_cursando": False},
    {"uri": "mat3", "label": "Arquitectura de Computadoras", "dificultad": 1, "es_obligatoria": True, "desbloquea_count": 3, "anio": 2, "creditos": 5, "es_cursando": False},
    {"uri": "mat4", "label": "Ingeniería del Software I", "dificultad": 1, "es_obligatoria": True, "desbloquea_count": 2, "anio": 3, "creditos": 5, "es_cursando": False},
    {"uri": "mat5", "label": "Probabilidad y Estadística", "dificultad": 3, "es_obligatoria": True, "desbloquea_count": 2, "anio": 2, "creditos": 5, "es_cursando": False},
]

# Simulamos los datos de la estrategia del Plan D para Perfil Medio Bajo
# Plan D: 1 Muy Difícil + 1 Fácil
cant_a_sugerir = 2
min_req = 1
dificultad_req = 4  # Muy Difícil

print("=" * 80)
print("VERIFICACIÓN: Plan D - 1 Muy Difícil + 1 Fácil (Perfil Medio Bajo)")
print("=" * 80)
print(f"\nMaterias disponibles:")
for m in materias_habilitadas:
    print(f"  - {m['label']:40} | Dificultad: {m['dificultad']}")

print(f"\nParámetros de la estrategia:")
print(f"  - Cantidad total a sugerir: {cant_a_sugerir}")
print(f"  - Dificultad requerida: {dificultad_req} (Muy Difícil)")
print(f"  - Mínimo requerido de esa dificultad: {min_req}")

print(f"\n{'-' * 80}")
print("APLICANDO NUEVA LÓGICA:")
print('-' * 80)

# Nueva lógica implementada
plan_seleccionado = []

if dificultad_req is not None:
    # 1. Tomar el mínimo requerido de la dificultad específica
    primary_candidates = [m for m in materias_habilitadas if m["dificultad"] == dificultad_req]
    print(f"\n1. Materias con dificultad {dificultad_req} (primary_candidates):")
    for m in primary_candidates:
        print(f"     - {m['label']:40} | Dificultad: {m['dificultad']}")
    
    plan_seleccionado.extend(primary_candidates[:min_req])
    print(f"\n   Tomando las primeras {min_req} materias de nivel {dificultad_req}:")
    for m in plan_seleccionado:
        print(f"     ✓ {m['label']:40} | Dificultad: {m['dificultad']}")
    
    # 2. Rellenar con materias más fáciles (dificultad < dificultad_req)
    if len(plan_seleccionado) < cant_a_sugerir:
        faltantes = cant_a_sugerir - len(plan_seleccionado)
        uris_sel = {m["uri"] for m in plan_seleccionado}
        
        # Filtrar materias con dificultad MENOR a la requerida
        easier_candidates = [
            m for m in materias_habilitadas 
            if m["uri"] not in uris_sel and m["dificultad"] < dificultad_req
        ]
        # Ordenar por dificultad ascendente (más fáciles primero)
        easier_candidates.sort(key=lambda x: x["dificultad"])
        
        print(f"\n2. Faltan {faltantes} materias. Buscando materias más fáciles (dificultad < {dificultad_req}):")
        for m in easier_candidates:
            print(f"     - {m['label']:40} | Dificultad: {m['dificultad']}")
        
        plan_seleccionado.extend(easier_candidates[:faltantes])
        
        print(f"\n   Tomando las primeras {faltantes} materias más fáciles:")
        for m in easier_candidates[:faltantes]:
            print(f"     ✓ {m['label']:40} | Dificultad: {m['dificultad']}")

print(f"\n{'=' * 80}")
print("RESULTADO FINAL:")
print('=' * 80)
print(f"\nMaterias seleccionadas para el plan ({len(plan_seleccionado)} materias):")
for i, m in enumerate(plan_seleccionado, 1):
    print(f"  {i}. {m['label']:40} | Nivel Dificultad: {m['dificultad']}")

# Verificación
print(f"\n{'-' * 80}")
print("VERIFICACIÓN:")
print('-' * 80)
count_by_difficulty = {}
for m in plan_seleccionado:
    d = m["dificultad"]
    count_by_difficulty[d] = count_by_difficulty.get(d, 0) + 1

print(f"\nDistribución por dificultad:")
dificultad_labels = {1: "Fácil", 2: "Normal", 3: "Difícil", 4: "Muy Difícil"}
for d, count in sorted(count_by_difficulty.items()):
    print(f"  - Nivel {d} ({dificultad_labels.get(d, 'Desconocido')}): {count} materia(s)")

# Verificar que se cumple el plan "1 Muy Difícil + 1 Fácil"
muy_dificiles = count_by_difficulty.get(4, 0)
faciles = count_by_difficulty.get(1, 0)

print(f"\n{'=' * 80}")
if muy_dificiles == 1 and faciles == 1:
    print("✅ ÉXITO: El plan '1 Muy Difícil + 1 Fácil' se cumple correctamente!")
    print(f"   - {muy_dificiles} materia Muy Difícil")
    print(f"   - {faciles} materia Fácil")
elif muy_dificiles == 1 and faciles == 0 and count_by_difficulty.get(2, 0) + count_by_difficulty.get(3, 0) == 1:
    print("⚠️ ADVERTENCIA: Se seleccionó 1 Muy Difícil pero no hay materias Fáciles disponibles.")
    print(f"   Se rellenó con una materia de dificultad {list(count_by_difficulty.keys())[1]}.")
    print("   Esto es aceptable si no hay materias más fáciles disponibles.")
else:
    print("❌ ERROR: El plan NO se cumple!")
    print(f"   Se esperaba: 1 Muy Difícil + 1 Fácil")
    print(f"   Se obtuvo: {muy_dificiles} Muy Difícil + {faciles} Fácil")
print('=' * 80)
