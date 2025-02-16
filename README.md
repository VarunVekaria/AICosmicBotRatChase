# Bot and Rat Tracking Simulation - Project 2

This repository contains a simulation project for a bot and rat tracking environment using a grid system. The project implements various classes for environment simulation, bot and rat behavior, probabilistic detection, and knowledge management.

## Project Structure

The repository includes the following files:

- `main.py` - The main file to run the simulation. Includes code to import other modules and execute the simulation.
- `bot.py` - Contains the implementation of the bot, including its movement, detection, and tracking logic.
- `knowledge_base.py` - Manages and filters the bot's knowledge about its location in the grid environment.
- `rat.py` - Implements the rat's behavior and movements in the grid.
- `rat_knowledge_base.py` - Manages the rat's knowledge and its interaction with the bot.
- `ship_environment_logic.py` - Defines the grid environment, including blocked and open cells.
- `simulation_logic.py` - Simulates the interaction between the bot and rat in the environment.

Key Components
1. Grid Environment Simulation
The grid represents a bounded environment with both open cells (navigable by the bot and rat) and blocked cells (obstacles).
The environment dynamically generates open paths by ensuring there are no isolated or inaccessible areas.
Dead-end detection is implemented to make the environment navigable by opening closed neighbor cells to resolve paths.
2. Bot Behavior
The bot starts with incomplete knowledge of its location and the environment.
It refines its understanding through sensor data (sensed directions of open cells) and probabilistic reasoning.
The bot moves using calculated probabilities to decide the most likely direction leading to the rat.
The bot uses a Breadth-First Search (BFS) algorithm to find paths when targeting specific locations.
3. Rat Behavior
The rat is randomly placed in an open cell of the grid and avoids being in the bot's initial position.
Its movement and position are hidden from the bot, and its presence is inferred using probabilities.
4. Probabilistic Detection
Detection is based on the Manhattan distance between the bot and the rat.
Probabilities decrease as the distance between the bot and rat increases, modeled using exponential decay.
5. Knowledge Management
The bot maintains a Knowledge Base to manage potential positions within the grid and refine them based on sensed data.
The rat has its own Knowledge Base to track detection probabilities for each cell.
6. Simulation Logic
The bot and rat interact within the grid, with the bot progressively narrowing down the rat's location.
The simulation tracks the number of steps taken by the bot to detect the rat and outputs relevant data, such as:
A probability grid, showing the likelihood of the rat being in each cell.
The total steps the bot took to find the rat.
