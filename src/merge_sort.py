import random

# ─── Generación del arreglo ──────────────────────────────────────────────────
n  = int(input("Cantidad de elementos : "))
li = int(input("Límite inferior       : "))
ls = int(input("Límite superior       : "))

ldes = [random.randint(li, ls) for _ in range(n)]
print("\nArreglo original:", ldes)

# ─── Merge Sort con trazado visual ───────────────────────────────────────────
comparaciones  = 0
intercambios   = 0

def merge_sort(lista, nivel=0):
    global comparaciones, intercambios

    sangria = "  " * nivel     # indentación por nivel de recursión

    if len(lista) <= 1:
        return lista

    mitad     = len(lista) // 2
    izquierda = lista[:mitad]
    derecha   = lista[mitad:]

    print(f"{sangria}[Nivel {nivel}] Dividir → Izq: {izquierda}  |  Der: {derecha}")

    izquierda = merge_sort(izquierda, nivel + 1)
    derecha   = merge_sort(derecha,   nivel + 1)

    print(f"{sangria}[Nivel {nivel}] Fusionar ← {izquierda} + {derecha}")

    ordenado = []
    i = j = 0

    while i < len(izquierda) and j < len(derecha):
        comparaciones += 1
        if izquierda[i] <= derecha[j]:
            ordenado.append(izquierda[i])
            i += 1
        else:
            ordenado.append(derecha[j])
            j += 1
            intercambios += 1

    ordenado.extend(izquierda[i:])
    ordenado.extend(derecha[j:])

    print(f"{sangria}[Nivel {nivel}] Resultado: {ordenado}")
    return ordenado


# ─── Ejecución ───────────────────────────────────────────────────────────────
print("\n" + "─" * 50)
ordenada = merge_sort(ldes)
print("─" * 50)
print("\nArreglo ordenado :", ordenada)
print(f"Comparaciones    : {comparaciones}")
print(f"Intercambios     : {intercambios}")
