# -*- coding: utf-8 -*-
"""
    pip_services3_commons.random.RandomText
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    RandomText implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from pip_services3_commons.random import RandomString

import random
from .RandomBoolean import RandomBoolean
from .RandomInteger import RandomInteger

_name_prefixes = ["Dr.", "Mr.", "Mrs"]
_name_suffixes = ["Jr.", "Sr.", "II", "III"]
_first_names = [
    "John", "Bill", "Andrew", "Nick", "Pamela", "Bela", "Sergio", "George", "Hurry", "Cecilia", "Vesta", "Terry",
    "Patrick"
]
_last_names = [
    "Doe", "Smith", "Johns", "Gates", "Carmack", "Zontak", "Clinton", "Adams", "First", "Lopez", "Due", "White", "Black"
]
_colors = [
    "Black", "White", "Red", "Blue", "Green", "Yellow", "Purple", "Grey", "Magenta", "Cian"
]
_stuffs = [
    "Game", "Ball", "Home", "Board", "Car", "Plane", "Hotel", "Wine", "Pants", "Boots", "Table", "Chair"
]
_adjectives = [
    "Large", "Small", "High", "Low", "Certain", "Fuzzy", "Modern", "Faster", "Slower"
]
_verbs = [
    "Run", "Stay", "Breeze", "Fly", "Lay", "Write", "Draw", "Scream"
]
_street_types = [
    "Lane", "Court", "Circle", "Drive", "Way", "Loop", "Blvd", "Street"
]
_street_prefix = [
    "North", "South", "East", "West", "Old", "New", "N.", "S.", "E.", "W."
]
_street_names = [
    "1st", "2nd", "3rd", "4th", "53rd", "6th", "8th", "Acacia", "Academy", "Adams", "Addison", "Airport", "Albany",
    "Alderwood", "Alton", "Amerige", "Amherst", "Anderson",
    "Ann", "Annadale", "Applegate", "Arcadia", "Arch", "Argyle", "Arlington", "Armstrong", "Arnold", "Arrowhead",
    "Aspen", "Augusta", "Baker", "Bald Hill", "Bank", "Bay Meadows",
    "Bay", "Bayberry", "Bayport", "Beach", "Beaver Ridge", "Bedford", "Beech", "Beechwood", "Belmont", "Berkshire",
    "Big Rock Cove", "Birch Hill", "Birchpond", "Birchwood",
    "Bishop", "Blackburn", "Blue Spring", "Bohemia", "Border", "Boston", "Bow Ridge", "Bowman", "Bradford",
    "Brandywine", "Brewery", "Briarwood", "Brickell", "Brickyard",
    "Bridge", "Bridgeton", "Bridle", "Broad", "Brookside", "Brown", "Buckingham", "Buttonwood", "Cambridge", "Campfire",
    "Canal", "Canterbury", "Cardinal", "Carpenter",
    "Carriage", "Carson", "Catherine", "Cedar Swamp", "Cedar", "Cedarwood", "Cemetery", "Center", "Central", "Chapel",
    "Charles", "Cherry Hill", "Chestnut", "Church", "Circle",
    "Clark", "Clay", "Cleveland", "Clinton", "Cobblestone", "Coffee", "College", "Colonial", "Columbia", "Cooper",
    "Corona", "Cottage", "Country Club", "Country", "County", "Court",
    "Courtland", "Creek", "Creekside", "Crescent", "Cross", "Cypress", "Deerfield", "Del Monte", "Delaware", "Depot",
    "Devon", "Devonshire", "Division", "Dogwood", "Dunbar",
    "Durham", "Eagle", "East", "Edgefield", "Edgemont", "Edgewater", "Edgewood", "El Dorado", "Elizabeth", "Elm",
    "Essex", "Euclid", "Evergreen", "Fairfield", "Fairground", "Fairview",
    "Fairway", "Fawn", "Fifth", "Fordham", "Forest", "Foster", "Foxrun", "Franklin", "Fremont", "Front", "Fulton",
    "Galvin", "Garden", "Gartner", "Gates", "George", "Glen Creek",
    "Glen Eagles", "Glen Ridge", "Glendale", "Glenlake", "Glenridge", "Glenwood", "Golden Star", "Goldfield", "Golf",
    "Gonzales", "Grand", "Grandrose", "Grant", "Green Hill",
    "Green Lake", "Green", "Greenrose", "Greenview", "Gregory", "Griffin", "Grove", "Halifax", "Hamilton", "Hanover",
    "Harrison", "Hartford", "Harvard", "Harvey", "Hawthorne",
    "Heather", "Henry Smith", "Heritage", "High Noon", "High Point", "High", "Highland", "Hill Field", "Hillcrest",
    "Hilldale", "Hillside", "Hilltop", "Holly", "Homestead",
    "Homewood", "Honey Creek", "Howard", "Indian Spring", "Indian Summer", "Iroquois", "Jackson", "James", "Jefferson",
    "Jennings", "Jockey Hollow", "John", "Johnson", "Jones",
    "Joy Ridge", "King", "Kingston", "Kirkland", "La Sierra", "Lafayette", "Lake Forest", "Lake", "Lakeshore",
    "Lakeview", "Lancaster", "Lane", "Laurel", "Leatherwood", "Lees Creek",
    "Leeton Ridge", "Lexington", "Liberty", "Lilac", "Lincoln", "Linda", "Littleton", "Livingston", "Locust",
    "Longbranch", "Lookout", "Lower River", "Lyme", "Madison", "Maiden",
    "Main", "Mammoth", "Manchester", "Manhattan", "Manor Station", "Maple", "Marconi", "Market", "Marsh", "Marshall",
    "Marvon", "Mayfair", "Mayfield", "Mayflower", "Meadow",
    "Meadowbrook", "Mechanic", "Middle River", "Miles", "Mill Pond", "Miller", "Monroe", "Morris", "Mountainview",
    "Mulberry", "Myrtle", "Newbridge", "Newcastle", "Newport",
    "Nichols", "Nicolls", "North", "Nut Swamp", "Oak Meadow", "Oak Valley", "Oak", "Oakland", "Oakwood", "Ocean",
    "Ohio", "Oklahoma", "Olive", "Orange", "Orchard", "Overlook",
    "Pacific", "Paris Hill", "Park", "Parker", "Pawnee", "Peachtree", "Pearl", "Peg Shop", "Pendergast", "Peninsula",
    "Penn", "Pennington", "Pennsylvania", "Pheasant", "Philmont",
    "Pierce", "Pin Oak", "Pine", "Pineknoll", "Piper", "Plumb Branch", "Poor House", "Prairie", "Primrose", "Prince",
    "Princess", "Princeton", "Proctor", "Prospect", "Pulaski",
    "Pumpkin Hill", "Purple Finch", "Queen", "Race", "Ramblewood", "Redwood", "Ridge", "Ridgewood", "River",
    "Riverside", "Riverview", "Roberts", "Rock Creek", "Rock Maple",
    "Rockaway", "Rockcrest", "Rockland", "Rockledge", "Rockville", "Rockwell", "Rocky River", "Roosevelt", "Rose",
    "Rosewood", "Ryan", "Saddle", "Sage", "San Carlos", "San Juan",
    "San Pablo", "Santa Clara", "Saxon", "School", "Schoolhouse", "Second", "Shadow Brook", "Shady", "Sheffield",
    "Sherman", "Sherwood", "Shipley", "Shub Farm", "Sierra",
    "Silver Spear", "Sleepy Hollow", "Smith Store", "Smoky Hollow", "Snake Hill", "Southampton", "Spring", "Spruce",
    "Squaw Creek", "St Louis", "St Margarets", "St Paul", "State",
    "Stillwater", "Strawberry", "Studebaker", "Sugar", "Sulphur Springs", "Summerhouse", "Summit", "Sunbeam",
    "Sunnyslope", "Sunset", "Surrey", "Sutor", "Swanson", "Sycamore",
    "Tailwater", "Talbot", "Tallwood", "Tanglewood", "Tarkiln Hill", "Taylor", "Thatcher", "Third", "Thomas",
    "Thompson", "Thorne", "Tower", "Trenton", "Trusel", "Tunnel",
    "University", "Vale", "Valley Farms", "Valley View", "Valley", "Van Dyke", "Vermont", "Vernon", "Victoria", "Vine",
    "Virginia", "Wagon", "Wall", "Walnutwood", "Warren",
    "Washington", "Water", "Wayne", "Westminster", "Westport", "White", "Whitemarsh", "Wild Rose", "William",
    "Williams", "Wilson", "Winchester", "Windfall", "Winding Way",
    "Winding", "Windsor", "Wintergreen", "Wood", "Woodland", "Woodside", "Woodsman", "Wrangler", "York",
]

_all_words = _first_names + _last_names + _colors + _stuffs + _adjectives + _verbs


class RandomText:
    """
    Random generator for various text values like names, addresses or phone numbers.

    Example:

    .. code-block:: python

        value1 = RandomText.name()      # Possible result: "Sergio"
        value2 = RandomText.verb()      # Possible result: "Run"
        value3 = RandomText.text(50)    # Possible result: "Run jorge. Red high scream?"
    """

    @staticmethod
    def color() -> str:
        """
        Generates a random color name. The result args is capitalized.

        :return: a random color name.
        """
        return random.choice(_colors)

    @staticmethod
    def stuff() -> str:
        """
        Generates a random noun. The result args is capitalized.

        :return: a random noun.
        """
        return random.choice(_stuffs)

    @staticmethod
    def noun() -> str:
        """
        Generates a random noun.
        The result value is capitalized.

        :return: a random noun
        """
        return RandomString.pick(_stuffs)

    @staticmethod
    def adjective() -> str:
        """
        Generates a random adjective. The result args is capitalized.

        :return: a random adjective.
        """
        return random.choice(_adjectives)

    @staticmethod
    def verb() -> str:
        """
        Generates a random verb. The result args is capitalized.

        :return: a random verb.
        """
        return random.choice(_verbs)

    @staticmethod
    def phrase(min_size: int, max_size: int = None) -> str:
        """
        Generates a random phrase which consists of few words separated by spaces.
        The first word is capitalized, others are not.

        :param min_size: (optional) minimum string length.

        :param max_size: maximum string length.

        :return: a random phrase.
        """
        max_size = max_size if max_size != None else min_size
        size = RandomInteger.next_integer(min_size, max_size)
        if size <= 0:
            return ""

        result = ""
        result += random.choice(_all_words)
        while len(result) < size:
            result += " " + random.choice(_all_words).lower()

        return result

    @staticmethod
    def name() -> str:
        """
        Generates a random person's name which has the following structure
        <optional prefix> <first name> <second name> <optional suffix>

        :return: a random name.
        """
        result = ""

        if RandomBoolean.chance(3, 5):
            result += random.choice(_name_prefixes) + " "

        result += random.choice(_first_names) + " " + random.choice(_last_names)

        if RandomBoolean.chance(5, 10):
            result += " " + random.choice(_name_suffixes)

        return result

    @staticmethod
    def full_name() -> str:
        """
        Generates a random person's name which has the following structure
        <optional prefix> <first name> <second name> <optional suffix>

        :return: a random name.
        """
        result = ''

        if RandomBoolean.chance(3, 5):
            result += RandomString.pick(_name_prefixes) + " "

        result += RandomString.pick(_first_names) + " " + RandomString.pick(_last_names)

        if RandomBoolean.chance(5, 10):
            result += " " + RandomString.pick(_name_suffixes)

        return result

    @staticmethod
    def word() -> str:
        """
        Generates a random word from available first names, last names, colors, stuffs, adjectives, or verbs.

        :return: a random word.
        """
        return random.choice(_all_words)

    @staticmethod
    def words(min_size: int, max_size: int = None) -> str:
        """
        Generates a random text that consists of random number of random words separated by spaces.

        :param min_size: (optional) a minimum number of words.

        :param max_size: a maximum number of words.

        :return: a random text.
        """
        max_size = max_size if max_size is not None else min_size
        result = ""

        count = RandomInteger.next_integer(min_size, max_size)
        for i in range(count):
            result += random.choice(_all_words)

        return result

    @staticmethod
    def phone() -> str:
        """
        Generates a random phone number. The phone number has the format: (XXX) XXX-YYYY

        :return: a random phone number.
        """
        result = ""
        result += "(" + str(RandomInteger.next_integer(111, 999)) + ") "
        result += str(RandomInteger.next_integer(111, 999))
        result += "-" + str(RandomInteger.next_integer(0, 9999))
        return result

    @staticmethod
    def email() -> str:
        """
        Generates a random email address.

        :return: a random email address.
        """
        return RandomText.words(2, 6) + "@" + RandomText.words(1, 3) + ".com"

    @staticmethod
    def text(min_size: int, max_size: int = None) -> str:
        """
        Generates a random text, consisting of first names, last names, colors, stuffs, adjectives, verbs,
        and punctuation marks.

        :param min_size: minimum amount of words to generate. Text will contain 'minSize' words if 'maxSize' is omitted.

        :param max_size: (optional) maximum amount of words to generate.

        :return: a random text.
        """
        max_size = max_size if max_size is not None else min_size
        size = RandomInteger.next_integer(min_size, max_size)

        result = ""
        result += random.choice(_all_words)

        while len(result) < size:
            next = random.choice(_all_words)
            if RandomBoolean.chance(4, 6):
                next = " " + next.lower()
            elif RandomBoolean.chance(2, 5):
                next = random.choice(":,-") + next.lower()
            elif RandomBoolean.chance(3, 5):
                next = random.choice(":,-") + " " + next.lower()
            else:
                next = random.choice(".!?") + " " + next

            result += next

        return result
