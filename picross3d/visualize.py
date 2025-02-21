import glfw
from OpenGL.GL import *
import imgui
from imgui.integrations.glfw import GlfwRenderer
import itertools
import time
from picross3d import load_picross3d, generate_sat_constraints, solve_sat

# Initialisation de GLFW
if not glfw.init():
    raise Exception("GLFW cannot be initialized")

# Création de la fenêtre
window = glfw.create_window(1200, 600, "Picross 3D Solver", None, None)
if not window:
    glfw.terminate()
    raise Exception("Window cannot be created")

glfw.make_context_current(window)
glEnable(GL_DEPTH_TEST)

# Initialisation d'ImGui
imgui.create_context()
impl = GlfwRenderer(window)

# Charger le puzzle
width, height, depth, sides = load_picross3d("LittlePuzzle.txt")
variables, clauses = generate_sat_constraints(width, height, depth, sides)

# Variables pour la gestion de l'affichage
solution = None
solving_time = 0
is_solved = False

# Dessiner un cube
def draw_cube(x, y, z, size):
    vertices = [
        (x, y, z), (x + size, y, z), (x + size, y + size, z), (x, y + size, z),
        (x, y, z + size), (x + size, y, z + size), (x + size, y + size, z + size), (x, y + size, z + size)
    ]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]

    glBegin(GL_LINES)
    for edge in edges:
        glVertex3fv(vertices[edge[0]])
        glVertex3fv(vertices[edge[1]])
    glEnd()

# Dessiner le puzzle Picross 3D
def draw_picross(width, height, depth):
    for x, y, z in itertools.product(range(width), range(height), range(depth)):
        draw_cube(x, y, z, 1)

def main():
    global solution, solving_time, is_solved

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        imgui.new_frame()

        # Dessiner le puzzle Picross 3D
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -10)

        # Appliquer la rotation (à implémenter)
        # glRotatef(rotation_x, 1, 0, 0)
        # glRotatef(rotation_y, 0, 1, 0)

        draw_picross(width, height, depth)

        # Afficher la sidebar avec les informations sur l'instance
        window_width, window_height = glfw.get_window_size(window)
        imgui.set_next_window_position(0, 0)
        imgui.set_next_window_size(300, window_height)
        imgui.begin("Sidebar", flags=imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_COLLAPSE)
        imgui.text(f"Dimensions: {width}x{height}x{depth}")
        imgui.text(f"Nombre de variables: {len(variables)}")
        imgui.text(f"Nombre de clauses: {len(clauses)}")
        imgui.text(f"Temps de résolution: {solving_time:.2f} secondes" if is_solved else "Temps de résolution: N/A")
        imgui.text(f"Solution: {'Trouvée' if is_solved else 'Non résolue'}")

        if imgui.button("Play"):
            start_time = time.time()
            solution = solve_sat(clauses)
            solving_time = time.time() - start_time
            is_solved = solution is not None

        imgui.end()

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()

if __name__ == "__main__":
    main()
