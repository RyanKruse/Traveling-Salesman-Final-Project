from settings import *
from hub import Hub
from objects import Truck, HashTable, Clock


class Simulation:
    """This class runs the simulation."""
    def __init__(self, prep):
        """Declare simulation variables. O(N)."""
        self.prepper = prep  # Contains a reference to prepper object.
        self.index_addresses = {v: k for k, v in prep.address_dictionary.items()}  # A reverse dictionary of addresses.
        self.distances = prep.distance_matrix  # Contains distance matrix table, which is a nested list of distances.
        self.packages = prep.package_table  # Contains package table, which is a nested list of packages.
        self.hash_table = HashTable(len(self.packages) + 1)  # Constructs hash table with size as package count.
        self.construct()  # Constructs Hash Table Items.
        self.time = Clock(0, 0, 0)  # Constructs Clock Object.
        self.hub = Hub(self, self.packages)  # Constructs HUB Object.
        self.truck_1 = Truck(self, 1, True, True, 41)  # Constructs Truck 1 Object.
        self.truck_2 = Truck(self, 2, False, False, 149)  # Constructs Truck 2 Object.
        self.gui_commands = ['Q', 'W', 'E', 'A', 'S', 'D']  # Contains a list of all GUI Commands.
        self.trucks = []  # Contains a list of all trucks.
        self.newline = "\n\n\n\n\n\n"  # Contains blank lines that appear between each simulation print.
        self.end = False  # GUI check to see if running simulation to end.
        self.event = True  # GUI check to see if an event has occurred.
        self.loop = False  # GUI check to see if simulation is complete.

    def __str__(self):
        """This prints valuable information about the state of the entire simulation. For simplicity sake, the
        simulation string is split up into rows and columns of data, denoted by the c#_r# variables. Going down the
        function, first column 1 is built, then column 2, up until column 6, where all columns and rows are combined
        then returned. Below is information about each column:
            Column 1) Adds blank spaces before the first truck string appears.
            Column 2) Contains the core construction of the first truck string.
            Column 3) Adds blank spaces before the second truck string appears.
            Column 4) Contains the core construction of the second truck string.
            Column 5) Adds blank spaces before the GUI Command string appears.
            Column 6) Contains information about the possible GUI commands that exist.

        The skeleton text for the truck is cited here: http://www.ascii-art.de/ascii/t/truck.txt. O(1)."""

        # If the hour clock on time switches from 1 digit to 2 digits (9 AM --> 10 AM), tab spaces are adjusted.
        clock_buffer_1 = ""
        clock_buffer_2 = "-"
        if self.time.hour >= 10:
            clock_buffer_1 = " "
            clock_buffer_2 = ""

        # Truck Line Buffers - This determines how much space appears between the text that appears in the truck and
        # the string character | which is denoted as the truck cargo door.
        add_1 = 68
        add_2 = 60
        add_3 = 64
        add_4 = 46

        # Truck 1 Line Buffer Subtraction Amount - Because the text length that appears inside the truck dynamically
        # changes, this subtracts that text length from the Truck Line Buffer so that the | character appears correctly.
        sub_1 = len(str(self.truck_1.package_ids))
        sub_2 = len(str(self.truck_1.locations))
        sub_3 = len(str(self.truck_1.distances)) + len(str(round(self.truck_1.weight, 1)))
        sub_4 = len(str(round(self.truck_1.miles, 1))) + len(str(self.truck_1.count)) + \
            len(str(self.index_addresses[self.truck_1.current]))

        # Example: A box appears as...                 _____________
        #                                             | D: []       |
        #                                             |_____________|
        #
        # If the list of D were to suddenly contain [1, 2] then the blank spaces that immediately appear after the ]
        # character need to removed, because the list size grew. If it is not removed, then the | character will be
        # overly shifted to the right.
        #
        #                       _____________                               _____________
        #                      | D: [1, 2]   |                             | D: [1, 2]       |
        #                      |_____________|                             |_____________|
        #                          Correct                                    Incorrect
        #
        # Thus, the add_# variable contains the space that initially exists between the ] character and the | character
        # when there is no data in the D list. If there is data in the D list, then we take the length of the data from
        # the D list (called sub_#) and subtract that amount from the add_# so that the | character appears correctly.
        #
        # The above example is correctly process by using the following Python code.
        #   add_1 = 7
        #   sub_1 = len(str(D))
        #   c1_r1 = " _____________ \n"
        #   c1_r2 = "| D: " + str(D) + self.space(add_1, sub_1) + "|\n"
        #   c1_r3 = "|_____________|\n"

        # Truck 1 Leading Space Strings - This determines how much space appears before truck characters are displayed.
        c1_r1 = self.space(19)
        c1_r2 = self.space(13)
        c1_r3 = self.space(12)
        c1_r4 = self.space(7)
        c1_r5 = self.space(7)
        c1_r6 = self.space(2)
        c1_r7 = self.space(2)
        c1_r8 = self.space(1)
        c1_r9 = self.space(3)
        c1_r10 = self.space(4, 0, "-")

        # Truck 1 String Construction - Constructs each row of the truck string and includes valuable truck information.
        # Slicers are used for the truck location string as some unique_count are too long to fit properly in the truck.
        truck = self.truck_1
        c2_r1 = "__________________________________________________________________________________"
        c2_r2 = "/    | Package IDs: " + str(truck.package_ids) + self.space(add_1, sub_1) + "|"
        c2_r3 = "/---, | Address Route Index: " + str(truck.locations) + self.space(add_2, sub_2) + "|"
        c2_r4 = "-----# ==| | Route Weight: " + str(truck.distances) + " = " + str(round(truck.weight, 1)) + \
                self.space(add_3, sub_3) + "|"
        c2_r5 = "| :) # ==| | Miles: " + str(round(truck.miles, 1)) + " || Packages: " + str(truck.count) + \
                " || Location: " + str(self.index_addresses[truck.current][:41]) + self.space(add_4, sub_4) + "|"
        c2_r6 = "-----'----#   | |__________________________________________________________________________________|"
        c2_r7 = "|)___()  '#   |______====____   \________________________________________________________|"
        c2_r8 = '[_/,-,\\"--"------ //,-,  ,-,\\\\\\   |/                               //,-,  ,-,  ,-,\\\\ __#'
        c2_r9 = "( 0 )|===******||( 0 )( 0 )||-  o                                '( 0 )( 0 )( 0 )||"
        c2_r10 = "'-'--------------'-'--'-'" + "----------|  TRUCK " + str(self.truck_1.identifier) + " -" + \
                 clock_buffer_1 + str(self.time) + "  |" + clock_buffer_2 + "----'-'--'-'--'-'"

        # Truck 2 Line Buffer Subtraction Amount - Used for subtracting spaces from the Truck 2 Line Buffer.
        sub_5 = len(str(self.truck_2.package_ids))
        sub_6 = len(str(self.truck_2.locations))
        sub_7 = len(str(self.truck_2.distances)) + len(str(round(self.truck_2.weight, 1)))
        sub_8 = len(str(round(self.truck_2.miles, 1))) + len(str(self.truck_2.count)) + \
            len(str(self.index_addresses[self.truck_2.current]))

        # Truck 2 Leading Space Strings - This determines how much space appears before truck characters are displayed.
        c3_r1 = self.space(25)
        c3_r2 = self.space(18)
        c3_r3 = self.space(17)
        c3_r4 = self.space(12)
        c3_r5 = self.space(12)
        c3_r6 = self.space(7)
        c3_r7 = self.space(17)
        c3_r8 = self.space(19)
        c3_r9 = self.space(21)
        c3_r10 = self.space(28, 0, "-")

        # Truck 2 String Construction - Constructs each row of the truck string and includes valuable truck information.
        truck = self.truck_2
        c4_r1 = "__________________________________________________________________________________"
        c4_r2 = "/    | Package IDs: " + str(truck.package_ids) + self.space(add_1, sub_5) + "|"
        c4_r3 = "/---, | Address Route Index: " + str(truck.locations) + self.space(add_2, sub_6) + "|"
        c4_r4 = "-----# ==| | Route Weight: " + str(truck.distances) + " = " + str(round(truck.weight, 1)) + \
                self.space(add_3, sub_7) + "|"
        c4_r5 = "| :) # ==| | Miles: " + str(round(truck.miles, 1)) + " || Packages: " + str(truck.count) + \
                " || Location: " + str(self.index_addresses[truck.current][:41]) + self.space(add_4, sub_8) + "|"
        c4_r6 = "-----'----#   | |__________________________________________________________________________________|"
        c4_r7 = "|)___()  '#   |______====____   \________________________________________________________|"
        c4_r8 = '[_/,-,\\"--"------ //,-,  ,-,\\\\\\   |/                               //,-,  ,-,  ,-,\\\\ __#'
        c4_r9 = "   ( 0 )|===******||( 0 )( 0 )||-  o                                '( 0 )( 0 )( 0 )||"
        c4_r10 = "'-'--------------'-'--'-'" + "----------|  TRUCK " + str(self.truck_2.identifier) + " -" + \
                 clock_buffer_1 + str(self.time) + "  |" + clock_buffer_2 + "----'-'--'-'--'-'----------------------"

        # GUI Leading Space Strings - This determines how much space appears before the row characters are displayed.
        c5_r1 = self.space(5)
        c5_r2 = self.space(4)
        c5_r3 = self.space(4)
        c5_r4 = self.space(4)
        c5_r5 = self.space(4)
        c5_r6 = self.space(4)
        c5_r7 = self.space(14)
        c5_r8 = self.space(17)
        c5_r9 = self.space(20)
        c5_r10 = self.space(1, 0, "-")

        # Display GUI Commands - Appears on the right of the simulation print. Also adds a new line.
        c6_r1 = "[Q] All Events\n"
        c6_r2 = "[E] Next Event\n"
        c6_r3 = "\n"
        c6_r4 = "[W] Packages Table\n"
        c6_r5 = "[A] Address Indexes\n"
        c6_r6 = "[S] Search Package\n"
        c6_r7 = "[D] Search Address\n"
        c6_r8 = "\n"
        c6_r9 = "\n"
        c6_r10 = " "

        # Return the fully constructed string. c is denoted by column number and r is denoted by row number.
        return c1_r1 + c2_r1 + c3_r1 + c4_r1 + c5_r1 + c6_r1 + \
            c1_r2 + c2_r2 + c3_r2 + c4_r2 + c5_r2 + c6_r2 + \
            c1_r3 + c2_r3 + c3_r3 + c4_r3 + c5_r3 + c6_r3 + \
            c1_r4 + c2_r4 + c3_r4 + c4_r4 + c5_r4 + c6_r4 + \
            c1_r5 + c2_r5 + c3_r5 + c4_r5 + c5_r5 + c6_r5 + \
            c1_r6 + c2_r6 + c3_r6 + c4_r6 + c5_r6 + c6_r6 + \
            c1_r7 + c2_r7 + c3_r7 + c4_r7 + c5_r7 + c6_r7 + \
            c1_r8 + c2_r8 + c3_r8 + c4_r8 + c5_r8 + c6_r8 + \
            c1_r9 + c2_r9 + c3_r9 + c4_r9 + c5_r9 + c6_r9 + \
            c1_r10 + c2_r10 + c3_r10 + c4_r10 + c5_r10 + c6_r10

    def space(self, add, sub=0, token=" "):
        """Returns a string of one specific character. Used for ease of formatting for the __str__ function. O(N)."""
        buffer = ""
        for char in range(0, add - sub):
            buffer = buffer + token
        return buffer

    def construct(self):
        """Constructs hash table with keys as ID and data as a list of package information. Updates statuses. O(N)."""
        for package in self.prepper.package_table[:]:
            package_data = []  # Hash table data is stored here for each key.
            for index in [0, 1, 2, 4, 5, 6, 8]:  # Selects specific data columns to store as data in hash table.
                package_data.append(package[index])
            if package[7] == 'Dropped 9:05':  # Bad address packages are unavailable.
                package_data[-1] = "Unavailable - Flight Delayed"
            elif package[7] == 'Bad Address':  # Delayed packages are unavailable.
                package_data[-1] = "Unavailable - Bad Address"
            else:  # All other packages are ready for pickup.
                package_data[-1] = "Ready for Pickup"
            self.hash_table[int(package[0])] = package_data  # Puts package data into hash table. Package ID is the key.

    def execute(self):
        """Runs entire simulation."""
        self.setup()
        while True:
            self.gui()
            self.time.tick_second()  # Increments time 1 second.
            self.special()  # Checks special events.
            for truck in self.trucks:
                self.drive(truck)  # Increments truck 1 second.
                self.load(truck)  # Checks to load truck.
                self.deliver(truck)  # Checks to deliver package.

    def setup(self):
        """Sets time to simulation start time. Append truck objects to list. Print simulation at start time. O(1)."""
        self.time.set_time(SIMULATION_START_TIME)
        self.trucks.append(self.truck_1)
        self.trucks.append(self.truck_2)
        print(self.newline + str(self))

    def special(self):
        """This function contains special events that change the state of the simulation. O(1)."""
        if self.time.compare_time(FLIGHT_DELAY_TIME):  # Packages arrive from airport.
            self.hub.flight_arrival()
        elif self.time.compare_time(BAD_ADDRESS_TIME):  # Packages with bad addresses are fixed.
            self.hub.address_fixed()
        elif not self.hub.warehouse and not self.hub.do_not_ship_packages and \
                not self.truck_1.package_ids and not self.truck_2.package_ids:  # All packages are delivered.
            self.complete()

    def load(self, truck):
        """Attempts to load truck at the HUB; truck must be declared available and must be located in HUB. O(1)."""
        if truck.available and truck.current == 0:  # Checks truck availability and location.
            self.hub.load_truck(truck)

    def drive(self, truck):
        """Drives the truck. Each time this is called, truck drives one second. O(1)."""
        if truck.locations:  # Checks if truck has an address to drive to.
            truck.drive()

    def deliver(self, truck):
        """Delivers a package from the truck if it has arrived at package location. O(1)."""
        if truck.next_distance <= 0 and truck.locations:  # Checks if truck arrived and has an address to drive to.
            truck.deliver_package()  # Deliver package. If it arrives at hub, this step does nothing.
            truck.next_address()  # Checks for next address to drive to. If empty, this step checks if truck is in HUB.
            truck.print_simulation()  # Prints the simulation and waits for another GUI input.

    def gui(self):
        """This is the user interface for interacting with the simulation. Contains commands and function calls. O(1).
        bind to specific keys that the user inputs."""
        while (self.event and not self.end) or self.loop:
            command = input("Input Command: ").upper()  # Accepts user input.
            if command in self.gui_commands:
                if command == 'Q':  # Advances to end of simulation and skips all GUI inputs.
                    self.end = True
                elif command == 'W':  # Prints package hash table.
                    print(self.hash_table)
                elif command == 'E':  # Advances to the next event.
                    self.event = False
                elif command == 'A':  # Prints address index dictionary.
                    self.print_data(self.prepper.address_dictionary)
                elif command == 'S':  # Prints package ID information.
                    self.search_package()
                elif command == 'D':  # Prints address ID information.
                    self.search_address()

    def search_package(self):
        """Function to search a specific package ID. Prints package data from hash table into console. O(1)."""
        while True:  # Keeps accepting inputs until a valid input is found.
            package_id = input('Input Package ID: ').upper()  # User input is submitted here.
            if package_id in self.gui_commands or package_id in \
                    ['STOP', 'EXIT', 'QUIT', 'HELP', 'BACK', 'COMMAND', 'RETURN', 'LEAVE']:  # Breaks input loop.
                break
            try:  # If input throws an error, ensures that program doesn't crash.
                if int(package_id) > 0:  # These are the only slot keys for hash table.
                    print("\t\t\t\t" + str(self.hash_table[int(package_id)]))  # Print package data into console.
            except (ValueError, KeyError, TypeError, IndexError):
                pass

    def search_address(self):
        """Function to search a specific address index. Prints address index, address street/zipcode, and packages
         that share the same deliver destination to console. O(N)."""
        while True:  # Keeps accepting inputs until a valid input is found.
            address_id = input('Input Address ID: ').upper()  # User input is submitted here.
            if address_id in self.gui_commands or address_id in \
                    ['STOP', 'EXIT', 'QUIT', 'HELP', 'BACK', 'COMMAND', 'RETURN', 'LEAVE']:  # Breaks input loop.
                break
            try:  # If input throws an error, ensures that program doesn't crash.
                if 0 <= int(address_id) <= len(self.index_addresses) - 1:  # These are the only valid address indexes.
                    # Print address index and address string.
                    print("\t\t\t\t  " + address_id + " --> " + str(self.index_addresses[int(address_id)]), end='')
                    if int(address_id) == 0:  # HUB does not have any packages delivered to it.
                        print("")
                    else:  # Print packages that are being delivered to this address index.
                        package_list = [x[0] for x in self.packages if x[-1] == int(address_id)]
                        print(" (Package " + str((', '.join(package_list))) + ")")
            except (ValueError, KeyError, TypeError, IndexError):
                pass

    def complete(self):
        """Prints simulation results once all packages are delivered. Accepts GUI inputs until program stops. O(1)."""
        print("%sThe simulation has ended at %s with all packages delivered." % (self.newline, self.time))
        print("The cumulative total miles driven is %0.4s miles.\n\nThis program was written by %s. \n(%s)\n" %
              (self.truck_1.miles + self.truck_2.miles, AUTHOR, LINKEDIN))
        self.loop = True
        while self.loop:  # While loop that permanently checks for user inputs.
            self.gui()

    def print_data(self, data, title=""):
        """This prints all of the data rows in console of a list or dict. Called for data display purposes. O(N)."""
        print("\n" + title)
        if type(data) is list:
            for index, element in enumerate(data):
                print("Index %02d: \t%s" % (index, element))
        elif type(data) is dict:
            for key, value in data.items():
                print("Index %02d: \t%s: %s" % (value, key, value))