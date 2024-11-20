import random
import pygame
import math
from collections import deque
from knowledge_base import KnowledgeBase
from bot import Bot
from rat import Rat
from rat_knowledge_base import RatKnowledgeBase
from ship_environment_logic import ShipEnvironment

# Constants for colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)      # Bot
GRAY = (50, 50, 50)     # Blocked cells
YELLOW = (200, 200, 200)  # Open cells
GREEN = (0, 255, 0)     # Rat


# Constants for the grid and cell size
CELL_SIZE = 20
GRID_SIZE = 30
SCREEN_SIZE = CELL_SIZE * GRID_SIZE

class Simulation:
    def __init__(self):
        self.env = ShipEnvironment(size=GRID_SIZE)
        self.kb = KnowledgeBase(self.env)
        self.bot = Bot(self.env, self.kb)
        self.rat = Rat(self.env, self.bot.position)
        self.real_detection_probability = None  # Initialize real_detection_probability as None
        self.target_cells = []  # Initialize target_cell
        self.bfs_paths = []  # To store all BFS paths to each target cell


    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        pygame.display.set_caption('Bot Localization Simulation')
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Run the bot localization process
            sensed_directions = self.bot.sense_directions()
            self.kb.filter_positions(sensed_directions)
            move_success = self.bot.move()

            # If the bot cannot move or has localized itself, end the localization and move towards the rat
            if not move_success or len(self.kb.possible_positions) == 1:
                if len(self.kb.possible_positions) == 1:
                    print("Simulation complete: Bot has located itself.")
                    bot_position = list(self.kb.possible_positions)[0]
                    print(f"Bot's detected location: {bot_position}")

                    # Create Rat Knowledge Base after bot localization
                    rat_kb = RatKnowledgeBase(self.env, bot_position, alpha=0.5)
                    self.target_cells = [cell for cell, _ in rat_kb.rat_detection_probabilities.items()]

                    # Repeat the refinement process until only one target cell remains
                    while True:
                        self.draw_grid(screen)  # Draw current state
                        pygame.display.flip()  # Update the screen
                        clock.tick(1)  # Slow down for visibility

                        # Calculate real detection probability from the rat's real position to the bot's position
                        self.real_detection_probability = self.calculate_real_detection_probability(
                            self.bot.position, self.rat.position, alpha=0.5
                        )
                        self.target_cells = self.find_matching_probability_cell(rat_kb)
                        rat_kb.filter_to_target_cells(self.target_cells)

                        # If only one target cell remains, end the refinement loop
                        if len(self.target_cells) == 1:
                            final_target = self.target_cells[0]
                            final_path = self.bfs_path(self.bot.position, final_target)
                            if final_path:
                                self.bot.set_target_path(final_path, rat_kb)
                            running = False
                            break

                        # Generate BFS paths to each target cell
                        self.bfs_paths.clear()
                        for target in self.target_cells:
                            path = self.bfs_path(self.bot.position, target)
                            if path:
                                self.bfs_paths.append(path)

                        # Choose a path to follow from the generated BFS paths
                        if self.bfs_paths:
                            chosen_path = random.choice(self.bfs_paths)
                            self.bot.set_target_path(chosen_path, rat_kb)
                            self.bot.move_to_target()

                        self.draw_grid(screen)  # Draw the updated grid after moving to the target
                        pygame.display.flip()
                        clock.tick(2)  # Control the speed for better observation

                # Visualize the final path to the rat after localization
                if self.bot.target_path:
                    while self.bot.target_path:
                        # Move the bot to the next step in the final path
                        self.bot.move_to_target()
                        self.draw_grid(screen)
                        pygame.display.flip()
                        clock.tick(2)  # Slow down for better observation of each final move
                    print("Final path completed. Bot has reached the rat.")
                    running = False  # End simulation after reaching the rat

            # Draw the grid and update the display during the localization phase
            self.draw_grid(screen)
            pygame.display.flip()
            clock.tick(5)  # FPS for localization phase

        pygame.quit()


    def calculate_real_detection_probability(self, bot_position, rat_position, alpha):
        """Calculate the real detection probability based on the formula."""
        # Manhattan distance between bot and rat
        distance = abs(bot_position[0] - rat_position[0]) + abs(bot_position[1] - rat_position[1])
        # Detection probability using the given formula
        detection_probability = math.exp(-alpha * (distance - 1))
        print(f"Real detection probability from rat at {rat_position} to bot at {bot_position}: {detection_probability}")
        return detection_probability
    

    def find_matching_probability_cell(self, rat_kb):
        """Find all cells in RatKnowledgeBase that match the real detection probability."""
        matching_cells = []
        if self.real_detection_probability is None:
            # print("Real detection probability not set. Exiting search for matching cells.")
            return matching_cells

        for cell, probability in rat_kb.rat_detection_probabilities.items():
            if math.isclose(probability, self.real_detection_probability, rel_tol=1e-9):
                matching_cells.append(cell)
        
        # print(f"Found target cells with matching detection probability: {matching_cells}")
        return matching_cells

    def bfs_path(self, start, target):
        """Perform BFS to find the shortest path from start to target in the grid."""
        queue = deque([(start, [start])])  # Queue holds tuples of (current cell, path to this cell)
        visited = set([start])

        while queue:
            current, path = queue.popleft()

            if current == target:
                return path  # Return the path when target is reached

            # Explore neighbors
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # N, S, W, E directions
                neighbor = (current[0] + dr, current[1] + dc)

                # Check if the neighbor is within bounds and is an open cell
                if (0 <= neighbor[0] < self.env.size and 0 <= neighbor[1] < self.env.size
                    and self.env.matrix[neighbor[0]][neighbor[1]] == 0 and neighbor not in visited):
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None  # No path found if we exit the loop without reaching the target


    def draw_grid(self, screen):
        for r in range(self.env.size):
            for c in range(self.env.size):
                rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if (r, c) == self.bot.position:
                    pygame.draw.rect(screen, BLUE, rect)  # Bot's position
                elif (r, c) == self.rat.position:
                    pygame.draw.rect(screen, GREEN, rect)  # Rat's position
                elif self.env.matrix[r][c] == 1:
                    pygame.draw.rect(screen, GRAY, rect)  # Blocked cells
                else:
                    pygame.draw.rect(screen, YELLOW, rect)  # Open cells
                pygame.draw.rect(screen, BLACK, rect, 1)  # Grid lines
