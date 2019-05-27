from settings import *
import collections
import random


class Hub:
    """This is the Hub class that handles all package storing and loading logistics."""
    def __init__(self, sim, import_packages):
        """Initializes recursive variables and warehouse variables."""
        self.simulation = sim  # Reference to simulation.
        self.truck = None  # Reference to truck.
        self.fastest_route = [INT_MAX, [INT_MAX], INT_MAX]  # Stores fastest Hamiltonian_Cycle route data.
        self.subset_matrix = []  # Subset of the full distance matrix.
        self.basecase = []  # Basecase to terminate recursive calls.
        self.urgent_addresses = []  # Address IDs of urgent packages.
        self.unique_count = 0  # Count of unique addresses.
        self.do_not_ship_packages = []  # Packages that will not be loaded onto truck.
        self.do_not_ship_addresses = []  # Address IDs that will not be loaded onto truck.
        self.do_not_ship(import_packages[:])  # Function call to construct do_not_ship variables.
        self.warehouse = [x for x in import_packages if x not in self.do_not_ship_packages]  # Package selection pool.
        self.reset = False

    def do_not_ship(self, packages):
        """Loops through all packages and identifies delayed + bad address packages.
        Ensures that these packages are removed from the package selection pool. O(N^2)."""
        # Remove excess data columns that are not important for loading the truck. O(N).
        for package in packages:
            for index in [9, 6, 4, 3, 2, 1]:
                package.pop(index)

        # Remove delayed packages from selection pool. O(N).
        for package in packages[:]:
            if package[2] == "Dropped 9:05":
                self.do_not_ship_packages.append(package)
                self.do_not_ship_addresses.append(package[-1])
                packages.remove(package)

        # Remove packages that share addresses with delayed packages from selection pool. O(N).
        for package in packages[:]:
            if package[-1] in self.do_not_ship_addresses:
                package[3] = "Unavailable at HUB"
                self.do_not_ship_packages.append(package)
                packages.remove(package)

        # Remove bad address packages from selection pool. O(N).
        for package in packages[:]:
            if package[2] == "Bad Address":
                self.do_not_ship_packages.append(package)
                self.do_not_ship_addresses.append(package[-1])
                packages.remove(package)

    def load_truck(self, truck):
        """Contains all function calls that load up the truck. O(M * N!)."""
        # Step 1: The truck enters the hub. Class variables are checked, reset, and tailored.
        self.truck_last_trip(truck)
        bay, ids, indexes, hub, count = self.setup_variables()
        bay, ids, indexes, hub, count = self.truck_specific_packages(bay, ids, indexes, hub, count)

        # Step 2: The truck is loaded with urgent packages that have delivery deadlines.
        bay, ids, indexes, hub, count = self.load_urgent_packages(bay, ids, indexes, hub, count)
        bay, ids, indexes, hub, count = self.load_address_pairs(bay, ids, indexes, hub, count)
        bay, ids, indexes, hub, count = self.unique_max_load(bay, ids, indexes, hub, count, True)
        bay, ids, indexes, hub, count = self.duplicate_max_load(bay, ids, indexes, hub, count)

        # Step 3: The truck is loaded with the best random set of packages.
        bay, ids, indexes, hub, count = self.seed_package_selector(bay, ids, indexes, hub, count)

        # Step 4: The truck finds the lowest mileage route.
        uniques = self.hamiltonian_cycle_setup(indexes, count, False)

        # Step 5: The truck departs the hub with all packages loaded.
        self.finalize_variables(uniques, bay)
        self.finalize_truck(count, bay)

    def truck_last_trip(self, truck):
        """Determines if this is the truck's last trip from the Hub.
        Truck 1 will not return to the Hub when it departs as Truck 2 can handle the remaining package deliveries.
        Truck 2 will not return to the Hub if the Hub is empty. O(1)."""
        self.truck = truck
        if self.truck.identifier == 1 or len(self.warehouse) <= TRUCK_STORAGE_LIMIT:
            self.truck.last_trip = True

    def setup_variables(self):
        """Reset class variables. Construct function variables. O(K)."""
        # Reset class variables.
        self.basecase = []
        self.subset_matrix = []
        self.basecase = []
        self.urgent_addresses = []
        self.unique_count = 0
        self.fastest_route = [INT_MAX, [INT_MAX], INT_MAX]
        self.reset = False

        # Construct function variables.
        count = 0  # Count of packages.
        bay = []  # List of packages.
        ids = []  # List of package IDs.
        indexes = []  # List of address IDs.
        hub = self.warehouse[:]  # Copy of package selection pool.
        return bay, ids, indexes, hub, count

    def truck_specific_packages(self, bay, ids, indexes, hub, count):
        """Remove all packages that are specific to Truck 2 from available packages if Truck ID is 1.
        As these packages are removed, remove any packages that share an address with these packages. O(N^3)."""
        if self.truck.identifier == 1:
            for package in hub[:]:
                if package[2] == "Truck 2":
                    hub.remove(package)
                    for pair in hub[:]:
                        if pair[-1] == package[-1]:
                            hub.remove(pair)
        return bay, ids, indexes, hub, count

    def load_urgent_packages(self, bay, ids, indexes, hub, count):
        """Load all time-sensitive and group-sensitive packages onto the truck. Store their addresses. O(N^2)."""
        for package in hub[:]:
            if package[1] != "EOD" or package[2] == "Group":
                bay, ids, indexes, hub, count = self.loading(package, bay, ids, indexes, hub, count)
                self.urgent_addresses.append(package[-1])
        return bay, ids, indexes, hub, count

    def load_address_pairs(self, bay, ids, indexes, hub, count):
        """Load all packages that share an address with any packages currently loaded. O(N^2)."""
        if count > 0:
            for package in hub[:]:
                if package[-1] in indexes:
                    bay, ids, indexes, hub, count = self.loading(package, bay, ids, indexes, hub, count)
        return bay, ids, indexes, hub, count

    def unique_max_load(self, bay, ids, indexes, hub, count, urgent):
        """Remove packages that have unique addresses until below truck capacity. O(N^2)."""
        if count > TRUCK_STORAGE_LIMIT:
            duplicate = [k for k, v in collections.Counter(indexes).items() if v > 1]
            for package in bay[:]:
                # Removes non-grouped, unique-address packages.
                if package[2] != "Group" and package[-1] not in duplicate and urgent:
                    bay, ids, indexes, hub, count = self.unloading(package, bay, ids, indexes, hub, count)
                # Removes non-urgent, non-grouped, unique-address packages.
                elif package[1] == 'EOD' and package[2] != "Group" and package[-1] not in duplicate:
                    bay, ids, indexes, hub, count = self.unloading(package, bay, ids, indexes, hub, count)
                # Breaks loop when equal or below storage limit.
                if count <= TRUCK_STORAGE_LIMIT:
                    break
        return bay, ids, indexes, hub, count

    def duplicate_max_load(self, bay, ids, indexes, hub, count):
        """Remove packages that have shared addresses until below truck capacity. O(N^3)."""
        if count > TRUCK_STORAGE_LIMIT:
            while True:
                for package in bay[:]:
                    # Removes non-grouped, shared-address packages.
                    if package[2] != "Group":
                        for pair in bay[:]:
                            if pair[-1] == package[-1]:
                                bay, ids, indexes, hub, count = self.unloading(pair, bay, ids, indexes, hub, count)
                        break
                # Breaks loop when equal or below storage limit.
                if count <= TRUCK_STORAGE_LIMIT:
                    break
        return bay, ids, indexes, hub, count

    def seed_package_selector(self, bay, ids, indexes, hub, count):
        """Randomly selects package to load and finds the minimum distance to deliver all packages. This function will
        loop M times and save the best result upon completion. These results are then returned. O(M * N!)."""
        if count == 16:  # Skip trucks at full capacity.
            return bay, ids, indexes, hub, count
        print("\nSelecting the most optimal packages to load onto truck " + str(self.truck.identifier) + ".")

        # Declare reset variables and best result variables. O(K).
        reset_bay, reset_ids, reset_indexes, reset_hub, reset_count = bay[:], ids[:], indexes[:], hub[:], count
        best, best_bay, best_ids, best_indexes, best_hub, best_count = [INT_MAX], None, None, None, None, None

        # Runs seed selection loop. O(M * N!).
        for seed in range(1, SEED_COUNT + 1):
            bay, ids, indexes, hub, count = reset_bay[:], reset_ids[:], reset_indexes[:], reset_hub[:], reset_count
            bay, ids, indexes, hub, count = self.seed_random_sample(bay, ids, indexes, hub, count)
            bay, ids, indexes, hub, count = self.load_address_pairs(bay, ids, indexes, hub, count)
            bay, ids, indexes, hub, count = self.unique_max_load(bay, ids, indexes, hub, count, False)
            bay, ids, indexes, hub, count = self.duplicate_max_load(bay, ids, indexes, hub, count)
            bay, ids, indexes, hub, count, best, record = self.seed_minimum(bay, ids, indexes, hub, count, best, seed)
            # Saves best results if minimum distance is lowest.
            if record:
                best_bay, best_ids, best_indexes, best_hub, best_count = bay, ids, indexes, hub, count
            if len(hub) == 0:
                break

        return best_bay, best_ids, best_indexes, best_hub, best_count

    def seed_random_sample(self, bay, ids, indexes, hub, count):
        """Load the truck with a random sample of packages. O(N^2)."""
        try:
            random_sample = random.sample(hub, TRUCK_STORAGE_LIMIT - count)
        except ValueError:
            random_sample = random.sample(hub, len(hub))
        for package in random_sample:
            bay, ids, indexes, hub, count = self.loading(package, bay, ids, indexes, hub, count)
        return bay, ids, indexes, hub, count

    def seed_minimum(self, bay, ids, indexes, hub, count, best, seed):
        """Finds the minimum distance to deliver all packages. O(K)."""
        # Saves record lowest distance.
        if self.fastest_route[0] < best[0]:
            best = self.fastest_route[:]
        # Hamiltonian Cycle will find the minimum distance for this seed.
        self.hamiltonian_cycle_setup(indexes, count, True)
        # Checks if this seed is the record lowest distance.
        if self.fastest_route[0] < best[0]:
            print("Seed Generation " + str(seed) + " / " + str(SEED_COUNT) + ": Fastest Path " +
                  str(self.fastest_route[0]) + ": Package IDs " + str(ids))
            record = True
        else:
            print("Seed Generation " + str(seed) + " / " + str(SEED_COUNT))
            record = False
        return bay, ids, indexes, hub, count, best, record

    def hamiltonian_cycle_setup(self, indexes, count, fast):
        """Sets up critical variables for the hamiltonian cycle function. O(N!)."""
        # Identify unique addresses for loaded packages.
        unique_addresses = list(set(indexes))
        unique_addresses.append(0)
        unique_addresses.sort()

        # Construct subset matrix to contain the travel distances of unique addresses.
        #                                                                     0     1     2     3     4
        #                            Example                             0  [0.0,  5.7,  1.6,  7.1,  10.6]
        #                                                                1  [7.0,  0.0,  2.5,  3.6,  8.0 ]
        #            Full distance matrix with [0, 1, 2, 3, 4]:          2  [1.0,  10.4, 0.0,  14.1, 5.5 ]
        #                                                                3  [5.2,  4.7,  3.1,  0.0,  1.3 ]
        #                                                                4  [11.2, 3.7,  6.7,  9.4,  0.0 ]
        #
        #                                                                     0     1     2
        #                                                                0  [0.0,  1.6,  10.6]
        #                The subset matrix with [0, 2, 4]:               1  [1.0,  0.0,  5.5 ]
        #                                                                2  [11.2, 6.7,  0.0 ]
        self.subset_matrix = []
        for row_index in unique_addresses:
            subset = []
            row = self.simulation.distances[row_index]
            for col_index in unique_addresses:
                subset.append(row[col_index])
            self.subset_matrix.append(subset)

        # Set up critical recursive variables.
        self.unique_count = len(unique_addresses)  # Number of unique addresses.
        self.basecase = [True] * self.unique_count  # Basecase of all locations visited.
        bitmap = [False] * self.unique_count  # List of locations visited.
        bitmap[0] = True

        # If fast, will find minimum miles. If slow, will find minimum miles, location history, and distance history.
        if fast:
            self.hamiltonian_cycle_fast(bitmap, 0, 0)
        else:
            self.hamiltonian_cycle_slow(bitmap, 0, 0, [], [0])

        return unique_addresses

    def hamiltonian_cycle_fast(self, bitmap, position, cost):
        """
        This is a recursive function called hamiltonian_cycle_fast. It is called fast because it keeps track of the
        bitmap, the position, and cost. These variables, copied between each recursive call, are not costly.

        This function is used only for the seed_package_selector function. If a random selection of packages are loaded
        then the minimum number of miles to deliver all packages is the only interest. Location history and distance
        history is not important because only 1 seed will actually be used for the truck route, not several dozen. It
        is not optimal to compute the location and distance history for all seeds if all but one will be thrown out.
        Later, when the best seed is found, the location history and distance history can be calculated. O(N!).
        """
        if bitmap == self.basecase:
            if self.truck.last_trip:
                cost = round(cost, 2)
            else:
                cost = round(cost + self.subset_matrix[position][0], 2)
            if cost < self.fastest_route[0]:
                self.fastest_route[0] = cost
                return
        if cost >= self.fastest_route[0]:
            return
        for _next in range(1, self.unique_count):
            if not bitmap[_next]:
                new_bitmap = bitmap[:]
                new_bitmap[_next] = True
                self.hamiltonian_cycle_fast(new_bitmap, _next, cost + self.subset_matrix[position][_next])

    def hamiltonian_cycle_slow(self, bitmap, position, cost, distances, locations):
        """
        This is a recursive function called hamiltonian_cycle_slow. It is called slow because it keeps track of the
        bitmap, the position, cost, the distances (costly), and the locations (costly). Distances and locations are
        lists that contain the distance amount travel for each layer and the Address ID traveled to in that layer.
        This information takes more time to process, but it is used later to set up the truck route and truck miles.

        The algorithm is set up so it begins with a bitmap. Let's say there are 4 cities total, and this function
        wants to find the minimum distance to traverse all 4 cities. The function begins at City 1 so the bitmap would
        look like this [True, False, False, False], because city 1 located at index 0 has already been visited. The
        next step is to traverse the bitmap from index 0 to the last index and visit all cities. The bitmap (otherwise
        considered the basecase) would look like this [True, True, True, True] because all cities are visited.

        A recursive function could be built so that it first checks to see if the entire bitmap equals true. If not
        then it attempts to visit the next city. The attempt to visit the next city can be written as a for loop,
        one attempt is made for each city in the bitmap, and if it finds a city that has not been visited then
        an instruction statement will call the hamiltonian_cycle_slow function again and repeat the entire process
        until all cities are visited. Once the basecase is reached, then it rolls back up and triggers the next instance
        of the for loop, and going down the chain of traveling again, until all for loops are completed.

        The tree of recursive calls looks like this to look at all the weights of visiting 4 cities.

         Layer 1:                     ___________________[T,F,F,F]___________________                   One City Visited
                                     /                       |                       \
         Layer 2:                [T,T,F,F]               [T,F,T,F]               [T,F,F,T]            Two Cities Visited
                                /         \             /         \             /         \
         Layer 3:          [T,T,T,F]  [T,T,F,T]    [T,T,T,F]  [T,F,T,T]    [T,T,F,T]  [T,F,T,T]     Three Cities Visited
                               |          |            |          |            |          |
         Layer 4:          [T,T,T,T]  [T,T,T,T]    [T,T,T,T]  [T,T,T,T]    [T,T,F,T]  [T,T,T,T]      Four Cities Visited

         Total:              12.4       14.8          7.6        9.1         16.2       15.9         Traverse Route Cost

         The recursive function moves from left to right, meaning that the first recursive call will traverse the
         cities in order they appear in the list from first to last. The last recursive call will traverse the first
         city, then traverse the cities in order from last to second.

         In the case of the first recursive call, the weight to traverse all cities is 12.4. This is set as the record
         for the least amount of miles to traverse the cities. The location history and the distance history of the
         traversal is saved in separate lists. The second recursive call is 14.8, which is inferior so it is ignored.
         Third recursive call is 7.6, so that recursive call has the location and distance history overwrite the
         previous record data. Repeat these steps for 9.1, 16.2, and 15.9. At the end of the recursive cycle, the
         record holder of 7.6, along with the location and distance history, is saved in self.fastest_route in indexes
         0, 1, and 2 respectively. These values are used later.

         Runtime is O((N-1)!) or simply O(N!) since it recursively calls itself N - 1 times for each call. Improvements
         were made to have an if statement terminate a recursive call early. O(N!).
         """
        # Basecase checks all locations are visited.
        if bitmap == self.basecase:
            # Checks if packages are delivered on time.
            for location in locations[len(locations):]:
                if location == 21:
                    return
            # Checks if truck will or will not return to Hub.
            if self.truck.last_trip:
                cost = round(cost, 2)
            else:
                locations.append(0)
                distances.append(self.subset_matrix[position][0])
                cost = round(cost + self.subset_matrix[position][0], 2)
            # Checks if record for least amount of miles.
            if cost <= self.fastest_route[0]:
                self.fastest_route[0] = cost
                self.fastest_route[1] = locations
                self.fastest_route[2] = distances
                return

        # Checks if total miles (cost) is greater than the record.
        if cost > self.fastest_route[0]:
            return

        for _next in range(1, self.unique_count):  # Loops through all locations and open N - 1 recursive calls.
            if not bitmap[_next]:  # Checks if _next is a location that has not been visited. Visits it.
                new_bitmap = bitmap[:]  # Create data copies to prevent data contamination between each recursive call.
                new_locations = locations[:]
                new_distances = distances[:]
                new_bitmap[_next] = True  # Update bitmap location index as visited.
                new_locations.append(_next)  # Appends location to the location history.
                new_distances.append(self.subset_matrix[position][_next])  # Appends distance to distance history.
                new_cost = cost + self.subset_matrix[position][_next]  # Updates the total miles.
                self.hamiltonian_cycle_slow(new_bitmap, _next, new_cost, new_distances, new_locations)  # Recursive call

    def finalize_variables(self, uniques, bay):
        """Finalize variables and check to see packages get delivered on time before loading truck. O(N^2)."""
        # Translate the subset matrix address IDs back to full matrix address IDs.
        for indexes, location in enumerate(self.fastest_route[1][:]):
            self.fastest_route[1][indexes] = uniques[location]

        # If packages do not get delivered on time, reset loading function. Otherwise, remove packages from warehouse.
        if self.fastest_route[1][-2] in self.urgent_addresses and self.truck.identifier == 2:
            print("Error: One of the packages will not make it to its destination on time. Restarting function.")
            self.reset = True
        else:
            for package in bay:
                self.warehouse.remove(package)

    def finalize_truck(self, count, bay):
        """Load the truck with the packages, location history, and distance history in respective order. O(N^2)."""
        # Restarts the loading function if packages do not get delivered on time.
        if self.reset:
            self.load_truck(self.truck)
            return

        # Translates Hamiltonian_Cycle variables to truck object variables.
        self.truck.count = count
        self.truck.available = False
        self.truck.locations = self.fastest_route[1][:]
        self.truck.locations.pop(0)
        self.truck.distances = self.fastest_route[2][:]
        self.truck.cost = self.fastest_route[0]

        # Loads truck with package IDs in delivery order.
        for indexes in self.fastest_route[1]:
            for package in bay:
                if package[-1] == indexes:
                    self.truck.package_ids.append(int(package[0]))
                    self.truck.bay.append(package)
        self.truck.next_distance = self.truck.distances[0]

        # Update package hash table statuses.
        for package in self.truck.package_ids:
            self.simulation.hash_table[package][-1] = "Loaded on Truck " + str(self.truck.identifier)

        # Print Simulation and accept another GUI input.
        print("\n\n\n\n\n\n" + self.truck.buffer + "[Departed HUB Fully Loaded]\n" + str(self.simulation))
        self.simulation.event = True

    def unloading(self, package, bay, ids, indexes, hub, count):
        """Removes a package from the truck bay. Adjusts all variables and then returns them. O(N)."""
        bay.remove(package)
        ids.remove(package[0])
        indexes.remove(package[-1])
        hub.append(package)
        count = count - 1
        return bay, ids, indexes, hub, count

    def loading(self, package, bay, ids, indexes, hub, count):
        """Loads a package onto the truck bay. Adjusts all variables and then returns them. O(N)."""
        bay.append(package)
        ids.append(package[0])
        indexes.append(package[-1])
        hub.remove(package)
        count = count + 1
        return bay, ids, indexes, hub, count

    def flight_arrival(self):
        """Transforms all delayed packages located in the Hub. Make Truck 2 available. O(N^2)."""
        self.simulation.truck_2.available = True
        for package in self.do_not_ship_packages[:]:
            if package[2] != "Bad Address":
                # Removes address and packages from do_not_ship lists.
                available = self.do_not_ship_packages.pop(0)
                try:
                    self.do_not_ship_addresses.remove(available[-1])
                except ValueError:
                    pass
                # Updates package status and move package to warehouse.
                self.simulation.hash_table[int(available[0])][-1] = "Ready for pickup"
                self.warehouse.append(available)

        # Print event and accept another GUI input.
        print("\nSPECIAL EVENT: Packages that were delayed at the airport are now available for pickup -"
              + ("", " ")[self.simulation.time.hour >= 10] + str(self.simulation.time) + ".")
        self.simulation.event = True
        self.simulation.gui()

    def address_fixed(self):
        """Fixes bad addresses for packages located in the Hub. O(N^2)"""
        for package in self.do_not_ship_packages[:]:
            if package[-2] == "Bad Address":
                package[-1] = "410 S State St; 84111"
            # Removes address and packages from do_not_ship lists.
            available = self.do_not_ship_packages.pop(0)
            try:
                self.do_not_ship_addresses.remove(available[-1])
            except ValueError:
                pass
            # Updates package status and move package to warehouse.
            self.simulation.hash_table[int(available[0])][-1] = "Ready for pickup"
            self.simulation.hash_table[int(available[0])][1] = "410 S State St"
            self.simulation.hash_table[int(available[0])][3] = "84111"
            self.warehouse.append(available)

        # Print event and accept another GUI input.
        print("\nSPECIAL EVENT: Packages that had bad addresses are now fixed and are available for pickup -"
              + ("", " ")[self.simulation.time.hour >= 10] + str(self.simulation.time) + ".")
        self.simulation.event = True
