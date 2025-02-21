import os
import itertools
import subprocess
import numpy as np
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import INPUTS_3D


# Charger un puzzle Picross 3D depuis un fichier
def load_picross3d(filename):
    path = os.path.join(INPUTS_3D, filename)
    with open(path, "r") as file:
        lines = [line.strip() for line in file.readlines()]

    width, height, depth = map(int, lines[0].split())
    sides = {0: [], 1: [], 2: []}

    index = 1
    expected_lines = {0: height, 1: depth, 2: width}  # Nombre de lignes attendues par face

    # saut de ligne
    while index < len(lines) and not lines[index]:
        index+=1

    for side in range(3):
        sides[side] = []
        for _ in range(expected_lines[side]):
            if index < len(lines) and lines[index]:  # Vérifie qu'on ne dépasse pas
                sides[side].append(lines[index].split())
                index += 1
        while index < len(lines) and not lines[index]:  # Sauter les lignes vides
            index += 1

    return width, height, depth, sides


# Générer les contraintes SAT
def generate_sat_constraints(width, height, depth, sides):
    variables = {}
    clauses = []

    # Assigner une variable à chaque voxel (x, y, z)
    var_count = 1
    for x, y, z in itertools.product(range(width), range(height), range(depth)):
        variables[(x, y, z)] = var_count
        var_count += 1

    # Contraintes de remplissage
    for side, grid in sides.items():
        dim1, dim2, dim3 = (width, height, depth) if side == 0 else (height, depth, width) if side == 1 else (depth, width, height)

        for d1 in range(dim1):
            for d2 in range(dim2):
                if d1 < len(grid) and d2 < len(grid[d1]):
                    clue = grid[d1][d2]
                    if clue.isdigit():
                        num_blocks = int(clue)
                        line_vars = [
                            variables[(d1, d2, d3)] if side == 0 else
                            variables[(d3, d1, d2)] if side == 1 else
                            variables[(d2, d3, d1)]
                            for d3 in range(dim3)
                        ]

                        # Contraintes CNF : exactement `num_blocks` parmi `line_vars` doivent être vrais
                        # Clause d'au moins `num_blocks` actifs (sous forme de clauses disjonctives)
                        for subset in itertools.combinations(line_vars, len(line_vars) - num_blocks + 1):
                            clause = " ".join(map(str, subset)) + " 0"
                            if clause not in clauses:  # Éviter les répétitions
                                clauses.append(clause)

                        # Clause d'au plus `num_blocks` actifs (négation en paires)
                        for subset in itertools.combinations(line_vars, num_blocks + 1):
                            clause = " ".join(f"-{var}" for var in subset) + " 0"
                            if clause not in clauses:  # Éviter les répétitions
                                clauses.append(clause)

                        # Debug: Imprimer les contraintes générées pour chaque ligne
                        print(f"Side {side}, Line ({d1}, {d2}), Clue {clue}:")
                        print(f"  At least {num_blocks}: {[subset for subset in itertools.combinations(line_vars, len(line_vars) - num_blocks + 1)]}")
                        print(f"  At most {num_blocks}: {[subset for subset in itertools.combinations(line_vars, num_blocks + 1)]}")

    return variables, clauses




# Résoudre le SAT avec Gophersat
def solve_sat(clauses):
    num_vars = max(max(map(abs, map(int, clause.split()))) for clause in clauses) if clauses else 0
    cnf = f"p cnf {num_vars} {len(clauses)}\n" + "\n".join(clauses)

    with open("temp.cnf", "w") as file:
        file.write(cnf+"\n")

    print("\n===== CNF GENERATED =====")
    with open("temp.cnf", "r") as file:
        print(file.read())  # Debug: voir le contenu du fichier CNF

    result = subprocess.run(["gophersat", "temp.cnf"], capture_output=True, text=True)

    if result.returncode == 0:
        print("\n===== GOPHERSAT OUTPUT =====")
        print(result.stdout)  # Afficher la sortie de Gophersat
    else:
        print("\n===== GOPHERSAT ERROR =====")
        print(result.stderr)  # Afficher l'erreur de Gophersat

    return result.stdout



# Charger un puzzle et résoudre
if __name__ == "__main__":
    width, height, depth, sides = load_picross3d("LittlePuzzle.txt")
    print(width, height, depth)
    print("side 0:")
    print(sides[0])
    print("side 1:")
    print(sides[1])
    print("side 2:")
    print(sides[2])
    variables, clauses = generate_sat_constraints(width, height, depth, sides)
    solution = solve_sat(clauses)
