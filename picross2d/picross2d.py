import tkinter as tk
import time

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

def draw_nonogram(root, row_hints, col_hints, grid, rows, cols):
    cell_size = 40  # Taille des cases
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
        canvas.create_text(offset_x + cols * cell_size + 10, offset_y + i * cell_size + cell_size // 2, text=hint, anchor='w', font=('Arial', 12))
    
    # Afficher les indices des colonnes en bas
    for j, hint in enumerate(col_hints):
        canvas.create_text(offset_x + j * cell_size + cell_size // 2, offset_y + rows * cell_size + 10, text=hint, anchor='n', font=('Arial', 12))
    
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
                    time.sleep(0.1)
    
    root.after(100, animate_fill)

# Chargement des fichiers texte
hints_filename = "data/cactus.txt"
grid_filename = "data/cactus_sol.txt"
rows, cols, row_hints, col_hints = load_hints(hints_filename)
grid = load_grid(grid_filename)

# Création de la fenêtre Tkinter
root = tk.Tk()
root.title("Nonogram")
draw_nonogram(root, row_hints, col_hints, grid, rows, cols)
root.mainloop()
