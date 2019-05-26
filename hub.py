from settings import *
import collections
import random


class Hub:
    """This is the HUB class that handles all package storing and loading logistics."""
    def __init__(self, sim, import_packages):
        """Initializes recursive variables and warehouse variables."""
        self.simulation = sim  # Reference to simulation.
        self.truck = None  # Reference to truck.
        self.fastest_route = [INT_MAX, [INT_MAX], INT_MAX]  # Stores fastest Hamiltonian_Cycle route data.
        self.matrix = []  # Subset of the full distance matrix.
        self.basecase = []  # Basecase to terminate Hamiltonian_Cycle recursive calls.
        self.urgent_addresses = []  # Address IDs of urgent packages.
        self.unique_count = 0  # Count of unique addresses.
        self.do_not_ship_packages = []  # Packages that will not be loaded onto truck.
        self.do_not_ship_addresses = []  # Address IDs that will not be loaded onto truck.
        self.do_not_ship(import_packages[:])  # Function call to construct do_not_ship variables.
        self.warehouse = [x for x in import_packages if x not in self.do_not_ship_packages]  # Package selection pool.
        self.reset = False

    def do_not_ship(self, packages):
        """Loops through all packages and identifies delayed + bad address packages.
        Ensures that these packages are removed from the package selection pool."""
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
        """Contains all function calls that load up the truck."""
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
        self.matrix = []
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
        """Remove all packages that are specific to Truck 2 from available packages if our Truck ID is 1.
        As we remove these packages, remove any packages that share an address with these packages. O(N^2)."""
        if self.truck.identifier == 1:
            for package in hub:
                if package[2] == "Truck 2":  # Checks if package special notes is only loadable on Truck 2.
                    hub.remove(package)
                    for pair in hub[:]:  # Removes all packages that share the same address as package just removed.
                        if pair[-1] == package[-1]:
                            hub.remove(pair)
        return bay, ids, indexes, hub, count

    def load_urgent_packages(self, bay, ids, indexes, hub, count):
        """Identify all time-sensitive and group-sensitive packages. Preload these packages into truck. O(N)."""
        for package in hub[:]:
            if package[1] != "EOD" or package[2] == "Group":
                bay, ids, indexes, hub, count = self.loading(package, bay, ids, indexes, hub, count)
                self.urgent_addresses.append(package[-1])  # Stores urgent_addresses address indexes.
        return bay, ids, indexes, hub, count

    def load_address_pairs(self, bay, ids, indexes, hub, count):
        """Load all packages that share the same address as the packages currently in bay. O(N)."""
        if count > 0:
            for package in hub[:]:
                if package[-1] in indexes:  # Checks if package address is equal to a currently loaded package address.
                    bay, ids, indexes, hub, count = self.loading(package, bay, ids, indexes, hub, count)
        return bay, ids, indexes, hub, count

    def unique_max_load(self, bay, ids, indexes, hub, count, preload):
        """If truck exceeds max load, remove all non-duplicate non-group packages until below thresh-hold. O(N)."""
        duplicate = [k for k, v in collections.Counter(indexes).items() if v > 1]  # Finds duplicate address indexes.
        if count > TRUCK_STORAGE_LIMIT:
            for package in bay[:]:
                # This chunk of code only removes non-group packages if preload is occurring. The reason why is because
                # all preloaded packages have a deadline so all of them are equally important.
                if package[2] != "Group" and package[-1] not in duplicate and preload:
                    bay, ids, indexes, hub, count = self.unloading(package, bay, ids, indexes, hub, count)

                # This chunk of code only removes non-group non-urgent_addresses packages if preload is not occurring. The reason
                # why is because we do not want to accidentally remove urgent_addresses packages to reduce package count.
                elif package[1] == 'EOD' and package[2] != "Group" and package[-1] not in duplicate:
                    bay, ids, indexes, hub, count = self.unloading(package, bay, ids, indexes, hub, count)
                if count <= TRUCK_STORAGE_LIMIT:  # Breaks For loop when truck is equal or below storage limit.
                    break
        return bay, ids, indexes, hub, count

    def duplicate_max_load(self, bay, ids, indexes, hub, count):
        """If truck exceeds max load, remove pairs of duplicate non-group packages until below thresh-hold. O(N^2)."""
        if count > TRUCK_STORAGE_LIMIT:
            while True:
                for package in bay[:]:
                    if package[2] != "Group":  # Ensures package being removed is not group package.
                        for pair in bay[:]:
                            if pair[-1] == package[-1]:  # Removes packages that share address with removed package.
                                bay, ids, indexes, hub, count = self.unloading(pair, bay, ids, indexes, hub, count)
                        break  # Before removing further packages, breaks For loop to check if below storage limit.
                if count <= TRUCK_STORAGE_LIMIT:  # Breaks While loop if truck is equal or below storage limit.
                    break
        return bay, ids, indexes, hub, count

    def seed_package_selector(self, bay, ids, indexes, hub, count):
        """This function randomly picks packages and calculates the minimum distance to travel it."""
        if count == 16:  # Skips trucks already at full capacity. No more packages can be loaded onto it.
            return bay, ids, indexes, hub, count
        print("\nSelecting the most optimal packages to load onto truck " + str(self.truck.identifier) + ".")

        # Declare reset variables and best result variables.
        reset_bay, reset_ids, reset_indexes, reset_hub, reset_count = bay[:], ids[:], indexes[:], hub[:], count
        best, best_bay, best_ids, best_indexes, best_hub, best_count = [INT_MAX], None, None, None, None, None
        for seed in range(1, SEED_COUNT + 1):  # Runs seed selection loop.
            bay, ids, indexes, hub, count = reset_bay[:], reset_ids[:], reset_indexes[:], reset_hub[:], reset_count
            bay, ids, indexes, hub, count = self.seed_sample(bay, ids, indexes, hub, count)
            bay, ids, indexes, hub, count = self.load_address_pairs(bay, ids, indexes, hub, count)
            bay, ids, indexes, hub, count = self.unique_max_load(bay, ids, indexes, hub, count, False)
            bay, ids, indexes, hub, count = self.duplicate_max_load(bay, ids, indexes, hub, count)
            bay, ids, indexes, hub, count, best, record = self.seed_best(bay, ids, indexes, hub, count, best, seed)
            if record:  # If new fastest_route time record was found, redefine best result variables.
                best_bay, best_ids, best_indexes, best_hub, best_count = bay, ids, indexes, hub, count
            if len(hub) == 0:  # If HUB empty, only 1 seed exists. Break loop.
                break

        return best_bay, best_ids, best_indexes, best_hub, best_count

    def seed_sample(self, bay, ids, indexes, hub, count):
        """Fill the truck with a random sample packages. Truck is now at max capacity or hub is now empty. O(N)."""
        try:
            random_sample = random.sample(hub, TRUCK_STORAGE_LIMIT - count)  # Random sample to completely fill truck.
        except ValueError:
            random_sample = random.sample(hub, len(hub))  # Random sample to partially fill truck.
        for package in random_sample:  # Load random sample onto truck.
            bay, ids, indexes, hub, count = self.loading(package, bay, ids, indexes, hub, count)
        return bay, ids, indexes, hub, count

    def seed_best(self, bay, ids, indexes, hub, count, best, seed):
        """Identifies the fastest_route route for the current package selection seed. O(K)."""
        if self.fastest_route[0] < best[0]:  # Saves value of best seed.
            best = self.fastest_route[:]
        self.hamiltonian_cycle_setup(indexes, count, True)  # Finds fastest_route path and stores it in self.fastest_route variable.
        if self.fastest_route[0] < best[0]:  # Checks if current seed is faster than all older seeds.
            print("Seed Generation " + str(seed) + " / " + str(SEED_COUNT) + ": Fastest Path " +
                  str(self.fastest_route[0]) + ": Package IDs " + str(ids))
            record = True  # This variable states if the current seed is the current record holder for lowest miles.
        else:
            print("Seed Generation " + str(seed) + " / " + str(SEED_COUNT))
            record = False
        return bay, ids, indexes, hub, count, best, record

    def hamiltonian_cycle_setup(self, indexes, count, fast):
        """This function sets up some critical variables for the hamiltonian cycle function. O(N^2)."""
        unique_addresses = list(set(indexes))  # Identify only unique addresses for all loaded packages.
        unique_addresses.append(0)  # Include HUB address.
        unique_addresses.sort()  # Sort addresses from smallest to largest index. HUB is first item in list.

        self.matrix = []  # This matrix will contain distance weights of only the unique addresses.
        for row_index in unique_addresses:  # Loops through all addresses
            subset = []  # Contains a subset of the distance weights for a particular address.
            row = self.simulation.distances[row_index]  # Get the full row of the distance weights for that address.
            for col_index in unique_addresses:  # Appends only specific columns of data for that row to subset.
                subset.append(row[col_index])
            self.matrix.append(subset)  # Add the subset to matrix.
        #                                                                  ___0_____1_____2_____3_____4__
        # Example                                                        0| [0.0,  5.7,  1.6,  7.1,  10.6]
        # Assume the full distance matrix appeared like this:            1| [7.0,  0.0,  2.5,  3.6,  8.0 ]
        #                                                                2| [1.0,  10.4, 0.0,  14.1, 5.5 ]
        # Thus, this means that there are 5 address indexes              3| [5.2,  4.7,  3.1,  0.0,  1.3 ]
        # contained in the entire matrix. If unique_addresses            4| [11.2, 3.7,  6.7,  9.4,  0.0 ]
        # variable contained indexes [0, 2, 4], then our subset
        # matrix must only contain the distance weights
        # of the full matrix for those indexes.                            ___0_____2_____4__
        #                                                                0| [0.0,  1.6,  10.6]
        # The subset matrix will appear like this:                       2| [1.0,  0.0,  5.5 ]
        #                                                                4| [11.2, 6.7,  0.0 ]

        self.unique_count = len(unique_addresses)  # Counts how many unique_count are in the matrix.
        self.basecase = [True] * self.unique_count  # Creates basecase that checks if all unique_count are visited.
        bitmap = [False] * self.unique_count  # Contains a binary list of unique_count that have been visited.
        bitmap[0] = True  # Change the first address of bitmap to visited since first address is HUB.
        if fast:  # If fast, the function will only find the lowest total miles.
            self.hamiltonian_cycle_fast(bitmap, 0, 0)
        else:  # If slow, the function will find the lowest total miles, distance history, and location history.
            self.hamiltonian_cycle_slow(bitmap, 0, 0, [], [0])

        return unique_addresses

    def hamiltonian_cycle_fast(self, bitmap, position, cost):
        """
        This is a recursive function called hamiltonian_cycle_fast. It is called fast because it keeps track of the
        bitmap, the position, and cost. These variables to transfer down each recursive call are not costly. This
        function is used primarily for the seed_package_selector function, meaning that if we put select a random
        set of packages, the function wants to know what is the least amount of miles those packages can all be
        delivered.

        Location history and cost history is not important because if the seed is bad, none of those variables will be
        stored. So this function runs quickly, returning only the minimum total miles to deliver all packages, and if it
        is confirmed that those packages are indeed the best sequence of packages to deliver for the truck, then
        hamiltonian_cycle_slow will be called again to find the location history and cost history variables.

        Additional comments and descriptions of the algorithm are covered in the hamiltonian_cycle_slow function. O(N!).
        """
        if bitmap == self.basecase:
            if self.truck.last_trip:
                cost = round(cost, 2)
            else:
                cost = round(cost + self.matrix[position][0], 2)
            if cost < self.fastest_route[0]:
                self.fastest_route[0] = cost
                return
        if cost >= self.fastest_route[0]:
            return
        for next_city in range(1, self.unique_count):
            if not bitmap[next_city]:
                new_mask = bitmap[:]
                new_mask[next_city] = True
                self.hamiltonian_cycle_fast(new_mask, next_city, cost + self.matrix[position][next_city])

    def hamiltonian_cycle_slow(self, bitmap, position, cost, weights, history):
        """
        This is a recursive function called hamiltonian_cycle_slow. It is called slow because it keeps track of the
        bitmap, the position, cost, the weights (costly), and the history (costly). Weights and history are lists that
        contain the route address indexes and the route address weights to traverse the route, so it takes more time
        to process this information. This information is needed later to set the truck route and truck miles added.

        The algorithm is set up so it begins with a bitmap. Let's say there are 4 cities total, and this function
        wants to find the shortest distance to traverse all 4 cities. The function begins at City 1 so the bitmap would
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
         for the least amount of miles to traverse the cities. The history of the traversal is saved, along with the
         weights each traversal, in a list. The second recursive call 14.8 > 12.4, which is inferior, so it is skipped.
         Third recursive call is 7.6 < 12.4, so that recursive call has the location and weight history overwrite
         the previous record holder. Finally, the steps repeat for 9.1, 16.2, and 15.9. At the end of the recursive
         cycle, the record holder of 7.6, along with the location and weight history, is saved in self.fastest_route
         in indexes 0, 1, and 2 respectively. These values are then used for later manipulation.

         Runtime is O(N!) since it recursively calls itself N - 1 times for each call. Improvements were made to have
         an if statement terminate a recursive call early. For instance, if we know that the fastest_route time is 7.6
         and one recursive call is at Layer 2, but already has a weight of say 8.0 then it could be confirmed that no
         matter how low the weights are for visiting the remaining layers, it will not be faster than what is currently
         the record. A return statement is issued terminating the recursive calls early. O(N!).
         """
        if bitmap == self.basecase:  # Base case checks all unique_count are visited.
            for location in history[len(history):]:
                if location == 21:  # Checks if this route will have the 9:00 AM packages not delivered on time.
                    return
            if self.truck.last_trip:  # If this is the truck's last trip, ignore cost of returning to hub.
                cost = round(cost, 2)
            else:  # If this is not the truck's last trip, add the cost and index of returning to the HUB to lists.
                history.append(0)
                weights.append(self.matrix[position][0])
                cost = round(cost + self.matrix[position][0], 2)
            if cost <= self.fastest_route[0]:  # Checks if fastest_route time (lowest miles). If confirmed then update variables.
                self.fastest_route[0] = cost
                self.fastest_route[1] = history
                self.fastest_route[2] = weights
                return

        if cost > self.fastest_route[0]:  # Early termination checks if cost is greater than the smallest cost.
            return

        for next_city in range(1, self.unique_count):  # Loops through all cities. Each loop does N recursive calls.
            if not bitmap[next_city]:  # Checks if next_city is a city that has not been visited. Visit that city.
                new_mask = bitmap[:]  # Make data copies to prevent data contamination between each recursive call.
                new_history = history[:]
                new_weights = weights[:]
                new_mask[next_city] = True  # Update bitmap city index as True (visited).
                new_history.append(next_city)  # Appends current city to the history address list.
                new_weights.append(self.matrix[position][next_city])  # Appends cost to weights list.
                new_cost = cost + self.matrix[position][next_city]  # Updates the total cost of all miles driven.
                self.hamiltonian_cycle_slow(new_mask, next_city, new_cost, new_weights, new_history)  # Recursive call.

    def finalize_variables(self, uniques, bay):
        """This function adjusts several variables now that the lowest mileage route is found. O(N)."""
        # Translate subset matrix package_map to the full simulation matrix package_map.
        for indexes, location in enumerate(self.fastest_route[1][:]):
            self.fastest_route[1][indexes] = uniques[location]

        # If any urgent_addresses packages appear in the last index of history, throw out route and restart function.
        # This is a brute force method to ensure all deliveries for truck 2 arrive at their destination on time.
        if self.fastest_route[1][-2] in self.urgent_addresses and self.truck.identifier == 2:
            print("Error: One of the packages will not make it to its destination on time. Restarting function.")
            self.reset = True
        else:
            # Remove packages from warehouse.
            for package in bay:
                self.warehouse.remove(package)

    def finalize_truck(self, count, bay):
        """Load the truck with the packages, route map, and route weights in respective order. O(N^2)."""
        if self.reset:
            self.load_truck(self.truck)
            return
        self.truck.count = count
        self.truck.available = False
        self.truck.address_map = self.fastest_route[1][:]
        self.truck.address_map.pop(0)
        self.truck.weight_map = self.fastest_route[2][:]
        self.truck.weight = self.fastest_route[0]
        for indexes in self.fastest_route[1]:
            for package in bay:
                if package[-1] == indexes:  # Loads truck with package IDs in specific order.
                    self.truck.package_map.append(int(package[0]))
                    self.truck.bay.append(package)
        self.truck.next_weight = self.truck.weight_map[0]  # Next route weight is always first address ID

        for package in self.truck.package_map:  # Update hash table status.
            self.simulation.hash_table[package][-1] = "Loaded on Truck " + str(self.truck.identifier)

        # Print Simulation. Accept another GUI input.
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
        """This function make all delayed packages located in the HUB available. It makes Truck 2 available. O(N^2)."""
        for package in self.do_not_ship_packages[:]:
            if package[2] != "Bad Address":  # Checks if package special notes is delayed package without bad address.
                available = self.do_not_ship_packages.pop(0)  # Removes package from do_not_ship.
                try:  # Removes address from do_not_ship. Sometimes address is already removed so catch ValueError.
                    self.do_not_ship_addresses.remove(available[-1])
                except ValueError:
                    pass
                self.simulation.hash_table[int(available[0])][-1] = "Ready for pickup"  # Updates package status.
                self.warehouse.append(available)  # Finally push package to warehouse.
        print("\nSPECIAL EVENT: Packages that were delayed at the airport are now available for pickup -"
              + ("", " ")[self.simulation.time.hour >= 10] + str(self.simulation.time) + ".")  # Print event.
        self.simulation.truck_2.available = True  # Truck 2 was waiting for package arrival. Now it can be available.
        self.simulation.event = True  # Informs GUI that the simulation requires another user input before continuing.
        self.simulation.gui()  # Call GUI again, otherwise Truck 2 would immediately start loading before next GUI call.

    def address_fixed(self):
        """This function fixes bad addresses for packages located in the HUB. O(N^2)"""
        for package in self.do_not_ship_packages[:]:
            if package[-2] == "Bad Address":  # Checks if package special notes is a bad address.
                package[-1] = "410 S State St; 84111"  # Updates incorrect address to correct address.
            available = self.do_not_ship_packages.pop(0)  # Removes package from do_not_ship.
            try:  # Removes address from do_not_ship. Sometimes address is already removed so catch ValueError.
                self.do_not_ship_addresses.remove(available[-1])
            except ValueError:
                pass
            self.simulation.hash_table[int(available[0])][-1] = "Ready for pickup"  # Updates package status.
            self.simulation.hash_table[int(available[0])][1] = "410 S State St"  # Updates package street.
            self.simulation.hash_table[int(available[0])][3] = "84111"  # Updates package zipcode.
            self.warehouse.append(available)  # Finally push package to warehouse.
        print("\nSPECIAL EVENT: Packages that had bad addresses are now fixed and are available for pickup -"
              + ("", " ")[self.simulation.time.hour >= 10] + str(self.simulation.time) + ".")  # Print event.
        self.simulation.event = True  # Informs GUI that the simulation requires another user input before continuing.
