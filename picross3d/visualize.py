"""Module de visualisation de la solution d'un picross 3D avec vpython et imgui"""
"""NB: Non utilisé dans le projet final"""

import glfw
from OpenGL.GL import *
import imgui
from imgui.integrations.glfw import GlfwRenderer
import time
from picross3d import Picross3D


def main():
    # Initialisation de GLFW et OpenGL
    if not glfw.init():
        raise Exception("GLFW cannot be initialized")

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
    puzzle = Picross3D("LittlePuzzle.txt")

    # Résoudre le puzzle
    solution = puzzle.solve()

    # Affichage de la solution avec vpython
    if solution:
        puzzle.visualize_solution(solution)
    
    # Boucle principale de l'interface
    while not glfw.window_should_close(window):
        glfw.poll_events()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        impl.process_inputs()
        imgui.new_frame()

        # Afficher les informations sur la solution
        imgui.text("Solution affichée en 3D")
        
        imgui.render()
        impl.render(imgui.get_draw_data())

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()


