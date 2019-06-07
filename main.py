# Made by Ryan Kruse.
from objects import Truck, HashTable, Clock, Hub
from settings import *


class Simulation:
    """This is the simulation class that executes function calls each tick."""
    def __init__(self, prep):
        """Initialize simulation variables."""
        self.prepper = prep  # Reference to prepper.
        self.index_addresses = {v: k for k, v in prep.address_dictionary.items()}  # Dictionary of addresses.
        self.distances = prep.distance_matrix  # Distance matrix table.
        self.packages = prep.package_table  # Package table.
        self.hash_table = HashTable(len(self.packages) + 1)  # Package hash table.
        self.construct()  # Constructs hash table.
        self.time = Clock(0, 0, 0)  # Constructs clock object.
        self.hub = Hub(self, self.packages)  # Constructs Hub object.
        self.truck_1 = Truck(self, 1, True, True, 41)  # Constructs truck 1 object.
        self.truck_2 = Truck(self, 2, False, False, 149)  # Constructs truck 2 object.
        self.trucks = []  # All trucks.
        self.newline = "\n\n\n\n\n\n"  # Buffer space for printing text.
        self.gui_commands = ['Q', 'W', 'E', 'A', 'S', 'D']  # All GUI Commands.
        self.end = False  # GUI check if executing all code.
        self.event = True  # GUI check if event occurred.
        self.loop = False  # GUI check if simulation complete.

    def __str__(self):
        """This prints valuable information about the state of the entire simulation. For simplicity sake, the
        simulation string is split up into rows and columns of data, denoted by the c#_r# variables. Going down the
        function, first column 1 is built, then column 2, up until column 6, where all columns and rows are combined
        then returned. Below is information about each column:

            Column 1) Adds blank spaces before the first truck string appears.
            Column 2) Contains the core construction text of the first truck string.
            Column 3) Adds blank spaces before the second truck string appears.
            Column 4) Contains the core construction text of the second truck string.
            Column 5) Adds blank spaces before the GUI Command string appears.
            Column 6) Contains information about all possible GUI commands that exist.

        The skeleton text for the truck is cited here: http://www.ascii-art.de/ascii/t/truck.txt. O(1)."""

        # Adjust clock buffer space.
        clock_buffer_2 = "-"
        if self.time.hour >= 10:
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
        # If the list of D were to suddenly contain [1, 2] then the blank spaces that immediately to the right of the ]
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
        # Slicers are used for the truck location string as some addresses are too long to fit properly in the truck.
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
                 str(self.time) + "  |" + clock_buffer_2 + "----'-'--'-'--'-'"

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
                 str(self.time) + "  |" + clock_buffer_2 + "----'-'--'-'--'-'----------------------"

        # GUI Leading Space Strings - This determines how much space appears before the GUI commands are displayed.
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

        # Display GUI Commands - Appears on the right-most side of the simulation print. Adds a new line.
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

        # Return the fully constructed joined string. c is denoted by column number and r is denoted by row number.
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
        """Returns a string of one specific character. O(N)."""
        buffer = ""
        for char in range(0, add - sub):
            buffer = buffer + token
        return buffer

    def construct(self):
        """Constructs hash table with keys as ID and data as package information. Updates statuses. O(N)."""
        for package in self.prepper.package_table[:]:
            package_data = []
            # Select data elements to store into hash table data.
            for index in [0, 1, 2, 4, 5, 6, 8]:
                package_data.append(package[index])
            # Update package status.
            if package[7] == 'Dropped 9:05':
                package_data[-1] = "Unavailable - Flight Delayed"
            elif package[7] == 'Bad Address':
                package_data[-1] = "Unavailable - Bad Address"
            else:
                package_data[-1] = "Ready for Pickup"
            # Put data into hash table. Package ID is key.
            self.hash_table[int(package[0])] = package_data

    def execute(self):
        """Runs entire simulation."""
        self.setup()
        while True:
            self.gui()
            self.time.tick_second()
            self.special()
            for truck in self.trucks:
                self.drive(truck)
                self.load(truck)
                self.deliver(truck)

    def setup(self):
        """Set simulation time. Create truck list. Print simulation. O(N)."""
        self.time.set_time(SIMULATION_START_TIME)
        self.trucks.append(self.truck_1)
        self.trucks.append(self.truck_2)
        print(self.newline + str(self))

    def special(self):
        """Check for special events that impact the simulation. O(N^2)."""
        # Packages arrive from airport.
        if self.time.compare_time(FLIGHT_DELAY_TIME):
            self.hub.flight_arrival()
        # Packages with bad addresses are fixed.
        elif self.time.compare_time(BAD_ADDRESS_TIME):
            self.hub.address_fixed()
        # All packages are confirmed delivered.
        elif not self.hub.warehouse and not self.hub.do_not_ship_packages and \
                not self.truck_1.package_ids and not self.truck_2.package_ids:
            self.complete()

    def load(self, truck):
        """Load truck in Hub if truck is available and located in Hub. O(M * N!)."""
        if truck.available and truck.current == 0:
            self.hub.load_truck(truck)

    def drive(self, truck):
        """Drive the truck one second. O(1)."""
        if truck.locations:
            truck.drive()

    def deliver(self, truck):
        """Deliver packages from truck if truck arrives at package location. O(N^2)."""
        if truck.next_distance <= 0 and truck.locations:
            truck.deliver_package()  # Deliver package. If truck arrives at hub, this step is ignored.
            truck.next_address()  # Check for next address to drive to. If none, checks if truck in HUB.
            truck.print_simulation()  # Print simulation and wait for GUI command.

    def gui(self):
        """User interface for interacting with the simulation. Contains binded key function calls. O(N)."""
        while (self.event and not self.end) or self.loop:
            # Accepts a user input.
            command = input("Input Command: ").upper()
            if command in self.gui_commands:
                # Advances to end of simulation and ignores all GUI inputs.
                if command == 'Q':
                    self.end = True
                # Prints package hash table.
                elif command == 'W':
                    print(self.hash_table)
                # Advances to the next event.
                elif command == 'E':
                    self.event = False
                # Prints address ID table.
                elif command == 'A':
                    self.print_data(self.prepper.address_dictionary)
                # Prints package ID information.
                elif command == 'S':
                    self.search_package()
                # Prints address ID information.
                elif command == 'D':
                    self.search_address()

    def search_package(self):
        """Search specific package ID from hash table and then prints package data. O(1)."""
        while True:
            # Accepts a user input.
            package_id = input('Input Package ID: ').upper()
            # Breaks user input loop upon key-phrase.
            if package_id in self.gui_commands or package_id in \
                    ['STOP', 'EXIT', 'QUIT', 'HELP', 'BACK', 'COMMAND', 'RETURN', 'LEAVE']:
                break
            try:
                if int(package_id) > 0:
                    # Print package data.
                    print("\t\t\t\t" + str(self.hash_table[int(package_id)]))
            except (ValueError, KeyError, TypeError, IndexError):
                pass

    def search_address(self):
        """Search specific address ID from address dictionary and then prints address data. O(N)."""
        while True:
            # Accepts a user input.
            address_id = input('Input Address ID: ').upper()
            # Breaks user input loop upon key-phrase.
            if address_id in self.gui_commands or address_id in \
                    ['STOP', 'EXIT', 'QUIT', 'HELP', 'BACK', 'COMMAND', 'RETURN', 'LEAVE']:
                break
            try:
                if 0 <= int(address_id) <= len(self.index_addresses) - 1:
                    # Print address ID and address name.
                    print("\t\t\t\t  " + address_id + " --> " + str(self.index_addresses[int(address_id)]), end='')
                    # Print package IDs that are being delivered to address ID.
                    if int(address_id) == 0:
                        print("")
                    else:
                        package_list = [x[0] for x in self.packages if x[-1] == int(address_id)]
                        print(" (Package " + str((', '.join(package_list))) + ")")
            except (ValueError, KeyError, TypeError, IndexError):
                pass

    def complete(self):
        """Prints simulation results once all packages are delivered. Accepts GUI inputs until terminated. O(1)."""
        print("%sThe simulation has ended at%s with all packages delivered." % (self.newline, self.time))
        print("The cumulative total miles driven is %0.4s miles.\n\nThis program was written by %s. \n(%s)\n" %
              (self.truck_1.miles + self.truck_2.miles, AUTHOR, GITHUB))
        # Permanently loop GUI inputs.
        self.loop = True
        while self.loop:
            self.gui()

    def print_data(self, data, title=""):
        """Prints all of the data rows in console of a list or dict. Called for data display purposes. O(N)."""
        print("\n" + title)
        if type(data) is list:
            for index, element in enumerate(data):
                print("Index %02d: \t%s" % (index, element))
        elif type(data) is dict:
            for key, value in data.items():
                print("Index %02d: \t%s: %s" % (value, key, value))


class Prepper:
    """This is the prepper class that reads data from .csv files and cleans it up for the simulation."""
    def __init__(self):
        """Initializes all variables."""
        self.temp = None  # File contents.
        self.address_dictionary = {}  # Key = Address String; Value = Address Index.
        self.distance_matrix = []  # Perfect square matrix of distances.
        self.package_table = []  # Nested lists of package data.

    def execute(self):
        """Main functions executed."""
        self.make_distance_matrix()
        self.make_package_table()

        # Formatting complete. Uncomment the below statements to view data in console.
        # self.print_data(self.package_table, 'Package Table')  # Print Package Table.
        # self.print_data(self.address_dictionary, 'Address Dictionary')  # Print Address Dictionary.
        # self.print_data(self.distance_matrix, 'Distance Matrix')  # Print Distance Matrix.

    def make_distance_matrix(self):
        """Import the distance.csv file and build the address dictionary and distance matrix variables."""
        self.open_file(DISTANCE_FILE)
        self.clean_matrix_file()
        self.delete_lead_data("\n")
        self.delete_junk_data(",")
        self.clean_matrix_addresses()
        self.make_address_dictionary()
        self.clean_matrix_elements()
        self.split_matrix_elements()
        self.transpose_matrix()
        self.assign_matrix()

    def make_package_table(self):
        """Import the packages.csv file and build the package table variable."""
        self.open_file(PACKAGE_FILE)
        self.clean_table_file()
        self.delete_lead_data("1")
        self.delete_junk_data("")
        self.nest_table_elements()
        self.format_special_notes()
        self.format_package_status()
        self.format_short_address()
        self.format_grouped_packages()
        self.format_address_index()

    def open_file(self, file_name):
        """Opens a .csv file and assigns the file contents to self.temp. O(1)."""
        with open(file_name) as file_python:
            self.temp = file_python.read()

    def clean_matrix_file(self):
        """Cleans up specific file characters. Splits the single file string into a list of string elements. O(N)."""
        self.temp = self.temp.replace(",,", "")
        self.temp = self.temp.replace("\n(", "; ")
        self.temp = self.temp.replace(")", "")
        self.temp = list(self.temp.split('"'))

    def delete_lead_data(self, stop_string):
        """Removes all elements that appear before the first line of actual data. O(N^2)."""
        while self.temp[0] != stop_string:
            del self.temp[0]

    def delete_junk_data(self, junk_string):
        """Removes all elements of a specific string type from the list. O(N^2)."""
        while junk_string in self.temp:
            self.temp.remove(junk_string)

    def clean_matrix_addresses(self):
        """Removes data column A. Address only needs street and zipcode. Assigns indexes 0 and 1 to be HUB. O(N^2)."""
        for index in range(len(self.temp) - 3, -1, -3):
            del self.temp[index]
        self.temp[0] = ' HUB'
        self.temp[1] = ',0.0\n'

    def make_address_dictionary(self):
        """Builds address dictionary by popping addresses out. Key is the address; value is the index. O(N^2)."""
        address_list = []
        for index in range(len(self.temp) - 2, -1, -2):
            address_list.insert(0, self.temp.pop(index).strip())
        # Build address dictionary.
        for index, address in enumerate(address_list):
            self.address_dictionary[address] = index

    def clean_matrix_elements(self):
        """Cleans up the first and last characters of matrix elements. Ensures data is formatted correctly. O(N^2)."""
        for index, element in enumerate(self.temp):
            tokens = list(element)
            del tokens[0]
            while tokens[-1] != '0':
                del tokens[-1]
            # Join characters and reassigns element back to matrix.
            self.temp[index] = ("".join(tokens))

    def split_matrix_elements(self):
        """Split matrix strings into lists. O(N^2)."""
        for index, element in enumerate(self.temp):
            self.temp[index] = self.temp[index].split(",")

    def transpose_matrix(self):
        """Create a perfect square matrix. Transposes left triangle of the matrix over right triangle. O(N^2)."""
        # Creates perfect square matrix by building a right triangle with fluff data.
        for index, row in enumerate(self.temp):
            while len(row) < len(self.temp[-1]):
                self.temp[index].append(True)
        # Transposes all data from left triangle over right triangle.
        for x in range(len(self.temp)):
            for y in range(x, len(self.temp[-1])):
                self.temp[x][y] = self.temp[y][x]

    def assign_matrix(self):
        """Converts all elements to floats and properly assigns the completed matrix list. O(N^2)."""
        self.distance_matrix = [[float(element) for element in nested_list] for nested_list in self.temp]

    def clean_table_file(self):
        """Cleans up specific file characters. Splits the file string into a list of string elements. O(N)."""
        self.temp = self.temp.replace(",,", "")
        self.temp = self.temp.replace(", ", " & ")
        self.temp = self.temp.replace("\n", ",")
        self.temp = self.temp.replace("5383 South", "5383 S")
        self.temp = self.temp.replace("Delayed on flight---will not arrive to depot until 9:05 am", "Dropped 9:05")
        self.temp = self.temp.replace("Must be delivered with", "Group")
        self.temp = self.temp.replace("Can only be on truck", "Truck")
        self.temp = self.temp.replace("Wrong address listed", "Bad Address")
        self.temp = list(self.temp.split(","))

    def nest_table_elements(self):
        """Creates nested lists, one for each package ID, containing all package data. O(N^3)."""
        while self.temp:
            self.package_table.append([])
            # Identify next package ID in table as stop string.
            stop_string = str(int(self.temp[0]) + 1)
            for index, element in enumerate(self.temp[:]):
                # Append data to new row until stop string is found.
                if element == stop_string and self.temp[1] != stop_string:
                    break
                self.package_table[-1].append(self.temp.pop(0))

    def format_special_notes(self):
        """Append 'Empty' as last data element if no special notes exist. O(N)."""
        for element in self.package_table:
            if len(element) <= 7:
                element.append("Empty")

    def format_package_status(self):
        """Append package status as last data element. This is adjusted later when building the hash table. O(N)."""
        for element in self.package_table:
            element.append("Status")

    def format_short_address(self):
        """Append a shortened address as last data element. Only street and zipcode information are included. O(N)."""
        for element in self.package_table:
            element.append(element[1] + "; " + element[4])

    def format_grouped_packages(self):
        """Groups all packages that has 'Group' in special notes or is mentioned in the group special notes. O(N^2)."""
        # Identifies all packages that have 'Group' in special notes. O(N * K)
        group_pairs = []
        for element in self.package_table:
            if element[7][0:6] == '"Group':
                # Records package IDs mentioned in special note.
                group_pairs.append(str(element[7][6:]).strip())
                element[7] = "Group"

        # Identifies all package IDs that were mentioned to be grouped in special notes. O(N^2).
        group_ids = []
        for element in group_pairs:
            package_id = ""
            # Loops through all characters of group_pair element.
            for index, char in enumerate(element):
                try:
                    # If character is a number, append that character to package_id.
                    package_id = package_id + str(int(char))
                except ValueError:
                    # If character is not a number, append package_id and restart loop.
                    if package_id != "":
                        group_ids.append(package_id)
                        package_id = ""

        # Adds the package IDs to the group label. O(N).
        for element in self.package_table:
            if element[0] in group_ids:
                element[7] = "Group"

    def format_address_index(self):
        """Appends the address index as last data element. O(N)."""
        for element in self.package_table:
            element.append(self.address_dictionary.get(element[9]))

    def print_data(self, data, title=""):
        """Prints all of the data rows in console of a list or dict. Called for data display purposes. O(N)."""
        print("\n" + title)
        if type(data) is list:
            for index, element in enumerate(data):
                print("Index %02d: \t%s" % (index, element))
        elif type(data) is dict:
            for key, value in data.items():
                print("Index %02d: \t%s: %s" % (value, key, value))


prepper = Prepper()
prepper.execute()
simulation = Simulation(prepper)
simulation.execute()
