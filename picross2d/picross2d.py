import sys
import tkinter as tk
import time
import os
import subprocess
from typing import List
from constraint import Problem, ExactSumConstraint
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DATA_DIR
from config import INPUTS_2D
import argparse


def load_hints(filename):
    with open(filename, "r") as file:
        lines = [line.strip() for line in file.readlines()]
    
    rows = int(lines[0])
    cols = int(lines[1])
    row_hints = lines[2:2+rows]
    col_hints = lines[2+rows:2+rows+cols]
    return rows, cols, row_hints, col_hints

def load_grid(filename):
    with open(filename, "r") as file:
        return [list(line.strip()) for line in file.readlines()]

def draw_nonogram(root, grid_filename: str, hints_filename: str):
    grid = load_grid(grid_filename)
    rows, cols, row_hints, col_hints = load_hints(hints_filename)
    cell_size = 18  # Taille des cases
    offset_x = 50  # Décalage pour la grille
    offset_y = 50  # Décalage pour la grille
    
    canvas = tk.Canvas(root, width=offset_x + cols * cell_size + 50, height=offset_y + rows * cell_size + 50)
    canvas.pack()
    
    # Dessiner la grille
    for i in range(rows + 1):
        canvas.create_line(offset_x, offset_y + i * cell_size, offset_x + cols * cell_size, offset_y + i * cell_size)
    for j in range(cols + 1):
        canvas.create_line(offset_x + j * cell_size, offset_y, offset_x + j * cell_size, offset_y + rows * cell_size)
    
    # Afficher les indices des lignes à droite
    for i, hint in enumerate(row_hints):
        canvas.create_text(offset_x + cols * cell_size + 10, offset_y + i * cell_size + cell_size // 2, text=hint, anchor='w', font=('Arial', 6))
    
    # Afficher les indices des colonnes en bas
    for j, hint in enumerate(col_hints):
        hint_numbers = hint.split()  # Séparer les nombres
        for k, number in enumerate(hint_numbers):
            canvas.create_text(
                offset_x + j * cell_size + cell_size // 2, 
                offset_y + rows * cell_size + 10 + k * 8,  # Décalage progressif vers le bas
                text=number, 
                anchor='n', 
                font=('Arial', 6)
            )

    # Fonction pour colorier progressivement les cases
    def animate_fill():
        for i in range(rows):
            for j in range(cols):
                if grid[i][j] == 'X':
                    canvas.create_rectangle(
                        offset_x + j * cell_size, offset_y + i * cell_size,
                        offset_x + (j + 1) * cell_size, offset_y + (i + 1) * cell_size,
                        fill='black'
                    )
                    root.update()
                    time.sleep(0.005)
    
    root.after(100, animate_fill)

# function to solve the nonogram
def var(i: int, j: int, cols: int) -> int:
    return i * cols + j + 1

def aux_var(counter: List[int]) -> int:
    counter[0] += 1
    return counter[0]

def get_intervals(Nb: int, Max: int) -> List[List[int]]:
    min_vals = list(range(Max + 1))   # Valeurs possibles pour la première et la dernière variable
    max_vals = list(range(1, Max + 1)) # Valeurs possibles pour les autres variables
    
    problem = Problem()
    # Générer des noms de variables dynamiquement
    variable_names = [f"var_{i}" for i in range(Nb + 1)]
    
    # Ajouter la première variable (peut être entre 0 et Max)
    problem.addVariable(variable_names[0], min_vals)
    
    # Ajouter les variables intermédiaires (entre 1 et Max)
    for i in range(1, Nb):
        problem.addVariable(variable_names[i], max_vals)
    
    # Ajouter la dernière variable (peut être entre 0 et Max)
    problem.addVariable(variable_names[Nb], min_vals)
    
    # Ajouter la contrainte de somme exacte
    problem.addConstraint(ExactSumConstraint(Max))
    
    # Récupérer les solutions
    Res = problem.getSolutions()
    Resultat = []
    
    # Reformater les résultats en liste de listes
    for r in Res:
        item = [r[var] for var in variable_names]
        Resultat.append(item)
    
    return Resultat

def encode_row_constraints(rows: int, cols: int, row_hints: List[str], clauses: List[List[int]], aux_counter: List[int]) -> None:
    for row, hint in enumerate(row_hints):
        blocks = list(map(int, hint.split()))
        total_blocks = sum(blocks)
        
        if cols - total_blocks < len(blocks) - 1:
            continue  # Skip invalid constraints
        
        possible_intervals = get_intervals(len(blocks), cols - total_blocks)
        
        conditions = []
        for interval in possible_intervals:
            cond = aux_var(aux_counter)
            conditions.append(cond)
            pos = 0
            noire_counter = 0
            for i in range(len(interval)-1):
                for j in range(interval[i]):
                    clauses.append([-cond, -var(row, pos, cols)])
                    pos += 1
                for k in range(blocks[noire_counter]):
                    clauses.append([-cond, var(row, pos, cols)])
                    pos += 1
                noire_counter += 1
            for _ in range(interval[-1]):
                clauses.append([-cond, -var(row, pos, cols)])
                pos += 1
        clauses.append(conditions)

def encode_col_constraints(rows: int, cols: int, col_hints: List[str], clauses: List[List[int]], aux_counter: List[int]) -> None:
    for idx, hint in enumerate(col_hints):
        blocks = list(map(int, hint.split()))
        total_blocks = sum(blocks)
        
        if rows - total_blocks < len(blocks) - 1:
            continue  # Skip invalid constraints
        
        possible_intervals = get_intervals(len(blocks), rows - total_blocks)
        
        conditions = []
        for interval in possible_intervals:
            cond = aux_var(aux_counter)
            conditions.append(cond)
            pos = 0
            noire_counter = 0
            for i in range(len(interval)-1):
                for j in range(interval[i]):
                    clauses.append([-cond, -var(pos, idx, cols)])
                    pos += 1
                for k in range(blocks[noire_counter]):
                    clauses.append([-cond, var(pos, idx, cols)])
                    pos += 1
                noire_counter += 1
            for _ in range(interval[-1]):
                clauses.append([-cond, -var(pos, idx, cols)])
                pos += 1
        clauses.append(conditions)

def solve_picross2d(hints_filename: str, output_filename: str) -> None:
    rows, cols, row_hints, col_hints = load_hints(hints_filename)
    cnf_filename = "temp.cnf"
    
    clauses: List[List[int]] = []
    aux_counter = [rows * cols]  # Start auxiliary variables after grid variables
    
    encode_row_constraints(rows, cols, row_hints, clauses, aux_counter)
    encode_col_constraints(rows, cols, col_hints, clauses, aux_counter)
    
    with open(cnf_filename, "w") as f:
        f.write(f"p cnf {aux_counter[0]} {len(clauses)}\n")
        for clause in clauses:
            f.write(" ".join(map(str, clause)) + " 0\n")
    
    # Run Gophersat solver
    result = subprocess.run(["gophersat", cnf_filename], capture_output=True, text=True)
    
    if "UNSAT" in result.stdout:
        print("No solution found.")
        with open(output_filename, "w") as f:
            f.write("No solution found.\n")
    else:
        # Get the solution
        solution = result.stdout.split("\n")[2].split()
        solution.pop(0)  # Remove trailing empty string
        
        # Initialize an empty grid
        solution_grid = [["." for _ in range(cols)] for _ in range(rows)]
        
        # Process the solution
        for var in solution[:rows * cols]:
            var = int(var)
            if var > 0:
                # Find the corresponding grid cell for this variable
                i, j = divmod(var - 1, cols)  # Convert variable to (row, col)
                solution_grid[i][j] = 'X'
            elif var < 0:
                var = -var
                i, j = divmod(var - 1, cols)  # Convert variable to (row, col)
                solution_grid[i][j] = '.'

        # Write the solution grid to the output file
        with open(output_filename, "w") as f:
            for row in solution_grid:
                f.write("".join(row) + "\n")
        
        # Optionally print the grid
        for row in solution_grid:
            print("".join(row))

def main():
    parser = argparse.ArgumentParser(description="Solve a Picross 2D puzzle and visualize the result.")
    parser.add_argument("--input_filename", type=str, required=True, help="Name of the input file (e.g., cactus.txt)")

    args = parser.parse_args()
    input_filename = args.input_filename
    script_dir = os.path.dirname(os.path.abspath(__file__))

    hints_filename = os.path.join(script_dir, "..",INPUTS_2D,input_filename)
    output_filename = os.path.join(script_dir, "..","data","outputs-2D", input_filename.replace(".txt", "_solution.txt"))

    solve_picross2d(hints_filename, output_filename)
    # Création de la fenêtre Tkinter
    root = tk.Tk()
    root.title("Nonogram")
    draw_nonogram(root, output_filename, hints_filename)
    root.mainloop()

if __name__ == "__main__":
    main()