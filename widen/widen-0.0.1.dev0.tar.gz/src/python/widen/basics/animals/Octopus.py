class Octopus(object):
    def __init__(self, name, color):
        self.color = color
        self.name = name

    def tell_me_about_the_octopus(self):
        print("This octopus is {} \n {} is the octopus's name.".format(self.color, self.name))
        return "This octopus is {} \n {} is the octopus's name.".format(self.color, self.name)