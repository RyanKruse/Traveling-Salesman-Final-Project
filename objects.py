from settings import *


class Truck:
    """This is the truck class."""
    def __init__(self, sim, identifier, available, last_trip, buffer):
        """Declare truck variables."""
        self.simulation = sim  # Reference to simulation.
        self.identifier = identifier  # Records truck ID.
        self.miles = 0.000  # Records current number of miles driven.
        self.next_weight = 0  # Records next address mileage weight.
        self.location = 0  # Records current address location.
        self.count = 0  # Records number of packages in bay.
        self.bay = []  # Records complete package information of packages currently on board.
        self.package_map = []  # Records the order in which package IDs are delivered.
        self.address_map = []  # Records the sequence of the unique_count the truck will drive.
        self.weight_map = []  # Records the sequence of the mileage weights the truck will incur.
        self.weight = 0.0  # Records mileage weight of total route the truck is driving on.
        self.last_trip = last_trip  # Records if truck will return to hub after delivering its last package.
        self.available = available  # Records if truck is currently driving or in hub.
        self.buffer = self.simulation.space(buffer)  # Records buffer space for printing event text.
        self.unload_ids = []  # Records all package IDs being delivered at a location.

    def drive(self):
        """Increments current truck miles and de-increments next_address miles by 1 second of travel. O(1)."""
        self.miles = self.miles + TRUCK_SPEED_PER_SECOND
        self.next_weight = self.next_weight - TRUCK_SPEED_PER_SECOND

    def deliver_package(self):
        """Unloads all packages from the truck that have the same address the truck is currently at. O(N^2)."""
        self.unload_ids = []  # Contains package IDs being unloaded. This will be used later when printing simulation.
        for package in self.bay[:]:
            if package[-1] == self.address_map[0]:  # Checks if package address index equals truck's current address.
                buffer = ""  # Contains clock buffer. As clock hour shifts from 1 digit to 2, space will adjust.
                if self.simulation.time.hour >= 10:
                    buffer = " "
                # Open up hash table, input key as package ID, then update status to "Delivered at ##:##:## AM/PM)
                self.simulation.hash_table[int(package[0])][-1] = "Delivered at" + buffer + str(self.simulation.time)
                self.unload_ids.append(package[0])  # Append package ID unloaded to unload ID list.
                self.count = self.count - 1  # Reduce package count on truck by 1.
                self.package_map.pop(0)  # Remove current package ID from the package map. Will always be index 0.
                self.bay.remove(package)  # Remove package from truck bay.

    def next_address(self):
        """Removes the address just delivered to from relevant lists. Updates weight of next address route. O(N)."""
        self.location = self.address_map.pop(0)  # Current location is the first index popped from the address map.
        self.weight_map.pop(0)  # Truck has finished driving to this location, so remove first index from weight map.
        if self.weight_map:  # Checks if there are more routes to drive. If so, set the new route and update weights.
            self.next_weight = self.next_weight + self.weight_map[0]
            self.weight = sum(self.weight_map)  # Calculates remaining miles to drive to all route unique_count.
        else:  # If this fires, there are no more routes to drive. Set remaining miles to drive on routes to 0.
            self.weight = 0.0
            if self.location == 0:  # Checks to see if truck is in HUB. If so, set truck to available to load packages.
                self.available = True

    def print_simulation(self):
        """Prints the event that just occurred above the truck text. Then print the simulation. O(N)."""
        if self.available and self.location == 0:  # Prints the event that the truck has arrived in the HUB.
            print(self.simulation.newline + self.buffer + "[Arrived at HUB]")
        else:  # Prints the event that the truck has delivered packages. Print all package IDs unloaded.
            print(self.simulation.newline + self.buffer + "[Delivered package " + str(', '.join(self.unload_ids)) + "]")
        print(self.simulation)
        self.simulation.event = True  # Informs GUI that the simulation requires another user input before continuing.


class Clock:
    """This class keeps track of time in the simulation."""
    def __init__(self, hour, minute, second):
        """Initializes the time keeping variables. O(1)."""
        self.hour = hour
        self.minute = minute
        self.second = second

    def __str__(self):
        """Returns a string version of the clock class in non-military time. O(1)."""
        return "%2d:%02d:%02d %s" % (self.hour_mod(), self.minute, self.second, ("AM", "PM")[self.hour >= 12])

    def tick_second(self):
        """This function increments time 1 second for each simulation tick_second. Adjusts hours and minutes. O(1)."""
        self.second = self.second + 1  # Increase clock time by 1 second.
        if self.second >= 60:  # If seconds are greater than 59, reset seconds to 0 and increment minutes by 1.
            self.second = 0
            self.minute = self.minute + 1
            if self.minute >= 60:  # If minutes are greater than 59, reset minutes to 0 and increment hours by 1.
                self.minute = 0
                self.hour = self.hour + 1
                if self.hour >= 24:  # If hours are greater than 23, reset hours back to 0.
                    self.hour = 0

    def hour_mod(self):
        """Returns clock hours in non-military time. Ensures hours does not equal 0. O(1)."""
        return ((self.hour-1) % 12)+1

    def compare_time(self, input_time):
        """Returns True if the input time and the current time are equal. Return false if times are not equal. O(1)."""
        input_time = self.split_time(input_time)
        return self.hour == input_time[0] and self.minute == input_time[1] and self.second == input_time[2]

    def set_time(self, input_time):
        """Set current time on the clock according to the input time string. O(1)."""
        input_time = self.split_time(input_time)
        self.hour = input_time[0]
        self.minute = input_time[1]
        self.second = input_time[2]

    def split_time(self, input_time):
        """Takes a time string and splits it into hours, minutes, and seconds. O(N)."""
        input_time = list(input_time.split(':'))  # Splits time string.
        return [int(x) for x in input_time]  # Converts all strings to integers.


class HashTable:
    """This class is a simple hash table to keep track of data for all package IDs. Can dynamically resize itself."""
    def __init__(self, size):
        """Setup hash table variables. O(N)."""
        self.size = size
        self.slots = [None] * self.size
        self.data = [None] * self.size

    def __len__(self):
        """Method to return hash table size. O(1)."""
        return int(self.size)

    def __contains__(self, key):
        """Method to determine if key is in hash table. O(1)."""
        if self.__getitem__(key) is None:
            return False
        return True

    def __getitem__(self, key):
        """Method to get data from hash table. O(1)."""
        return self.get(key)

    def __setitem__(self, key, data):
        """Method to put items in hash table. O(1)."""
        self.put(key, data)

    def __str__(self):
        """Prints all keys and values in the hash table. O(N)."""
        table_string = "\nPackage Hash Table\n"  # Variable to contain the hash table string.
        for slot in self.slots:
            if slot is None:
                pass  # Ignores empty items in hash table.
            else:
                table_string = table_string + repr(slot) + ": " + repr(self.get(slot)) + "\n"  # Append data.
        return table_string

    def put(self, key, data):
        """Stores the value of a key and data in the hash table. If no available slots are found, print error. O(1)."""
        hash_value = self.hash_function(key, len(self.slots))  # Get hash value of key.
        hash_value_start = hash_value

        # Allowed hash table to dynamically adjust size as package count increases.
        load_factor = len([a for a in self.data if a is not None]) / len(self)
        if load_factor >= .7:  # If hash table load exceeds 70%, double hash table size and rehash all items.
            temp_slots = [None] * self.size
            temp_data = [None] * self.size
            self.size *= 2
            self.slots = self.slots + temp_slots
            self.data = self.data + temp_data

        if self.slots[hash_value] is None:  # If slot corresponding to hash value is empty, set slot and data.
            self.slots[hash_value] = key
            self.data[hash_value] = data
        else:
            if self.slots[hash_value] == key:  # If slot corresponding to hash value is equal to key, replace data.
                self.data[hash_value] = data  # replace
            else:  # If slot corresponding to hash value is not equal to key and not empty, rehash hash value.
                next_slot = self.rehash(hash_value, len(self.slots))
                while self.slots[next_slot] is not None and self.slots[next_slot] != key:  # Keeps rehashing.
                    next_slot = self.rehash(next_slot, len(self.slots))
                    if hash_value_start == next_slot:  # If we looped through entire hash table, break loop.
                        print('Error: Hash table is full. The data was not able to be stored.')
                        break
                if self.slots[next_slot] is None:  # Set slot and data.
                    self.slots[next_slot] = key
                    self.data[next_slot] = data
                else:
                    self.data[next_slot] = data  # Replace data.

    def get(self, key):
        """Returns the value of a specific key in the hash table. If slot for key is not found, return None. O(1)."""
        start_slot = self.hash_function(key, len(self.slots))  # Gets hash value of key.
        position = start_slot  # Current position is hash value.
        data = None

        while self.slots[position] is not None:
            if self.slots[position] == key:  # Key is found, set data and break loop.
                data = self.data[position]
                break
            else:  # Key is not found, rehash at new position.
                position = self.rehash(position, len(self.slots))
                if position == start_slot:  # If looped through entire hash table, break loop.
                    break

        return data

    def hash_function(self, key, size):
        """Returns remainder of being divided by hash table size. O(1)."""
        return key % size

    def rehash(self, old_hash, size):
        """Increases hash slot by 1 if previous hash value had a collision. O(1)."""
        return (old_hash + 1) % size
