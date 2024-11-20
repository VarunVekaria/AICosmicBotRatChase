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
        self.env = ShipEnvironment(size=GRID_SIZE)
        self.kb = KnowledgeBase(self.env)
        self.bot = Bot(self.env, self.kb)
        self.rat = Rat(self.env, self.bot.position)
        self.target_cells = []
        self.bfs_paths = []
        self.step_counter = 0

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

            sensed_directions = self.bot.sense_directions()
            self.kb.filter_positions(sensed_directions)
            move_success = self.bot.move()
            self.rat.move_randomly()
            if move_success:
                self.step_counter += 1
                # Move rat immediately after bot moves
                #self.rat.move_randomly()


            if not move_success or len(self.kb.possible_positions) == 1:
                if len(self.kb.possible_positions) == 1:
                    print("Bot has localized itself.")
                    bot_position = list(self.kb.possible_positions)[0]
                    rat_kb = RatKnowledgeBase(self.env, bot_position)
                    filter_distance = 10


                    while True:
                        # Calculate the probability of a ping at the current location
                        # Rat moves randomly each step
                        
                        print(f"ratttttttttttttttttttt is at{self.rat.position}")
                        self.rat.move_randomly()
                        print(f"ratttttttttttttttttttt is nowwwww at{self.rat.position}")
                        # Calculate ping probability based on updated bot and rat positions
                        ping_probability = rat_kb.highest_probability_ping(self.bot.position, self.rat.position)
                        hears_ping = ping_probability > 0.1

                        if hears_ping:
                                      
                            # Calculate a new filtering distance based on ping probability and alpha
                            filter_distance = max(1, int(2 * ((math.log(ping_probability) / -ALPHA) + 1)))
                            print(f"Ping detected with probability {ping_probability}. Filtering cells with distance <= {filter_distance}.")

                            # Create a list of cells that are within `filter_distance` from the current bot position
                            close_cells = [
                                cell for cell in rat_kb.rat_detection_probabilities.keys()
                                if rat_kb.manhattan_distance(self.bot.position, cell) <= filter_distance
                            ]
                            print(f"close cells are: {close_cells}")
                            
                            if close_cells:
                                # Save the bot's current position where ping was heard
                                ping_position = self.bot.position

                                while close_cells:
                                    # Choose a random cell from the filtered `close_cells`
                                    target_cell = random.choice(close_cells)
                                    path_to_target = self.bfs_path(self.bot.position, target_cell)

                                    if path_to_target:
                                        # Move the bot along the path towards the chosen target cell
                                        for step in range(1, len(path_to_target)):
                                            next_step = path_to_target[step]
                                            self.bot.position = next_step
                                            self.step_counter += 1
                                            print(f"Rat is at {self.rat.position} and bot at {self.bot.position}")
                                            
                                            # Move the rat after each bot step
                                            self.rat.move_randomly()
                                            print(f"Rat is now at {self.rat.position} and bot at {self.bot.position}")
                                            
                                            # Draw the updated positions
                                            self.draw_grid(screen)
                                            pygame.display.flip()
                                            clock.tick(50)
                                            print(f"Bot moved to position {next_step}.")

                                            self.bot.recent_positions.append(self.bot.position)
                                            if self.bot.detect_osc():
                                                self.bot.force_move_out_of_osc(self, screen, clock)   
                                                break



                                            # After each step, check if we hear a ping at the new location
                                            ping_probability = rat_kb.highest_probability_ping(self.bot.position, self.rat.position)
                                            hears_ping = ping_probability > 0.1

                                            if hears_ping:
                                                print(f"Ping heard again at {self.bot.position} with probability {ping_probability}.")
                                                # Re-filter `close_cells` around this new position with a reduced `filter_distance`
                                                filter_distance = max(1, int(2 * ((math.log(ping_probability) / -ALPHA) + 1)))
                                                close_cells = [
                                                    cell for cell in close_cells
                                                    if rat_kb.manhattan_distance(self.bot.position, cell) <= filter_distance
                                                ]
                                                break  # Restart loop with updated `close_cells` based on new ping location

                                        if self.bot.position == self.rat.position:
                                            print("Rat caught!")
                                            print(f"Total steps taken to catch the rat: {self.step_counter}")
                                            running = False
                                            break  # Exit the loop immediately

                                    else:
                                        # No valid path, return to the last ping position and try another cell
                                        print(f"No path to {target_cell}. Returning to last ping position {ping_position}.")
                                        path_back_to_ping = self.bfs_path(self.bot.position, ping_position)
                                        for step in range(1, len(path_back_to_ping)):
                                            next_step = path_back_to_ping[step]
                                            self.bot.position = next_step
                                            self.rat.move_randomly()
                                            print(f"Rat is now at {self.rat.position} and bot at {self.bot.position}")
                                            
                                            self.step_counter += 1
                                            #self.rat.move_randomly()
                                            self.draw_grid(screen)
                                            pygame.display.flip()
                                            clock.tick(50)
                                            print(f"Bot returned to ping position {next_step}.")


                                    # Re-evaluate after moving halfway, preparing for the next ping detection
                                    #print(f"After moving halfway, bot position: {self.bot.position}.")
                                        if self.bot.position == self.rat.position:
                                            print("Rat caught!")
                                            print(f"Total steps taken to catch the rat: {self.step_counter}")
                                            running = False
                                            break  # Exit the loop immediately



                        
                        else:
                            print("Ping not detected.")

                            # Update the rat knowledge base to include only cells with a Manhattan distance of 10 or more
                            rat_kb.filter_cells_by_distance(10, greater_than=True)  # Retain only cells >= 10 distance

                            # Retrieve possible cells to move towards, filtered by distance
                            far_cells = list(rat_kb.rat_detection_probabilities.keys())
                            
                            # If there are far cells to choose from, proceed with movement
                            if far_cells:
                                chosen_far_cell = random.choice(far_cells)
                                
                                # Use BFS to find a path towards the chosen far cell
                                path_to_far_cell = self.bfs_path(self.bot.position, chosen_far_cell)
                                print(f"Planned BFS path to far cell {chosen_far_cell}: {path_to_far_cell}")
                                
                                # Move along the path to the chosen cell until reaching it, then check for a ping again
                                if path_to_far_cell:
                                    for step in range(1, len(path_to_far_cell)):
                                        next_step = path_to_far_cell[step]
                                        self.bot.position = next_step  # Update the bot's position
                                        self.rat.move_randomly()
                                        self.step_counter += 1  # Count each step
                                        self.draw_grid(screen)
                                        pygame.display.flip()
                                        clock.tick(100)  # Adjust for visualization speed
                                        print(f"Bot moved towards far cell to position {next_step}.")

                                    # Once the bot reaches the chosen far cell, it will check for a ping again in the next iteration


                        if self.bot.position == self.rat.position:
                            print("Rat caught!")
                            print(f"Total steps taken to catch the rat: {self.step_counter}")  # Print total steps
                            running = False
                            break

                        self.draw_grid(screen)
                        pygame.display.flip()
                        clock.tick(100)
                        



        pygame.quit()





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
                    pygame.draw.rect(screen, BLUE, rect)
                elif (r, c) == self.rat.position:
                    pygame.draw.rect(screen, GREEN, rect)
                elif self.env.matrix[r][c] == 1:
                    pygame.draw.rect(screen, GRAY, rect)
                else:
                    pygame.draw.rect(screen, YELLOW, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)


