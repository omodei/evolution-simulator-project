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
    "A": {
        "name": "A",
        "color": "forestgreen",
        "marker": ".", 
        "eats_tags": {"B": 0.9},
        "genes": {
            'max_age': 100,
            'max_energy': 100,
            'max_water': 100,
            'vision':  100,
            'speed':   2,
        },
    },
    "B": {
        "name": "B",
        "color": "khaki",
        "marker": "P", 
        "eats_tags": {"C": 0.9},

        "genes": {
            'max_age': 100,
            'max_energy': 100,
            'max_water': 100,
            'vision':  100,
            'speed':   2,
        },
    },
    "C": {
        "name": "C",
        "color": "grey",
        "marker": "o", 
        "eats_tags": {"D": 0.9},
        "genes": {
            'max_age': 100,
            'max_energy': 100,
            'max_water': 100,
            'vision':  100,
            'speed':   2,
        },
    },
    "D": {
        "name": "D",
        "color": "red",
        "marker": "s", 
        "eats_tags": {"E": 1},
        "genes": {
            'max_age': 70,
            'max_energy': 80,
            'max_water': 90,
            'vision':  100,
            'speed':   2,
        },
    },
    "E": {
        "name": "E",
        "color": "blue",
        "marker": "^", 
        "eats_tags": {"F": 1},
        "genes": {
            'max_age': 70,
            'max_energy': 80,
            'max_water': 90,
            'vision':  100,
            'speed':   2,
        },
    },
    "F": {
        "name": "F",
        "color": "pink",
        "marker": "o", 
        "eats_tags": {"G": 1},
        "genes": {
            'max_age': 70,
            'max_energy': 80,
            'max_water': 90,
            'vision':  100,
            'speed':   2,
        },
    },
    "G": {
        "name": "G",
        "color": "magenta",
        "marker": "^", 
        "eats_tags": {"H": 1},
        "genes": {
            'max_age': 70,
            'max_energy': 80,
            'max_water': 90,
            'vision':  100,
            'speed':   2,
        },
    },
    "H": {
        "name": "H",
        "color": "cyan",
        "marker": "^", 
        "eats_tags": {"I": 1},
        "genes": {
            'max_age': 70,
            'max_energy': 80,
            'max_water': 90,
            'vision':  100,
            'speed':   2,
        },
    },
    "I": {
        "name": "I",
        "color": "k",
        "marker": "o", 
        "eats_tags": {"J": 1},
        "genes": {
            'max_age': 70,
            'max_energy': 80,
            'max_water': 90,
            'vision':  100,
            'speed':   2,
        },
    },
    "J": {
        "name": "J",
        "color": "lime",
        "marker": "o", 
        "eats_tags": {"A": 1},
        "genes": {
            'max_age': 70,
            'max_energy': 80,
            'max_water': 90,
            'vision':  100,
            'speed':   2,
        },
    },
}
