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
        self.environment = ShipEnvironment(size=GRID_SIZE)
        self.kbase = KnowledgeBase(self.environment)
        self.bot = Bot(self.environment, self.kbase)
        self.rat = Rat(self.environment, self.bot.loc)
        self.real_detection_probability = None  # Initialize real_detection_probability as None
        self.goal_cells = []  # Initialize goal_cell
        self.bfs_paths = []  # To store all BFS paths to each goal cell


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
            self.kbase.filter_locs(sensed_directions)
            move_success = self.bot.move()

            # If the bot cannot move or has localized itself, end the localization and move towards the rat
            if not move_success or len(self.kbase.eligible_locs) == 1:
                if len(self.kbase.eligible_locs) == 1:
                    print("Simulation complete: Bot has located itself.")
                    bot_loc = list(self.kbase.eligible_locs)[0]
                    print(f"Bot's detected loc: {bot_loc}")

                    # Create Rat Knowledge Base after bot localization
                    rat_kbase = RatKnowledgeBase(self.environment, bot_loc, alpha=0.5)
                    self.goal_cells = [cell for cell, _ in rat_kbase.rat_detection_probabilities.items()]

                    # Repeat the refinement process until only one goal cell remains
                    while True:
                        self.draw_grid(screen)  # Draw current state
                        pygame.display.flip()  # Update the screen
                        clock.tick(1)  # Slow down for visibility

                        # Calculate real detection probability from the rat's real loc to the bot's loc
                        self.real_detection_probability = self.calculate_real_detection_probability(
                            self.bot.loc, self.rat.loc, alpha=0.5
                        )
                        self.goal_cells = self.find_matching_probability_cell(rat_kbase)
                        rat_kbase.filter_to_goal_cells(self.goal_cells)

                        # If only one goal cell remains, end the refinement loop
                        if len(self.goal_cells) == 1:
                            final_goal = self.goal_cells[0]
                            final_path = self.bfs_path(self.bot.loc, final_goal)
                            if final_path:
                                self.bot.set_goal_path(final_path, rat_kbase)
                            running = False
                            break

                        # Generate BFS paths to each goal cell
                        self.bfs_paths.clear()
                        for goal in self.goal_cells:
                            path = self.bfs_path(self.bot.loc, goal)
                            if path:
                                self.bfs_paths.append(path)

                        # Choose a path to follow from the generated BFS paths
                        if self.bfs_paths:
                            chosen_path = random.choice(self.bfs_paths)
                            self.bot.set_goal_path(chosen_path, rat_kbase)
                            self.bot.move_to_goal()

                        self.draw_grid(screen)  # Draw the modifyd grid after moving to the goal
                        pygame.display.flip()
                        clock.tick(2)  # Control the speed for better observation

                # Visualize the final path to the rat after localization
                if self.bot.goal_path:
                    while self.bot.goal_path:
                        # Move the bot to the next step in the final path
                        self.bot.move_to_goal()
                        self.draw_grid(screen)
                        pygame.display.flip()
                        clock.tick(2)  # Slow down for better observation of each final move
                    print("Final path completed. Bot has reached the rat.")
                    running = False  # End simulate after reaching the rat

            # Draw the grid and modify the display during the localization phase
            self.draw_grid(screen)
            pygame.display.flip()
            clock.tick(5)  # FPS for localization phase

        pygame.quit()


    def calculate_real_detection_probability(self, bot_loc, rat_loc, alpha):
        """Calculate the real detection probability based on the formula."""
        # Manhattan dist between bot and rat
        dist = abs(bot_loc[0] - rat_loc[0]) + abs(bot_loc[1] - rat_loc[1])
        # Detection probability using the given formula
        detection_probability = math.exp(-alpha * (dist - 1))
        print(f"Real detection probability from rat at {rat_loc} to bot at {bot_loc}: {detection_probability}")
        return detection_probability
    

    def find_matching_probability_cell(self, rat_kbase):
        """Find all cells in RatKnowledgeBase that match the real detection probability."""
        matching_cells = []
        if self.real_detection_probability is None:
            # print("Real detection probability not set. Exiting search for matching cells.")
            return matching_cells

        for cell, probability in rat_kbase.rat_detection_probabilities.items():
            if math.isclose(probability, self.real_detection_probability, rel_tol=1e-9):
                matching_cells.append(cell)
        
        # print(f"Found goal cells with matching detection probability: {matching_cells}")
        return matching_cells

    def bfs_path(self, start, goal):
        """Perform BFS to find the shortest path from start to goal in the grid."""
        queue = deque([(start, [start])])  # Queue holds tuples of (current cell, path to this cell)
        visited = set([start])

        while queue:
            current, path = queue.popleft()

            if current == goal:
                return path  # Return the path when goal is reached

            # Explore neighbors
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # N, S, W, E directions
                neighbor = (current[0] + dr, current[1] + dc)

                # Check if the neighbor is within bounds and is an open cell
                if (0 <= neighbor[0] < self.environment.size and 0 <= neighbor[1] < self.environment.size
                    and self.environment.matrix[neighbor[0]][neighbor[1]] == 0 and neighbor not in visited):
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None  # No path found if we exit the loop without reaching the goal


    def draw_grid(self, screen):
        for r in range(self.environment.size):
            for c in range(self.environment.size):
                rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if (r, c) == self.bot.loc:
                    pygame.draw.rect(screen, BLUE, rect)  # Bot's loc
                elif (r, c) == self.rat.loc:
                    pygame.draw.rect(screen, GREEN, rect)  # Rat's loc
                elif self.environment.matrix[r][c] == 1:
                    pygame.draw.rect(screen, GRAY, rect)  # Blocked cells
                else:
                    pygame.draw.rect(screen, YELLOW, rect)  # Open cells
                pygame.draw.rect(screen, BLACK, rect, 1)  # Grid lines
