import random


from rat_knowledge_base import RatKnowledgeBase
from rat import Rat
from ship_environment_logic import ShipEnvironment

from collections import deque
class Bot:
    def __init__(self, environment, knowledge_base):
        self.environment = environment
        self.kbase = knowledge_base
        self.loc = random.choice(list(self.kbase.eligible_locs))
        self.prev_history = []
        self.recent_locs = []
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
            self.prev_history.append(self.loc)
            print(f"Bot moved to {self.loc} along the goal path.")
            if self.rat_kbase:
                self.rat_kbase.modify_goal_cells(self.loc)

    def sense_directions(self):
        r, c = self.loc
        return self.kbase.get_open_neighbors(r, c)

    def move(self):
        probabilities = self.kbase.calculate_dir_probabilities()
        if probabilities is None:
            print("No available moves. Stopping.")
            return False
        directions_map = [(0, 1), (0, -1), (-1, 0), (1, 0)]
        chosen_dir_index = random.choices(range(4), weights=probabilities, k=1)[0]
        dr, dc = directions_map[chosen_dir_index]
        new_loc = (self.loc[0] + dr, self.loc[1] + dc)
        if (0 <= new_loc[0] < self.environment.size and
            0 <= new_loc[1] < self.environment.size and
            self.environment.matrix[new_loc[0]][new_loc[1]] == 0):
            self.loc = new_loc
            self.prev_history.append(self.loc)
            print(f"Bot moved to {self.loc}")
            self.kbase.modify_eligible_locs(dr, dc)
            return True
        print("Bot could not move in the chosen direction.")
        return False