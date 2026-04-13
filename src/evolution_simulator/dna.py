# dna.py (Updated)
import random
from config import *
import logger 
logger = logger.logger()

class DNA:
    def __init__(self, genes=None):
        if genes:
            self.genes = genes
        else:
            self.genes = {
                'max_age': random.randint(MAX_AGE - 50, MAX_AGE + 50),
                'energy_efficiency': random.uniform(0.8, 1.2),
                'hydration_efficiency': random.uniform(0.8, 1.2), # Multiplier for water loss
                'eat_energy_gain': random.uniform(0.8, 1.2) * EAT_ENERGY_GAIN,
                'carnivore_energy_gain': random.uniform(0.8, 1.2) * CARNIVORE_ENERGY_GAIN,
                'hunting_radius': random.uniform(0.8, 1.2) * HUNTING_RADIUS,
                'speed': random.randint(1, SPEED),
                #'brownian_motion_sigma': random.uniform(0.8, 1.2) * BROWNIAN_MOTION_SIGMA,
                'vision_range': random.uniform(0.8, 1.2) * VISION_RANGE,
                'hydration_urgency_threshold': random.uniform(0.8, 1.2) * HYDRATION_URGENCY_THRESHOLD,
                'energy_urgency_threshold': random.uniform(0.8, 1.2) * ENERGY_URGENCY_THRESHOLD,
                'reproduction_urgency_threshold': random.uniform(0.8, 1.2) * REPRODUCTION_URGENCY_THRESHOLD,
                'proximity_radius': random.uniform(0.8, 1.2) * PROXIMITY_RADIUS,
                'reproduction_energy_threshold': random.uniform(0.8, 1.2) * REPRODUCTION_ENERGY_THRESHOLD,
                'reproduction_age_threshold': random.uniform(0.8, 1.2) * REPRODUCTION_AGE_THRESHOLD,
                'carnivore_age_threshold': random.uniform(0.8, 1.2) * CARNIVORE_AGE_THRESHOLD,

                'reproduction_energy_cost': random.uniform(0.8, 1.2) * REPRODUCTION_ENERGY_COST,
                # --- NEW DIET GENE ---
                # 0 for Herbivore, 1 for Carnivore
                'diet_type': 1 if random.random() < INITIAL_CARNIVORE_RATIO else 0,
               
            }
    @staticmethod
    def mix_and_mutate(dna1, dna2):
        child_genes = {}
        for gene in dna1.genes:
            child_genes[gene] = random.choice([dna1.genes[gene], dna2.genes[gene]])

        for gene in child_genes:
            if random.random() < MUTATION_RATE:
                pre_mutation_value = child_genes[gene]
                if gene == 'diet_type':
                    # Flip the bit: a rare mutation can change species
                    child_genes[gene] = 1 - child_genes[gene] 
                else:
                    change = child_genes[gene] * MUTATION_AMOUNT
                    mutation = random.uniform(-change, change)
                    
                    if 'color' in gene:
                        child_genes[gene] = int(max(0, min(255, child_genes[gene] + 1))) # Color mutations are small and more likely to be positive (for visibility)
                    elif gene == 'max_age':
                        child_genes[gene] = int(max(50, child_genes[gene] + mutation)) # Max age should be at least 50 to allow for reproduction
                    else:
                        child_genes[gene] = max(0.1, child_genes[gene] + mutation)   # Other genes should not go below 0.1 to prevent non-viable organisms
                logger.log(f"Mutated gene '{gene}' from {pre_mutation_value} to {child_genes[gene]}")
        return DNA(genes=child_genes)