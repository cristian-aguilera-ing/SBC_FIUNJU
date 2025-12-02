#!/usr/bin/env python3
"""
Script para probar el MODO FILTRADO con materias seleccionadas "Cursando"
Simula el caso: Usuario seleccionó 2 muy difíciles + 2 fáciles
Plan recomendado: 1 Muy Difícil + 1 Fácil
"""

# Simulamos materias disponibles (todas las que el usuario puede cursar)
materias_habilitadas = [
    {"uri": "mat1", "label": "Análisis Matemático II", "dificultad": 4, "es_cursando": True},
    {"uri": "mat2", "label": "Física Mecánica", "dificultad": 4, "es_cursando": True},
    {"uri": "mat3", "label": "Arquitectura de Computadoras", "dificultad": 1, "es_cursando": True},
    {"uri": "mat4", "label": "Ingeniería del Software I", "dificultad": 1, "es_cursando": True},
    {"uri": "mat5", "label": "Probabilidad y Estadística", "dificultad": 3, "es_cursando": False},
]

# URIs que el usuario marcó como "Cursando"
uris_cursando = {"mat1", "mat2", "mat3", "mat4"}

# Estrategia: Plan D Medio Bajo - 1 Muy Difícil + 1 Fácil
cant_a_sugerir = 2
min_req = 1
dificultad_req = 4

print("=" * 80)
print("PRUEBA: MODO FILTRADO - Plan D (1 Muy Difícil + 1 Fácil)")
print("=" * 80)

print(f"\nMaterias seleccionadas por el usuario (Cursando):")
for m in materias_habilitadas:
    if m["es_cursando"]:
        print(f"  - {m['label']:40} | Dificultad: {m['dificultad']}")

print(f"\nParámetros de la estrategia:")
print(f"  - Cantidad total a sugerir: {cant_a_sugerir}")
print(f"  - Dificultad requerida: {dificultad_req} (Muy Difícil)")
print(f"  - Mínimo requerido de esa dificultad: {min_req}")

print(f"\n{'-' * 80}")
print("APLICANDO LÓGICA CORREGIDA (MODO FILTRADO):")
print('-' * 80)

# 1. Identificar materias seleccionadas por el usuario
seleccion_usuario = [m for m in materias_habilitadas if m["uri"] in uris_cursando]

print(f"\n1. Materias seleccionadas por el usuario ({len(seleccion_usuario)} total):")
for m in seleccion_usuario:
    print(f"     - {m['label']:40} | Dificultad: {m['dificultad']}")

# 2. Construir plan respetando cantidad y distribución de dificultades
plan_seleccionado = []

if dificultad_req is not None:
    # Separar materias por dificultad
    primary = [m for m in seleccion_usuario if m["dificultad"] == dificultad_req]
    others = [m for m in seleccion_usuario if m["dificultad"] != dificultad_req]
    
    print(f"\n2. Materias que coinciden con dificultad requerida ({dificultad_req}):")
    for m in primary:
        print(f"     - {m['label']:40} | Dificultad: {m['dificultad']}")
    
    print(f"\n3. Otras materias (dificultad != {dificultad_req}):")
    for m in others:
        print(f"     - {m['label']:40} | Dificultad: {m['dificultad']}")
    
    # Tomar EXACTAMENTE min_req de la dificultad requerida (no más)
    plan_seleccionado.extend(primary[:min_req])
    
    print(f"\n4. Tomando EXACTAMENTE {min_req} materia(s) de nivel {dificultad_req}:")
    for m in primary[:min_req]:
        print(f"     ✓ {m['label']:40} | Dificultad: {m['dificultad']}")
    
    # Rellenar con materias más fáciles de la selección del usuario
    if len(plan_seleccionado) < cant_a_sugerir:
        faltantes = cant_a_sugerir - len(plan_seleccionado)
        # Ordenar 'others' por dificultad ascendente (más fáciles primero)
        others.sort(key=lambda x: x["dificultad"]) 
        
        print(f"\n5. Faltan {faltantes} materia(s). Rellenando con las más fáciles:")
        for m in others[:faltantes]:
            print(f"     ✓ {m['label']:40} | Dificultad: {m['dificultad']}")
        
        plan_seleccionado.extend(others[:faltantes])

print(f"\n{'=' * 80}")
print("RESULTADO FINAL:")
print('=' * 80)
print(f"\nMaterias seleccionadas para el plan ({len(plan_seleccionado)} materias):")
for i, m in enumerate(plan_seleccionado, 1):
    dif_label = {1: "Fácil", 2: "Normal", 3: "Difícil", 4: "Muy Difícil"}.get(m['dificultad'], "?")
    print(f"  {i}. {m['label']:40} | Nivel {m['dificultad']} ({dif_label})")

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
for d in sorted(count_by_difficulty.keys()):
    count = count_by_difficulty[d]
    print(f"  - Nivel {d} ({dificultad_labels.get(d, 'Desconocido')}): {count} materia(s)")

# Verificar que se cumple el plan "1 Muy Difícil + 1 Fácil"
muy_dificiles = count_by_difficulty.get(4, 0)
faciles = count_by_difficulty.get(1, 0)

print(f"\n{'=' * 80}")
if muy_dificiles == 1 and faciles == 1:
    print("✅ ÉXITO: El plan '1 Muy Difícil + 1 Fácil' se cumple correctamente!")
    print(f"   - {muy_dificiles} materia Muy Difícil")
    print(f"   - {faciles} materia Fácil")
else:
    print("❌ ERROR: El plan NO se cumple!")
    print(f"   Se esperaba: 1 Muy Difícil + 1 Fácil")
    print(f"   Se obtuvo: {muy_dificiles} Muy Difícil(es) + {faciles} Fácil(es)")
    if sum(count_by_difficulty.values()) != 2:
        print(f"   Total de materias: {sum(count_by_difficulty.values())} (esperado: 2)")
print('=' * 80)
