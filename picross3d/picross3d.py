import itertools
import subprocess
import os
import sys
import pyvista as pv
import numpy as np

INPUTS_3D = os.path.join("data", "inputs-3D")



class Picross3D:
    def __init__(self, filename):
        """ Constructeur : Charge un puzzle depuis un fichier """
        self.width, self.height, self.depth, self.sides = self.load_picross3d(filename)
        self.variables = {}
        self.clauses = []
        self.solution = None
        self.numLiterals = 1  # Pour commencer à générer les variables
        self.indices = self.init_indices()  # Initialisation des indices
        self.generate_constraints()  # Génération des contraintes

    def load_picross3d(self, filename):
        """ Charge un puzzle Picross 3D depuis un fichier """
        path = os.path.join(INPUTS_3D, filename)
        with open(path, "r") as file:
            lines = [line.strip() for line in file.readlines()]

        width, height, depth = map(int, lines[0].split())
        sides = {0: [], 1: [], 2: []}

        index = 1
        expected_lines = {0: height, 1: depth, 2: width}

        while index < len(lines) and not lines[index]:
            index += 1

        for side in range(3):
            sides[side] = []
            for _ in range(expected_lines[side]):
                if index < len(lines) and lines[index]:
                    sides[side].append(lines[index].split())
                    index += 1
            while index < len(lines) and not lines[index]:
                index += 1

        return width, height, depth, sides

    def init_indices(self):
        """ Initialise les indices des variables SAT pour chaque bloc du puzzle """
        indices = {}
        for x in range(self.width):
            for y in range(self.height):
                for z in range(self.depth):
                    indices[(x, y, z)] = self.numLiterals
                    self.variables[(x, y, z)] = self.numLiterals  # Track the variable
                    self.numLiterals += 1
        return indices


    def generate_constraints(self):
        """ Génère les contraintes SAT pour chaque face du puzzle """
        for sideIndex in range(len(self.sides)):
            side = self.sides[sideIndex]
            for rowIndex in range(len(side)):
                row = side[rowIndex]
                for colIndex in range(len(row)):
                    col = row[colIndex]
                    if col != '-':
                        stack = self.get_stack_of_blocks(sideIndex, rowIndex, colIndex)
                        if col[0] == '(':
                            sideNum = int(col[1])
                            self.clauses.extend(self.PLSentencesCircleStack(stack, sideNum))
                        elif col[0] == '[':
                            sideNum = int(col[1])
                            self.clauses.extend(self.PLSentencesSquareStack(stack, sideNum))
                        else:
                            sideNum = int(col)
                            self.clauses.extend(self.PLSentencesPlainStack(stack, sideNum))

    def get_stack_of_blocks(self, sideIndex, rowIndex, colIndex):
        """ Retourne la liste des blocs dans une pile donnée par les indices du puzzle """
        stack = []
        if sideIndex == 0:
            y = rowIndex
            z = colIndex
            for x in range(self.width):
                stack.append(self.indices[(x, y, z)])
        elif sideIndex == 1:
            x = self.width - rowIndex - 1
            z = colIndex
            for y in range(self.height):
                stack.append(self.indices[(x, y, z)])
        elif sideIndex == 2:
            x = self.width - colIndex - 1
            y = rowIndex
            for z in range(self.depth):
                stack.append(self.indices[(x, y, z)])
        return stack

    def PLSentencesPlainStack(self, stack, sideNum):
        """ Construit les clauses CNF pour une pile de blocs (plain number) """
        sentences = []
        if sideNum == 0:
            # Pas de bloc dans cette pile
            for block in stack:
                sentences.append([-block])  # Le bloc n'est pas dans la solution
        elif sideNum == len(stack):
            # Tous les blocs dans cette pile doivent être dans la solution
            for block in stack:
                sentences.append([block])  # Le bloc est dans la solution
        else:
            # Constructeur pour exactement "sideNum" blocs dans cette pile
            combos = list(itertools.combinations(stack, len(stack) - sideNum + 1))
            for combo in combos:
                sentences.append(list(combo))

            combos = list(itertools.combinations(stack, sideNum + 1))
            for c in combos:
                combo = list(c)
                for i in range(len(combo)):
                    combo[i] *= -1
                sentences.append(combo)

            # Les blocs doivent apparaître dans une ligne continue
            for start in range(len(stack)):
                for nextBlock in range(start + sideNum, len(stack)):
                    sentences.append([stack[start] * -1, stack[nextBlock] * -1])

        return sentences




    def PLSentencesCircleStack(self, stack, sideNum):
        """Construit les clauses CNF pour une pile avec un nombre exact de 2 groupes de blocs séparés par au moins un bloc vide.
        Example: stack de 4 blocs, sideNum = 2
        Les sols possibles sont:
        - 1 0 1 0
        - 0 1 0 1
        - 1 0 0 1
        (il faut au moins un bloc vide entre les 2 groupes continus de blocs)


        """
        sentences = []
        if sideNum == 0:
            # Pas de bloc dans cette pile
            for block in stack:
                sentences.append([-block])
        elif sideNum == len(stack):
            # Tous les blocs dans cette pile doivent être dans la solution
            for block in stack:
                sentences.append([block])
        else:
            # Construire les groupes de blocs
            for start in range(len(stack) - sideNum + 1):
                for end in range(start + sideNum, len(stack) + 1):
                    group = stack[start:end]
                    if len(group) == sideNum:
                        sentences.append(group)
            # Les groupes doivent être séparés par au moins un bloc vide
            for start in range(len(stack) - sideNum):
                for end in range(start + sideNum + 1, len(stack)):
                    group1 = stack[start:start + sideNum]
                    group2 = stack[end:end + sideNum]
                    sentences.append([group1[0] * -1, group2[0] * -1])

        return sentences
    
    def PLSentencesSquareStack(self, stack, sideNum):
        """
        Construit les clauses CNF pour une pile avec un nombre de 3+ groupes de blocs séparés par au moins un bloc vide.
        La difficulté ici est que l'on ne connait pas le nombre de groupes à l'avance. Pour cela on limite le nombre de groupes à la longueur de la pile - 2 (puisque au moins 2 blocs vides sont nécessaires pour séparer les groupes).
        Exemple: stack de 6 blocs, sideNum = 3
        Les solutions possibles sont:
        - 1 0 1 0 1 0
        - 0 1 0 1 0 1
        - 1 0 0 1 0 1
        - 1 0 1 0 0 1
        - 0 1 0 1 0 1
        """
        sentences = []
        if sideNum == 0:
            # Pas de bloc dans cette pile
            for block in stack:
                sentences.append([-block])
        elif sideNum == len(stack):
            # Tous les blocs dans cette pile doivent être dans la solution
            for block in stack:
                sentences.append([block])
        else:
            # Construire les groupes de blocs
            for numGroups in range(3, 5):
                for groupIndices in itertools.combinations(range(len(stack)), numGroups * sideNum):
                    groupIndices = list(groupIndices)
                    groups = [stack[i:i + sideNum] for i in groupIndices]
                    if all(len(group) == sideNum for group in groups):
                        for group in groups:
                            sentences.append(group)
                    else:
                        continue
                    # Les groupes doivent être séparés par au moins un bloc vide
                    for i in range(len(groups) - 1):
                        group1 = groups[i]
                        group2 = groups[i + 1]
                        sentences.append([group1[-1] * -1, group2[0] * -1])

        return sentences
    

    def solve(self):
        """ Résout le puzzle avec Gophersat """
        cnf = f"p cnf {self.numLiterals - 1} {len(self.clauses)}\n" + "\n".join(" ".join(map(str, clause)) + " 0" for clause in self.clauses)

        with open("temp.cnf", "w") as file:
            file.write(cnf + "\n")

        result = subprocess.run(["gophersat", "temp.cnf"], capture_output=True, text=True)

        if result.returncode == 0:
            print("Gophersat a résolu le puzzle avec succès")
            return result.stdout
        else:
            print("Erreur avec Gophersat", result.stderr)
            return None

    def print_solution(self, solution):
        """ Affiche la solution du puzzle """
        # Split solution into lines and filter out the non-solution part
        solution_lines = solution.splitlines()
        
        # Find the line with 'v ' and process the literals
        solution_values = []
        for line in solution_lines:
            if line.startswith('v '):
                solution_values = line.split()[1:]  # Skip 'v' and take the literals
        
        # Ensure solution_values is not empty
        if not solution_values:
            print("No solution found.")
            return

        # Convert solution literals to integers
        satisfied_vars = set(map(int, solution_values))
        
        for x in range(self.width):
            for y in range(self.height):
                for z in range(self.depth):
                    var_index = self.variables[(x, y, z)]  # Get the literal for this (x, y, z)
                    if var_index > 0:
                        print('1' if var_index in satisfied_vars else '0', end=' ')  # Positive literal means "1"
                    else:
                        print('0' if var_index in satisfied_vars else '1', end=' ')  # Negative literal means "0"
                print()
            print()



    def visualize_solution(self, solution):
        """ Affiche la solution du puzzle en 3D avec un mini-repère en haut à droite """

        # Extraire les valeurs de la solution SAT
        solution_lines = solution.splitlines()
        solution_values = []

        for line in solution_lines:
            if line.startswith('v '):
                solution_values = line.split()[1:]  # On saute le 'v' et on garde les littéraux

        if not solution_values:
            print("Aucune solution trouvée pour la visualisation.")
            return

        satisfied_vars = set(map(int, solution_values))  # Convertir en ensemble pour recherche rapide

        # Création du plot interactif
        plotter = pv.Plotter()

        # Ajout des cubes (blocs actifs en vert, inactifs en gris semi-transparent)
        for x in range(self.width):
            for y in range(self.height):
                for z in range(self.depth):
                    var_index = self.variables[(x, y, z)]  # Récupérer l'index SAT
                    
                    if var_index in satisfied_vars:
                        color = "green"  # Bloc actif
                        opacity = 1.0  # Opaque
                    else:
                        color = "gray"  # Bloc supprimé
                        opacity = 0.1  # Semi-transparent
                    
                    cube = pv.Cube(center=(x, y, z), x_length=1, y_length=1, z_length=1)
                    plotter.add_mesh(cube, color=color, opacity=opacity, show_edges=True)

        # Ajout du mini-repère 3D en haut à droite
        plotter.add_axes(interactive=True)  # Affiche un petit repère qui tourne avec la figure

        # Affichage interactif (rotation, zoom, etc.)
        plotter.show()




if __name__ == "__main__":
    puzzle = Picross3D("SquaredPuzzle_big.txt")
    solution = puzzle.solve()
    if solution:
        puzzle.print_solution(solution)
        puzzle.visualize_solution(solution)
