from settings import *


class Prepper:
    """This class reads data from .csv files and cleans it up for the simulator to work with."""
    def __init__(self):
        """Initializes all variables. O(1)."""
        self.temp = None  # File contents are stored here.
        self.address_dictionary = {}  # Key = Address String; Value = Address Index
        self.distance_matrix = []  # Contains a perfect square matrix of all distance weights.
        self.package_table = []  # Contains nested lists of all package information.

    def execute(self):
        """Below are the two main functions this class executes."""
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
        """Removes all elements that appear before the first line of actual data. O(N)."""
        while self.temp[0] != stop_string:  # Runs while our stop string is not equal to the current data element.
            del self.temp[0]

    def delete_junk_data(self, junk_string):
        """Removes all elements of a specific string type from the list. O(N)."""
        while junk_string in self.temp:  # Runs while string exists in list.
            self.temp.remove(junk_string)

    def clean_matrix_addresses(self):
        """Removes data column A. We only need the street and zipcode. Assigns elements 0 and 1 to be HUB. O(N)."""
        for index in range(len(self.temp) - 3, -1, -3):  # Skips between elements to only select full addresses.
            del self.temp[index]
        self.temp[0] = ' HUB'
        self.temp[1] = ',0.0\n'

    def make_address_dictionary(self):
        """Builds address dictionary by popping short addresses out. Key is the address; value is the index. O(N^2)."""
        address_list = []
        for index in range(len(self.temp) - 2, -1, -2):  # Skips between elements to only select short addresses.
            address_list.insert(0, self.temp.pop(index).strip())  # Pops out address and inserts it to address list.

        for index, address in enumerate(address_list):
            self.address_dictionary[address] = index  # Makes address dictionary.

    def clean_matrix_elements(self):
        """Cleans up the first and last characters of all matrix elements. Ensures data formatted correctly. O(N^2)."""
        for index, element in enumerate(self.temp):
            tokens = list(element)  # Splits an element into a list of token characters.
            del tokens[0]  # First character is junk data.
            while tokens[-1] != '0':  # Last characters are filled with junk data.
                del tokens[-1]
            self.temp[index] = ("".join(tokens))  # Join tokens and reassigns it back to matrix.

    def split_matrix_elements(self):
        """The distance matrix contains a large string of numbers for each row. This splits string into list. O(N^2)."""
        for index, element in enumerate(self.temp):
            self.temp[index] = self.temp[index].split(",")

    def transpose_matrix(self):
        """Create a perfect square matrix. Transposes left triangle of the matrix over right triangle. O(N^2)."""
        # Creates perfect square matrix. This builds the right triangle with fluff data.
        for index, row in enumerate(self.temp):
            while len(row) < len(self.temp[-1]):  # Uses length of last data row to determine square size.
                self.temp[index].append(True)

        # Transposes all data from left triangle over right triangle.
        for x in range(len(self.temp)):
            for y in range(x, len(self.temp[-1])):
                self.temp[x][y] = self.temp[y][x]

    def assign_matrix(self):
        """Converts all elements to floats and properly assigns the completed matrix list. O(N^2)."""
        self.distance_matrix = [[float(element) for element in nested_list] for nested_list in self.temp]

    def clean_table_file(self):
        """Cleans up specific file characters. Splits the single file string into a list of string elements. O(N)."""
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
        """Creates nested lists, one for each package ID, containing all package information. O(N^2)."""
        while self.temp:  # Runs as long as there is data to be processed.
            self.package_table.append([])  # Appends a new row to the table.
            stop_string = str(int(self.temp[0]) + 1)   # The stop string is the next package ID in table.
            for index, element in enumerate(self.temp[:]):
                if element == stop_string and self.temp[1] != stop_string:  # If correct stop string is found, end loop.
                    break
                self.package_table[-1].append(self.temp.pop(0))  # Appends data to new row by popping it out.

    def format_special_notes(self):
        """Append 'Empty' as last data element if no special notes exist. O(N)."""
        for element in self.package_table:
            if len(element) <= 7:  # Packages without any special notes have a length of less than 8.
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
                group_pairs.append(str(element[7][6:]).strip())  # Records package IDs mentioned in special note.
                element[7] = "Group"  # Renames the special note to 'Group'.

        # Identifies all IDs that were mentioned to be grouped in special
        # otes. O(N^2).
        group_ids = []
        for element in group_pairs:
            package_id = ""
            for index, char in enumerate(element):  # Loops through all characters of a group_pair element.
                try:  # If one of the characters is a number, append that character to package_id.
                    package_id = package_id + str(int(char))
                except ValueError:  # If the character is not a number, append the current package ID and restart loop.
                    if package_id != "":
                        group_ids.append(package_id)
                        package_id = ""

        # Adds the special IDs to the group label. O(N).
        for element in self.package_table:
            if element[0] in group_ids:
                element[7] = "Group"  # Renames the special note to 'Group'.

    def format_address_index(self):
        """Appends the address index as last data element. O(N)."""
        for element in self.package_table:
            element.append(self.address_dictionary.get(element[9]))

    def print_data(self, data, title=""):
        """This prints all of the data rows in console of a list or dict. Called for data display purposes. O(N)."""
        print("\n" + title)
        if type(data) is list:
            for index, element in enumerate(data):
                print("Index %02d: \t%s" % (index, element))
        elif type(data) is dict:
            for key, value in data.items():
                print("Index %02d: \t%s: %s" % (value, key, value))
