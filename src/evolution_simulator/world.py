# world.py (Updated)
import numpy as np
import math
from itertools import combinations
from .organism import Organism
from .dna import DNA
from .config import *
from perlin_noise import PerlinNoise # <-- Import the new library
import logging # 1. Import logging

# 2. Get a logger instance for this module
logger = logging.getLogger(__name__)

class World:
    def __init__(self, size):
        self.size = size
        self.organisms = []
        self.food_grid = np.zeros(size, dtype=int)
        for _ in range(FOOD_INITIAL_NUMBER):
            x = np.random.randint(0, size[0])
            y = np.random.randint(0, size[1])
            self.food_grid[x, y] = 1
        # --- NEW: Procedurally generate the water grid ---
        # Initialize the noise generator with our parameters from config
        noise = PerlinNoise(octaves=NOISE_OCTAVES, 
                            seed=RANDOM_SEED)
        
        self.water_grid = np.zeros(size)
        for x in range(size[0]):
            for y in range(size[1]):
                # Calculate the noise value for the coordinate
                noise_val = noise([x / NOISE_SCALE, y / NOISE_SCALE])
                
                # If the noise value is above our water level, it's a water tile
                if noise_val > WATER_LEVEL_THRESHOLD:
                    self.water_grid[x, y] = 1.0
    def add_organism(self, organism):
        self.organisms.append(organism)

    def _replenish_food(self):
        # This method is unchanged
        current_food_count = np.sum(self.food_grid)
        food_to_add = min(FOOD_REPLENISH_RATE, MAX_FOOD_UNITS - current_food_count)
        if food_to_add <= 0: return
        occupied_cells = set((org.x, org.y) for org in self.organisms)
        possible_coords = [(x, y) for x in range(self.size[0]) for y in range(self.size[1]) if self.food_grid[x, y] == 0 and (x, y) not in occupied_cells]
        num_to_place = min(len(possible_coords), food_to_add)
        if num_to_place > 0:
            spawn_indices = np.random.choice(len(possible_coords), num_to_place, replace=False)
            for i in spawn_indices:
                x, y = possible_coords[i]
                self.food_grid[x, y] = 1

    def update_world(self):
        """Update the world state for one tick with new interaction logic."""
        
        # 1. Update basic stats and move all organisms first
        for org in self.organisms:
            org.update(self)
            logger.debug(org)

        # --- NEW: 2. Handle Drinking ---
        for org in self.organisms:
            if not org.is_alive(): continue
            # Check if the organism is on a water tile
            if self.water_grid[org.x, org.y] > 0:
                org.drink()

        # 2. Handle eating and hunting
        eaten_this_tick = set()
        # Create a copy of organisms to iterate over for hunting prey
        all_prey = list(self.organisms) 

        for org in self.organisms:
            if not org.is_alive(): continue

            # Herbivore behavior
            if org.diet_type == 0:
                if self.food_grid[org.x, org.y] == 1:
                    org.energy += org.dna.genes['eat_energy_gain']
                    self.food_grid[org.x, org.y] = -1 # Remove the food from the grid
            
            # Carnivore behavior
            elif org.diet_type == 1:
                for prey in all_prey:
                    # Carnivores hunt living herbivores they are not related to (for now, any herbivore)
                    # A prey cannot be itself or already eaten this tick
                    if org is prey or not prey.is_alive() or prey in eaten_this_tick:
                        continue
                    
                    # Carnivores only eat herbivores
                    if prey.diet_type == 0:
                        dist = math.sqrt((org.x - prey.x)**2 + (org.y - prey.y)**2)
                        if dist <= org.dna.genes['hunting_radius']:
                            org.energy += org.dna.genes['carnivore_energy_gain']
                            prey.energy = 0 # The prey is killed
                            eaten_this_tick.add(prey)
                            break # Carnivore only eats one prey per tick

        # 3. Handle Reproduction (logic is the same, but happens after eating)
        newborns = []
        reproduced_this_tick = set()
        for org1, org2 in combinations(self.organisms, 2):
            if org1 in reproduced_this_tick or org2 in reproduced_this_tick or not org1.is_alive() or not org2.is_alive():
                continue
            if org1.can_reproduce() and org2.can_reproduce():
                dist = math.sqrt((org1.x - org2.x)**2 + (org1.y - org2.y)**2)
                if dist <= org1.dna.genes['proximity_radius']:
                    org1.energy -= org1.dna.genes['reproduction_energy_cost']
                    org2.energy -= org2.dna.genes['reproduction_energy_cost']
                    child_dna = DNA.mix_and_mutate(org1.dna, org2.dna)
                    child = Organism(x=org1.x, y=org1.y, dna=child_dna)
                    newborns.append(child)
                    reproduced_this_tick.add(org1)
                    reproduced_this_tick.add(org2)
        
        # 4. Add newborns and replenish food
        self.organisms.extend(newborns)
        self._replenish_food()

        # 5. Cull the dead (from old age, starvation, or being eaten)
        initial_pop = len(self.organisms)
        self.organisms = [org for org in self.organisms if org.is_alive()]
        deaths = initial_pop - len(self.organisms)
        
        #print(f"Tick: {len(self.organisms):>4} pop | Born: {len(newborns):>2}, Died: {deaths:>2}")