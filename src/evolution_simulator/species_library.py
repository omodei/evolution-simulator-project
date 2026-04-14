# species_library.py

"""
This library defines the blueprints for all species in the simulation.
Each species is a dictionary containing:
- name: The name of the species.
- tags: A set of identifiers (e.g., 'plant', 'animal', 'insect').
- color: The base color for visualization.
- marker: The shape for visualization.
- base_genes: The default DNA values for this species.
- capabilities: A dictionary defining what this species can DO.
"""

SPECIES = {
    "grass": {
        "name": "Grass",
        "tags": {"plant", "producer"},
        "color": "forestgreen",
        "marker": "P", # for Plant
        "base_genes": {
            'speed': 0, # Plants don't move
            'vision_range': 0,
        },
        "capabilities": {
            "photosynthesize": {"energy_gain": 2},
            "can_reproduce": {"min_energy": 20, "cost": 10},
        }
    },
    "algae": {
        "name": "Algae",
        "tags": {"plant", "producer", "aquatic"},
        "color": "seagreen",
        "marker": "P",
        "base_genes": {
            'speed': 0,
            'vision_range': 0,
        },
        "capabilities": {
            "photosynthesize": {"energy_gain": 1},
            "can_reproduce": {"min_energy": 15, "cost": 8},
            "requires_water_tile": True, # Must be on a water tile
        }
    },
    "water_flea": {
        "name": "Water Flea",
        "tags": {"animal", "herbivore", "insect", "aquatic"},
        "color": "skyblue",
        "marker": "o",
        "base_genes": {
            'speed': 1.5,
            'vision_range': 4,
            'max_age': 150,
        },
        "capabilities": {
            "can_move": True,
            "can_eat": {"energy_gain": 40, "eats_tags": {"algae"}},
            "can_reproduce": {"min_energy": 100, "cost": 50},
            "requires_water_tile": True,
        }
    },
    "minnow": {
        "name": "Minnow",
        "tags": {"animal", "carnivore", "fish", "aquatic"},
        "color": "silver",
        "marker": ">",
        "base_genes": {
            'speed': 2.5,
            'vision_range': 6,
            'max_age': 200,
        },
        "capabilities": {
            "can_move": True,
            "can_eat": {"energy_gain": 60, "eats_tags": {"water_flea"}},
            "can_reproduce": {"min_energy": 120, "cost": 60},
            "requires_water_tile": True,
        }
    },
    "cow": {
        "name": "Cow",
        "tags": {"animal", "herbivore", "mammal"},
        "color": "lightgray",
        "marker": "o",
        "base_genes": {
            'speed': 1.0,
            'vision_range': 5,
            'max_age': 250,
        },
        "capabilities": {
            "can_move": True,
            "can_eat": {"energy_gain": 50, "eats_tags": {"grass"}},
            "can_reproduce": {"min_energy": 150, "cost": 75},
            "need_water": {"hydration_gain": 50}, # Needs to drink every 5 ticks
        }
    },
}
