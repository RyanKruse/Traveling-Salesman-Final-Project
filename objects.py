from settings import *


class Truck:
    """This is the truck class that handles all package delivery logistics."""
    def __init__(self, sim, identifier, available, last_trip, buffer):
        """Initialize truck variables."""
        self.simulation = sim  # Reference to simulation.
        self.identifier = identifier  # Truck ID number.
        self.miles = 0.000  # Miles currently driven.
        self.next_distance = 0  # Miles to next address.
        self.current = 0  # Current location.
        self.count = 0  # Number of packages loaded.
        self.bay = []  # Loaded package data.
        self.package_ids = []  # Loaded package IDs.
        self.locations = []  # Truck driving route.
        self.distances = []  # Driving route distances.
        self.weight = 0.0  # Sum of distances.
        self.last_trip = last_trip  # Records if truck will return to hub.
        self.available = available  # Records if truck is driving.
        self.buffer = self.simulation.space(buffer)  # Buffer space for printing text.
        self.unload_ids = []  # Package IDs being delivered.

    def drive(self):
        """Drives the truck one second. O(1)."""
        self.miles = self.miles + TRUCK_SPEED_PER_SECOND
        self.next_distance = self.next_distance - TRUCK_SPEED_PER_SECOND

    def deliver_package(self):
        """When truck arrives at a location, deliver all packages for that location from truck. O(N^2)."""
        self.unload_ids = []
        for package in self.bay[:]:
            if package[-1] == self.locations[0]:
                # Update package status in hash table, de-increment count, and remove package.
                self.simulation.hash_table[int(package[0])][-1] = "Delivered at" + str(self.simulation.time)
                self.unload_ids.append(package[0])
                self.count = self.count - 1
                self.package_ids.pop(0)
                self.bay.remove(package)

    def next_address(self):
        """Update truck current location, driving route, and driving route distances. O(N)."""
        self.current = self.locations.pop(0)
        self.distances.pop(0)
        # Updates next location. Make available if in Hub.
        if self.distances:
            self.next_distance = self.next_distance + self.distances[0]
            self.weight = sum(self.distances)
        else:
            self.weight = 0.0
            if self.current == 0:
                self.available = True

    def print_simulation(self):
        """Print the event that occurred above truck string and print the simulation. O(N)."""
        if self.available and self.current == 0:
            print(self.simulation.newline + self.buffer + "[Arrived at HUB]")
        else:
            print(self.simulation.newline + self.buffer + "[Delivered package " + str(', '.join(self.unload_ids)) + "]")
        print(self.simulation)
        # Accept another GUI input.
        self.simulation.event = True


class Clock:
    """This is the clock class that keeps track of time in the simulation."""
    def __init__(self, hour, minute, second):
        """Initializes time keeping variables."""
        self.hour = hour
        self.minute = minute
        self.second = second

    def __str__(self):
        """Returns a string version of the clock class in non-military time. O(1)."""
        return " %d:%02d:%02d %s" % (self.hour_mod(), self.minute, self.second, ("AM", "PM")[self.hour >= 12])

    def tick_second(self):
        """This function increments time by 1 second for each simulation tick. Adjusts hours and minutes. O(1)."""
        self.second = self.second + 1
        if self.second >= 60:
            self.second = 0
            self.minute = self.minute + 1
            if self.minute >= 60:
                self.minute = 0
                self.hour = self.hour + 1
                if self.hour >= 24:
                    self.hour = 0

    def hour_mod(self):
        """Returns clock hours in non-military time. O(1)."""
        return ((self.hour-1) % 12)+1

    def compare_time(self, input_time):
        """Determines if input time equals current time. O(1)."""
        input_time = [int(x) for x in list(input_time.split(':'))]
        return self.hour == input_time[0] and \
            self.minute == input_time[1] and \
            self.second == input_time[2]

    def set_time(self, input_time):
        """Set current time on the clock to input time. O(1)."""
        input_time = [int(x) for x in list(input_time.split(':'))]
        self.hour = input_time[0]
        self.minute = input_time[1]
        self.second = input_time[2]


class HashTable:
    """This is the hash table class that keepts track of package data."""
    def __init__(self, size):
        """Initialize hash table variables."""
        self.size = size
        self.slots = [None] * self.size  # Package IDs are stored here.
        self.data = [None] * self.size  # Package data is stored here.

    def __len__(self):
        """Return hash table size. O(1)."""
        return int(self.size)

    def __contains__(self, key):
        """Determines if key is in hash table. O(1)."""
        if self.__getitem__(key) is None:
            return False
        return True

    def __getitem__(self, key):
        """Get data from hash table. O(1)."""
        return self.get(key)

    def __setitem__(self, key, data):
        """Put data in hash table. O(1)."""
        self.put(key, data)

    def __str__(self):
        """Returns a string of all occupied slots and data from the hash table. O(N)."""
        table_string = "\nPackage Hash Table\n"
        for slot in self.slots:
            if slot is None:
                continue
            table_string = table_string + repr(slot) + ": " + repr(self.get(slot)) + "\n"
        return table_string

    def put(self, key, data):
        """Stores key and data into hash table. If load factor exceeds 70%, resize hash table. O(1)."""
        # Get hash value of key.
        hash_value = self.hash_function(key, len(self.slots))
        hash_value_start = hash_value

        # Allowed hash table to dynamically adjust size as load increases.
        load_factor = len([a for a in self.data if a is not None]) / len(self)
        if load_factor >= .7:
            temp_slots = [None] * self.size
            temp_data = [None] * self.size
            self.size *= 2
            self.slots = self.slots + temp_slots
            self.data = self.data + temp_data

        # If slot corresponding to hash value is empty, set slot and data.
        if self.slots[hash_value] is None:
            self.slots[hash_value] = key
            self.data[hash_value] = data
        else:
            # If slot corresponding to hash value is equal to key, replace data.
            if self.slots[hash_value] == key:
                self.data[hash_value] = data
            else:
                # If slot corresponding to hash value is not equal to key and is not empty, rehash hash value.
                next_slot = self.rehash(hash_value, len(self.slots))
                while self.slots[next_slot] is not None and self.slots[next_slot] != key:
                    next_slot = self.rehash(next_slot, len(self.slots))
                # Set slot and data.
                if self.slots[next_slot] is None:
                    self.slots[next_slot] = key
                    self.data[next_slot] = data
                else:
                    self.data[next_slot] = data

    def get(self, key):
        """Returns the data corresponding to key from hash table. If slot for key is not found, return None. O(1)."""
        # Gets hash value of key.
        start_slot = self.hash_function(key, len(self.slots))
        position = start_slot

        # Search slots for key.
        while self.slots[position] is not None:
            # If key is found, return data.
            if self.slots[position] == key:
                return self.data[position]
            # If key is not found, rehash new position.
            position = self.rehash(position, len(self.slots))
            if position == start_slot:
                return None

    def hash_function(self, key, size):
        """Returns remainder of being divided by hash table size. O(1)."""
        return key % size

    def rehash(self, old_hash, size):
        """Increases hash slot by 1 if previous hash value had collision. O(1)."""
        return (old_hash + 1) % size
