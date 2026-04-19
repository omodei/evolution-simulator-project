# dna.py (Updated)
import random
from .config import *
import logging # 1. Import logging

# 2. Get a logger instance for this module
logger = logging.getLogger(__name__)

class DNA:
    def __init__(self, genes=None):
        
        if genes:
            self.genes = genes
        else:
            self.genes = {}
            for k in GENE_DEFAULTS.keys():
                self.genes[k] = GENE_DEFAULTS[k][0]

    @staticmethod
    def mix_and_mutate(dna1, dna2):
        child_genes = {}
        for gene in dna1.genes:
            child_genes[gene] = random.choice([dna1.genes[gene], dna2.genes[gene]])

        for gene in child_genes:
            if random.random() < MUTATION_RATE:
                pre_mutation_value = child_genes[gene]
                if pre_mutation_value == 0:
                    continue
                change = child_genes[gene] * MUTATION_AMOUNT
                mutation = random.uniform(-change, change)
                if gene == 'max_age':
                    child_genes[gene] = int(max(50, child_genes[gene] + mutation)) # Max age should be at least 50 to allow for reproduction
                else:
                    child_genes[gene] = child_genes[gene] + mutation   # Other genes should not go below 0.1 to prevent non-viable organisms
                logger.debug(f"Mutated gene '{gene}' from {pre_mutation_value} to {child_genes[gene]}")
        return DNA(genes=child_genes)