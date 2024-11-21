import random
import pygame
import math
from collections import deque
from ship_environment_logic import ShipEnvironment
from knowledge_base import KnowledgeBase
from bot import Bot
from rat import Rat
from rat_knowledge_base import RatKnowledgeBase



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
ALPHA = 0.2

class Simulation:
    def __init__(self):
        self.environment = ShipEnvironment(size=GRID_SIZE)
        self.kbase = KnowledgeBase(self.environment)
        self.bot = Bot(self.environment, self.kbase)
        self.rat = Rat(self.environment, self.bot.loc)
        self.goal_cells = []
        self.bfs_paths = []
        self.step_counter = 0  # here we are initialising step counter


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

            sensed_possible_moves = self.bot.sense_possible_moves()
            self.kbase.filter_locs(sensed_possible_moves)
            move_success = self.bot.move()
            self.step_counter += 1 if move_success else 0  # Increment step count on successful moves


            if not move_success or len(self.kbase.poss_locs) == 1:
                if len(self.kbase.poss_locs) == 1:
                    print("Bot has localized itself.")
                    bot_loc = list(self.kbase.poss_locs)[0]
                    rat_kbase = RatKnowledgeBase(self.environment, bot_loc)
                    filter_dist = 10  

                    while True:
                        # We are calculating the probability of a ping at the current loc
                        ping_probability = rat_kbase.highest_probability_ping(self.bot.loc, self.rat.loc)
                        hears_ping = ping_probability > 0.1
                        if hears_ping:
                            # Calculating a new filtering dist based on ping probability and alpha
                            filter_dist = max(1, int(2 * ((math.log(ping_probability) / -ALPHA) + 1)))
                            print(f"Ping detected with probability {ping_probability}. Filtering cells with dist <= {filter_dist}.")

                            # We are keeping a list of cells that are within `filter_dist` from the current bot location
                            close_cells = [
                                cell for cell in rat_kbase.rat_detection_probabilities.keys()
                                if rat_kbase.manhattan_dist(self.bot.loc, cell) <= filter_dist
                            ]
                            print(f"close cells are: {close_cells}")
                            
                            if close_cells:
        
                                ping_loc = self.bot.loc

                                while close_cells:
                                    # Selecting a random cell from the filtered `close_cells`
                                    goal_cell = random.choice(close_cells)
                                    path_to_goal = self.bfs_path(self.bot.loc, goal_cell)

                                    if path_to_goal:
                                        # Moving the bot along the path towards the chosen goal cell
                                        for step in range(1, len(path_to_goal)):
                                            next_step = path_to_goal[step]
                                            self.bot.loc = next_step
                                            self.step_counter += 1
                                            self.draw_grid(screen)
                                            pygame.display.flip()
                                            clock.tick(50)
                                            print(f"Bot moved to loc {next_step}.")

                                            # After each step, check if we hear a ping at the new bots location.
                                            ping_probability = rat_kbase.highest_probability_ping(self.bot.loc, self.rat.loc)
                                            hears_ping = ping_probability > 0.1

                                            if hears_ping:
                                                print(f"Ping heard again at {self.bot.loc} with probability {ping_probability}.")
                                               
                                                filter_dist = max(1, int(2 * ((math.log(ping_probability) / -ALPHA) + 1)))
                                                close_cells = [
                                                    cell for cell in close_cells
                                                    if rat_kbase.manhattan_dist(self.bot.loc, cell) <= filter_dist
                                                ]
                                                break  

                                        if self.bot.loc == self.rat.loc:
                                            print("Rat caught!")
                                            print(f"Total steps taken to catch the rat: {self.step_counter}")
                                            running = False
                                            break  

                                    else:
                                        
                                        print(f"No path to {goal_cell}. Returning to last ping loc {ping_loc}.")
                                        path_back_to_ping = self.bfs_path(self.bot.loc, ping_loc)
                                        for step in range(1, len(path_back_to_ping)):
                                            next_step = path_back_to_ping[step]
                                            self.bot.loc = next_step
                                            self.step_counter += 1
                                            self.draw_grid(screen)
                                            pygame.display.flip()
                                            clock.tick(50)
                                            print(f"Bot returned to ping loc {next_step}.")



                                        if self.bot.loc == self.rat.loc:
                                            print("Rat caught!")
                                            print(f"Total steps taken to catch the rat: {self.step_counter}")
                                            running = False
                                            break  



                        
                        else:
                            print("Ping not detected.")

                            # Update the rat knowledge base to include far off cells
                            rat_kbase.filter_cells_by_dist(10, greater_than=True)  

                            # Retrieve possible cells to move towards, filtered by dist
                            far_cells = list(rat_kbase.rat_detection_probabilities.keys())
                            
                            
                            if far_cells:
                                chosen_far_cell = random.choice(far_cells)
                                
                                # Using BFS algo to find a path towards the chosen far cell
                                path_to_far_cell = self.bfs_path(self.bot.loc, chosen_far_cell)
                                print(f"Planned BFS path to far cell {chosen_far_cell}: {path_to_far_cell}")
                                
                                # Move along the path, then check for a ping again
                                if path_to_far_cell:
                                    for step in range(1, len(path_to_far_cell)):
                                        next_step = path_to_far_cell[step]
                                        self.bot.loc = next_step  # Update the bot's location
                                        self.step_counter += 1  
                                        self.draw_grid(screen)
                                        pygame.display.flip()
                                        clock.tick(100)  
                                        print(f"Bot moved towards far cell to loc {next_step}.")

                                    # Once the bot reaches the chosen far cell, it will run the rat detctor and check for a ping again in the next iteration.


                        if self.bot.loc == self.rat.loc:
                            print("Rat caught!")
                            print(f"Total steps taken to catch the rat: {self.step_counter}")  
                            running = False
                            break

                        self.draw_grid(screen)
                        pygame.display.flip()
                        clock.tick(100)

        pygame.quit()





    def bfs_path(self, start, goal):
        """Perform BFS to find the shortest path from start to goal in the grid."""
        queue = deque([(start, [start])])  
        visited = set([start])

        while queue:
            current, path = queue.popleft()

            if current == goal:
                return path  

            
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  
                neighbor = (current[0] + dr, current[1] + dc)

                
                if (0 <= neighbor[0] < self.environment.size and 0 <= neighbor[1] < self.environment.size
                    and self.environment.matrix[neighbor[0]][neighbor[1]] == 0 and neighbor not in visited):
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None  

    def draw_grid(self, screen):
        for r in range(self.environment.size):
            for c in range(self.environment.size):
                rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if (r, c) == self.bot.loc:
                    pygame.draw.rect(screen, BLUE, rect)
                elif (r, c) == self.rat.loc:
                    pygame.draw.rect(screen, GREEN, rect)
                elif self.environment.matrix[r][c] == 1:
                    pygame.draw.rect(screen, GRAY, rect)
                else:
                    pygame.draw.rect(screen, YELLOW, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)
