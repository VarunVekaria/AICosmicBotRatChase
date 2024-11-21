import random
import pygame

from rat_knowledge_base import RatKnowledgeBase
from rat import Rat
from ship_environment_logic import ShipEnvironment

from collections import deque
class Bot:
    def __init__(self, environment, knowledge_base):
        self.environment = environment
        self.kbase = knowledge_base
        self.loc = random.choice(list(self.kbase.poss_locs))
        self.prev_hist = []
        self.recent_locs = deque(maxlen=20)
        self.goal_path = []
        self.rat_kbase = None

    def set_goal_path(self, path, rat_kbase):
        self.goal_path = path
        self.rat_kbase = rat_kbase
        print(f"Bot set to follow path to goal cell: {path}")

    def move_to_goal(self):
        if self.goal_path:
            next_loc = self.goal_path.pop(0)
            self.loc = next_loc
            self.prev_hist.append(self.loc)
            self.recent_locs.append(self.loc)  # Diff
            print(f"Bot moved to {self.loc} along the goal path.")
            if self.rat_kbase:
                self.rat_kbase.modify_goal_cells(self.loc)

    def detect_osc(self):
        # Check if recent locs contain a repeating pattern
        if len(set(self.recent_locs)) <= 4:
            return True
        return False
    
    def force_move_out_of_osc(self, simulate, screen, clock):

        # Get all open cells within the grid
        open_cells = [(r, c) for r in range(1, self.environment.size - 1) for c in range(1, self.environment.size - 1)
                      if self.environment.matrix[r][c] == 0 and (r, c) not in self.recent_locs]

        if open_cells:
            # Choose a cell that's not in recent locs
            chosen_cell = random.choice(open_cells)
            path_to_chosen_cell = simulate.bfs_path(self.loc, chosen_cell)

            if path_to_chosen_cell:
                # Move several steps along this path to break out of the loop
                steps_to_move = min(3, len(path_to_chosen_cell) - 1)  # Take up to 3 steps or the full path length
                
                for step in range(1, steps_to_move + 1):
                    self.loc = path_to_chosen_cell[step]
                    self.prev_hist.append(self.loc)
                    self.recent_locs.append(self.loc)
                    
                    # Update the display after each step
                    simulate.draw_grid(screen)
                    pygame.display.flip()
                    clock.tick(10)  # Adjust speed as needed


    def sense_possible_moves(self):
        r, c = self.loc
        return self.kbase.get_open_neighbors(r, c)

    def move(self):
        probabilities = self.kbase.calc_dir_probabilities()
        if probabilities is None:
            print("No available moves. Stopping.")
            return False
        possible_moves_map = [(0, 1), (0, -1), (-1, 0), (1, 0)]
        chosen_dir_idx = random.choices(range(4), weights=probabilities, k=1)[0]
        dr, dc = possible_moves_map[chosen_dir_idx]
        new_loc = (self.loc[0] + dr, self.loc[1] + dc)
        if (0 <= new_loc[0] < self.environment.size and
            0 <= new_loc[1] < self.environment.size and
            self.environment.matrix[new_loc[0]][new_loc[1]] == 0):
            self.loc = new_loc
            self.prev_hist.append(self.loc)
            print(f"Bot moved to {self.loc}")
            self.kbase.modify_poss_locs(dr, dc)
            return True
        print("Bot could not move in the chosen direction.")
        return False