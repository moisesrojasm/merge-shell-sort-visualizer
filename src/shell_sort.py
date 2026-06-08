import random

# ─── Entrada ──────────────────────────────────────────────────────────────────
n  = int(input("Cantidad de elementos : "))
li = int(input("Límite inferior       : "))
ls = int(input("Límite superior       : "))

ldes = [random.randint(li, ls) for _ in range(n)]
print("\nArreglo original:", ldes)

# ─── Shell Sort con trazado ───────────────────────────────────────────────────
comparaciones = 0
intercambios  = 0

def shell_sort(lista):
    global comparaciones, intercambios
    n = len(lista)
    a = list(lista)

    # Secuencia de Knuth: 1, 4, 13, 40, 121...
    gaps = []
    g = 1
    while g < n:
        gaps.append(g)
        g = g * 3 + 1

    print(f"\nSecuencia de gaps (Knuth): {list(reversed(gaps))}\n" + "─" * 50)

    for gap in reversed(gaps):
        print(f"\n[Gap = {gap}]  arreglo: {a}")

        for i in range(gap, n):
            tmp = a[i]
            j   = i
            print(f"  insertar {tmp} en posición {i}", end="")

            while j >= gap:
                comparaciones += 1
                if a[j - gap] > tmp:
                    a[j] = a[j - gap]
                    intercambios += 1
                    j -= gap
                else:
                    break

            a[j] = tmp
            if j != i:
                print(f" → movido a posición {j}  |  {a}")
            else:
                print(f" → sin mover")

    return a

# ─── Ejecución ────────────────────────────────────────────────────────────────
print("\n" + "─" * 50)
ordenada = shell_sort(ldes)
print("\n" + "─" * 50)
print("\nArreglo ordenado :", ordenada)
print(f"Comparaciones    : {comparaciones}")
print(f"Intercambios     : {intercambios}")
