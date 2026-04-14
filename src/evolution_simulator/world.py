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

         # 2. Handle interactions (like eating) in a general way
        eaters = [org for org in self.organisms if "can_eat" in org.capabilities]
        potential_prey = list(self.organisms) # All organisms are potential prey
        
        eaten_this_tick = set()
        for eater in eaters:
            if not eater.is_alive(): continue

            eat_capability  = eater.capabilities["can_eat"]
            valid_prey_tags = eat_capability["eats_tags"]

            vision = eater.base_genes["vision_range"]

            for prey in potential_prey:
                if not prey.is_alive() or prey is eater: continue

                # Check if the prey is something this eater can eat
                # `isdisjoint` is a fast way to check for any overlap in sets
                if not valid_prey_tags.isdisjoint(prey.tags):
                    # Check distance (within vision/hunting range)
                    dist_sq = (eater.x - prey.x)**2 + (eater.y - prey.y)**2
                    if dist_sq <= vision**2:
                        # Success! Eater eats prey.
                        eater.energy += eat_capability["energy_gain"]
                        prey.die()
                        break # Eater only eats one thing per tick




        # --- NEW: 2. Handle Drinking ---
        drinkers = [org for org in self.organisms if "need_water" in org.capabilities]
        for org in drinkers:
            if not org.is_alive(): continue
            if self.water_grid[org.x, org.y] > 0:
                org.drink() 

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
        #deaths = initial_pop - len(self.organisms)
        
        #print(f"Tick: {len(self.organisms):>4} pop | Born: {len(newborns):>2}, Died: {deaths:>2}")