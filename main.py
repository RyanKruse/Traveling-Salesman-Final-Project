# Made by Ryan Kruse #001099380.

from prepper import Prepper
from simulation import Simulation

prepper = Prepper()
prepper.execute()
simulation = Simulation(prepper)
simulation.execute()
