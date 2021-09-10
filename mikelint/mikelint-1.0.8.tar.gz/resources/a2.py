"""
End of Dayz
Assignment 2
Semester 1, 2021
CSSE1001/CSSE7030

A text-based zombie survival game wherein the player has to reach
the hospital whilst evading zombies.
"""

from typing import Tuple, Optional, Dict, List

from a2_support import *

# Replace these <strings> with your name, student number and email address.
__author__ = "<Meghana Nair>, <45853382>"
__email__ = "<m.nair@uqconnect.edu.au>"


# Implement your classes here.

class Entity(object): 
    def step(self, position, game):
        pass  


    def display(self):
        raise NotImplementedError
    

    def __repr__(self):
        return self.__class__.__name__ + "()"


class Player(Entity):
    def display(self):
        return PLAYER
    

class Hospital(Entity):
    def display(self): 
        return HOSPITAL
    

class VulnerablePlayer(Player):
    def __init__(self):
        self._infect = False


    def infect(self):
        self._infect = True


    def is_infected(self):
        return self._infect


class HoldingPlayer(VulnerablePlayer):
    def get_inventory(self):
        pass


    def infect(self):
        pass


    def step(self, position, game):
        pass


class Zombie(Entity):
    def display(self):
        return ZOMBIE


    def step(self, position, game):
        possible_moves = random_directions()
        positions_with_entities = game.get_grid().get_mapping().keys() 

        for move in possible_moves:
            offset_position = Position(move[0], move[1])
            new_position = position.add(offset_position)
            
            entity_at_position = game.get_grid().get_entity(new_position)
            if entity_at_position == None:
                pass
            else:
                if entity_at_position.display() == PLAYER:
                    entity_at_position.infect()
                    break
            if game.get_grid().in_bounds(new_position) == True and new_position not in positions_with_entities:
                game.get_grid().move_entity(position, new_position)
                break


class TrackingZombie(Zombie):
    def step(self, position, game):
        player_position = game.get_grid().find_player()

        directions = ['S', 'N', 'E', 'W']
        correct_directions = ['W', 'S', 'N', 'E']

        empty_list = []

        i = 0
        for i in OFFSETS:
            offset_position = Position(i[0], i[1])
            new_position = position.add(offset_position)
            distance_to_player = new_position.distance(player_position)

            empty_list.append((directions[i], distance_to_player, offset_position))
            i += 1

        prioritised_list = empty_list.sort(key=lambda tup: (tup[1], correct_directions.index(tup[0])))

        for i[2] in prioritised_list:
            new_position = position.add(i[2])

            entity_at_position = game.get_grid().get_entity(new_position)
            
            if entity_at_position == None:
                pass
            else:
                if entity_at_position.display() == PLAYER:
                    entity_at_position.infect()
                    break
            if game.get_grid().in_bounds(new_position) == True and new_position not in positions_with_entities:
                game.get_grid().move_entity(position, new_position)
                break            

    
    def display(self):
        return TRACKING_ZOMBIE
        

class Pickup(Entity):
    def __init__(self):
        self._durability = 0
        self._lifetime = self._durability


    def get_durability(self):
        raise NotImplementedError


    def get_lifetime(self):
        return self._lifetime


    def hold(self):
        self._lifetime -= 1


    def __repr__(self):
        return f"Pickup({self._lifetime})"
    

class Garlic(Pickup):
    def __init__(self):
        self._durability = 10
        self._lifetime = self._durability

        
    def get_durability(self):
        return self._durability 


    def display(self):
        return GARLIC


class Crossbow(Pickup):
    def __init__(self):
        self._durability = 5
        self._lifetime = self._durability

        
    def get_durability(self):
        return self._durability


    def display(self):
        return CROSSBOW
    

class Grid(object):
    def __init__(self, size: int):
        self._size = size
        self._entity= {}
        self._serialized_entity_dictionary = {}
        

    def get_size(self):
        return self._size
    

    def in_bounds(self, position):
        if position.get_x() >= 0 and position.get_y() >= 0 and position.get_x() < self._size and position.get_y() < self._size:
            return True
        else:
            return False
        

    def add_entity(self, position, entity):
        if self.in_bounds(position) == False:
            return None
        else:
            self._entity.update({position : entity})

        
    def remove_entity(self, position):
        self._entity.pop(position)


    def get_entity(self, position):
        if self.in_bounds(position) == False:
            return None
        elif self._entity.get(position) == None:
            return None
        else:
            return self._entity[position]
    

    def get_mapping(self):
        copy_entity_dict = self._entity.copy()
        return copy_entity_dict
    

    def get_entities(self):
        entities = []
        for k in self._entity:
            entities.append(self._entity[k])
        return entities
    

    def move_entity(self, start: Position, end: Position):
        if self.in_bounds(start) == False or self.in_bounds(end) == False:
            return None
        elif self._entity.get(start) == None:
            return None
        else:
            self._entity[end] = self._entity[start]
            self._entity.pop(start)
            

    def find_player(self):

        for key in self._entity.keys():
            if self._entity[key].display() == 'P':
                return key
        return key
    

    def serialize(self):
        for position, entity in self._entity.items():
            entity = entity.display()
            position = (position._x, position._y)

            self._serialized_entity_dictionary[position] = entity
        
        return self._serialized_entity_dictionary

            
class MapLoader(object):

    def create_entity(self, token: str):
        raise NotImplementedError

    
    def load(self, filename): 
        loaded_map = load_map(filename)
        grid_size = loaded_map[1]
        new_game_grid = Grid(grid_size)
        
        for key, value in loaded_map[0].items():
            new_position = Position(key[0], key[1]) 

            new_game_grid.add_entity(new_position, self.create_entity(value))

        return new_game_grid
    
   
class BasicMapLoader(MapLoader):
    def create_entity(self, token: str):
        if token == PLAYER:
            return Player()
        elif token == HOSPITAL:
            return Hospital()
        else:
            raise ValueError


class IntermediateMapLoader(BasicMapLoader):
    def create_entity(self, token: str):
        if token == ZOMBIE:
            return Zombie()
        elif token == PLAYER:
            return VulnerablePlayer()
        return super().create_entity(token)


class AdvancedMapLoader(IntermediateMapLoader):
    def create_entity(self, token: str):
        if token == TRACKING_ZOMBIE:
            return TrackingZombie()
        elif token == GARLIC:
            return Garlic()
        elif token == CROSSBOW:
            return Crossbow()
        elif token == PLAYER:
            return HoldingPlayer()
        return super().create_entity(token) 
  

class Game(object):
    def __init__(self, grid):
        self._grid = grid
        self._count = 0
        

    def get_grid(self):
        return self._grid
    

    def get_player(self):
        
        player_position = self.get_grid().find_player()
        player = self.get_grid().get_mapping()[player_position]

        return player


    def step(self):
        for position, entity in self.get_grid().get_mapping().items():
            entity.step(position, self)

        self._count += 1


    def get_steps(self):
        return self._count
    

    def move_player(self, offset: Position):
        if self.get_grid().find_player() == None:
            return None
        else:
            current_player_position = self.get_grid().find_player()
            new_player_position = current_player_position.add(offset)

            if self.get_grid().in_bounds(new_player_position) == True:
                self.get_grid().move_entity(current_player_position, new_player_position)
            else:
                return None


    def direction_to_offset(self, direction: str):
        offset_possibilities = {UP : Position(0,-1), LEFT : Position(-1,0), DOWN : Position(0,1), RIGHT : Position(1,0)}

        if direction not in DIRECTIONS:
            return None
        else:
            return offset_possibilities[direction]


    def has_won(self):
        entities_on_grid = self.get_grid().serialize().values()

        if HOSPITAL not in entities_on_grid:
            return True
        else:
            return False

            
    def has_lost(self):
        return False


class IntermediateGame(Game):
    def has_lost(self):
        if self.get_player().is_infected() == True:
            return True
        else:
            return False


class AdvancedGame(IntermediateGame):
    def move_player(self, offset):
        if self.get_grid().find_player() == None:
            return None
        else:
            current_player_position = self.get_grid().find_player()
            new_player_position = current_player_position.add(offset)

            if self.get_grid().in_bounds(new_player_position) == True and new_player_position not in self.get_grid().get_mapping().keys():
                self.get_grid().move_entity(current_player_position, new_player_position)
            else:
                return None


class TextInterface(GameInterface):
    def __init__(self, size):
        self._size = size
        

    def draw(self, game):
        grid_size = self._size

        positions_with_entities = game.get_grid().get_mapping().keys()
        grid_repr = ''
        
        horizontal_border = (BORDER*(grid_size+2)) + '\n'
        grid_repr += horizontal_border
        
        for row in range(grid_size):
            grid_repr += BORDER 
            for col in range(grid_size):
                position = Position(col, row)
                if position in positions_with_entities:
                    grid_repr += game.get_grid().get_mapping()[position].display()
                else:
                    grid_repr += ' '
                    
            grid_repr += BORDER + "\n"
        grid_repr += horizontal_border
        print(grid_repr, end='')


    def handle_action(self, game, action: str):
        if game.direction_to_offset(action) == None:
            return None
        else:
            game.move_player(game.direction_to_offset(action))
            game.step()

        
    def play(self, game):
        while True:
            self.draw(game)
            action = input(ACTION_PROMPT)
            self.handle_action(game, action)

            if game.has_won() == True:
                print(WIN_MESSAGE)
                break
            elif game.has_lost() == True:
                print(LOSE_MESSAGE)
                break


class AdvancedTextInterface(TextInterface):
    def draw(self, game):
        super().draw(game)
##        print(HOLDING_MESSAGE)
##        for item in game.get_player().get_inventory().get_items():
##            print
##        


    def handle_action(self, game, action: str):
        pass
    

class Inventory(object):
    def __init__(self):
        self._inventory = [] 


    def step(self):
        pass


    def add_item(self, item):
        self._inventory.append(item.__repr__())


    def get_items(self):
        copy_inventory = self._inventory.copy()
        return copy_inventory


    def contains(self, pickup_id):
        pass


def main():
    """Entry point to gameplay."""
    print("Implement your solution and run this file")
    

if __name__ == "__main__":
    main()


