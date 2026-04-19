# world.py (Updated)
import numpy as np
import math
from itertools import combinations
from .organism import Organism
from .dna import DNA
from .config import *

from perlin_noise import PerlinNoise # <-- Import the new library

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # Set to DEBUG to see detailed logs from the world

class World:
    def __init__(self, size):
        self.size = size
        self.organisms = []
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


    def update_world(self):
        """Update the world state for one tick with new interaction logic."""
        
        # 1. Update basic stats and move all organisms first
        for org in self.organisms:
            org.update(self)
            logger.debug(org)

         # 2. Handle interactions (like eating) in a general way
        #eaters = [org for org in self.organisms if "can_eat" in org.capabilities]
        potential_prey = list(self.organisms) # All organisms are potential prey
        
        eaten_this_tick = set()

        for eater in self.organisms:
            if not eater.is_alive() or eater in eaten_this_tick or not eater.is_hungry: continue

            valid_prey_tags = eater.eats_tags.keys() # Get the tags of what this species can eat

            for prey in potential_prey:
                if prey is eater: continue

                # Check if the prey is something this eater can eat
                # `isdisjoint` is a fast way to check for any overlap in sets
                if prey.species_name in valid_prey_tags:
                    # Check distance (within vision/hunting range)
                    dist_sq = (eater.x - prey.x)**2 + (eater.y - prey.y)**2
                    if dist_sq <= INTERACTION_RADIUS ** 2 and eater.eats_tags.get(prey.species_name, 0) > np.random.random():
                        #print(f"{eater.species_name} eating {prey.species_name}: {eater.eats_tags.get(prey.species_name, 0)}")

                        # Success! Eater eats prey.
                        eater.eat(prey)
                        prey.die()
                        eaten_this_tick.add(eater)
                        break # Eater only eats one thing per tick




        # --- NEW: 2. Handle Drinking ---
        for org in self.organisms:
            if not org.is_alive() or not org.is_thirsty: continue
            if self.water_grid[org.x, org.y] > 0:
                org.drink() 

        # 3. Handle Reproduction (logic is the same, but happens after eating)
        newborns = []
        reproduced_this_tick = set()

        for org1, org2 in combinations(self.organisms, 2):
            if org1 in reproduced_this_tick or org2 in reproduced_this_tick or not org1.is_alive() or not org2.is_alive() or not org1.is_seeking_mate() or not org2.is_seeking_mate():
                continue
            dist_sq = (org1.x - org2.x)**2 + (org1.y - org2.y)**2
            if dist_sq <= INTERACTION_RADIUS ** 2 and org1.species_name == org2.species_name:
                child_dna = DNA.mix_and_mutate(org1.dna, org2.dna)
                child = Organism(x=org1.x, y=org1.y, species_name = org1.species_name, dna=child_dna)
                child.energy = org1.energy*0.5 + org2.energy*0.5 # Start with average energy of parents
                org1.energy -= REPRODUCTION_COST * INITIAL_ENERGY
                org2.energy -= REPRODUCTION_COST * INITIAL_ENERGY
                newborns.append(child)
                reproduced_this_tick.add(org1)
                reproduced_this_tick.add(org2)
        
        # 4. Add newborns and replenish food
        self.organisms.extend(newborns)

        # 5. Cull the dead (from old age, starvation, or being eaten)
        self.organisms = [org for org in self.organisms if org.is_alive()]
