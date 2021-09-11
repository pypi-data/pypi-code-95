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
__author__ = "Xue Zhang, 45636932"
__email__ = "xue.zhang6@uqconnect.edu.au"


# Implement your classes here.

class Entity():

    def step(self, position: Position, game: object):
        return
    
    def display(self):
        return " "

    def __str__(self):
        return self.__class__.__name__ + "()"
    
    def __repr__(self):
        return str(self)
    

## player
class Player(Entity):

    def display(self):
        return PLAYER


class Hospital(Entity):

    def display(self):
        return HOSPITAL


class Grid():
    
    def __init__(self, size: int):
        self._dict = {}
        self._size = size

    def get_size(self) -> int:
        return self._size

    def in_bounds(self, position: Position) -> bool:
        if position.get_x() >= self.get_size() or position.get_y() >= self.get_size() or position.get_x() < 0 or position.get_y() < 0:
            return False
        return True

    def get_entities(self):
        return list(self._dict.values());
    
    def add_entity(self, position: Position, entity: Entity):
        self._dict[position] = entity

    def get_entity(self, position: Position):
        return self._dict.get(position)

    def remove_entity(self, position: Position):
        if self._dict.get(position) != None:
            del self._dict[position]

    def move_entity(self, start: Position, end: Position):
        if self._dict.get(start) != None:
            dit = self.serialize()
            start_key = start.get_x(), start.get_y()
            end_key = end.get_x(), end.get_y()
            if (dit.get(start_key) == PLAYER or dit.get(start_key) in ZOMBIES) and (dit.get(end_key) == PLAYER or dit.get(end_key) in ZOMBIES):
                self.get_entity(self.find_player()).infect()
                return
            self._dict[end] = self._dict[start]
            self.remove_entity(start)

    def get_mapping(self):
        return self._dict

    def find_player(self):
        for k,v in self._dict.items():
            if PLAYER == v.display():
                return k
            
    def find_hospital(self):
        for k,v in self._dict.items():
            if HOSPITAL == v.display():
                return k

    def find_zombies(self):
        zombies = {}
        for k,v in self._dict.items():
            if ZOMBIE == v.display():
                zombies[k] = v
        return zombies

    def find_tracking_zombies(self):
        tracking_zombies = {}
        for k,v in self._dict.items():
            if TRACKING_ZOMBIE == v.display():
                tracking_zombies[k] = v
        return tracking_zombies
    
    def serialize(self):
        dit = {}
        for k,v in self._dict.items():
            dit[k.get_x(),k.get_y()] = v.display()
        return dit


class MapLoader():

    def load(self, filename: str):
        result,len = load_map(filename)
        grid = Grid(len)
        for k in result:
            e = self.create_entity(result[k])
            if e != None:
                grid.add_entity(Position(k[0],k[1]), e)
        return grid

    def create_entity(self, token: str):
        return Entity()


class BasicMapLoader(MapLoader):

    def create_entity(self, token: str):
        if token == PLAYER:
            return Player()
        elif token == HOSPITAL:
            return Hospital()


class Game():
    
    def __init__(self, grid: Grid):
        self.grid = grid
        self.__hospital = grid.find_hospital()
        self._step = 0

    def get_grid(self):
        return self.grid

    def get_player(self):
        return self.get_grid().get_mapping().get(self.get_grid().find_player())

    def get_hospital(self):
        return self.get_grid().find_hospital()

    def step(self):
        self._step += 1

    def get_steps(self):
        return self._step

    def move_player(self, offset: Position):
        player = self.get_grid().find_player()
        grid = self.get_grid()
        grid.move_entity(player, player.add(offset))

    def direction_to_offset(self, direction: str):
        player = self.get_grid().find_player()
        grid = self.get_grid()
        p = None
        if direction == UP:
            p = Position(0, -1)
        elif direction == DOWN:
            p = Position(0, 1)
        elif direction == LEFT:
            p = Position(-1, 0)
        elif direction == RIGHT:
            p = Position(1, 0)
        else:
            print("Invalid direction entered!")
            return
        new_player = player.add(p)
        if grid.in_bounds(new_player):
            self.move_player(p)
            self.step()
        return p


    def has_won(self):
        player = self.get_grid().find_player()
        hospital = self.__hospital
        if player.__eq__(hospital):
            print(WIN_MESSAGE)
            return True
        return False

    def has_lost(self):
        return self.get_player().is_infected()


class TextInterface(GameInterface):

    def __init__(self, size: int):
        self.size = size


    def draw(self, game: Game):
        board_repr = ""
        horizontal_border = BORDER * (self.size + 2) + "\n"
        board_repr += horizontal_border
        for row in range(self.size):
            board_repr += BORDER
            for col in range(self.size):
                dit = game.get_grid().serialize()
                cell_content = dit.get((col, row), " ") 
                board_repr += cell_content
            board_repr += BORDER + "\n"    
        board_repr += horizontal_border
        print(board_repr)

    def play(slef, game: Game):
        is_break = False
        while not is_break:
            slef.draw(game)
            m = input(ACTION_PROMPT)
            slef.handle_action(game, m)
            if game.has_won():
                is_break = True
                return
            if game.has_lost():
                print(LOSE_MESSAGE)
                is_break = True
                return
            

    def handle_action(self, game: Game, action: str):
        action = game.direction_to_offset(action)
        if action == None:
            return
        zombie_list = game.get_grid().find_zombies()
        for z in zombie_list:
            zombie_list[z].step(z, game)
        tracking_zombie_list = game.get_grid().find_tracking_zombies()
        for z in tracking_zombie_list:
            tracking_zombie_list[z].step(z, game)
            

        
class VulnerablePlayer(Player):

    def __init__(self):
        self._infect = False
    
    def infect(self):
        self._infect = True

    def is_infected(self):
        return self._infect


class Zombie(Entity):

    def display(self):
        return ZOMBIE

    def step(self, position: Position, game: Game):
        grid = game.get_grid()
        random_list = random_directions()
        for i in random_list:
            p = position.add(Position(i[0], i[1]))
            if None == grid._dict.get(p):
                if grid.in_bounds(p):
                    grid.move_entity(position, p)
                    break
            elif PLAYER == grid._dict.get(p).display():
                grid._dict.get(p).infect()
                break

class IntermediateGame(Game):

    def has_lost(self):
        return super().has_lost()


class IntermediateMapLoader(BasicMapLoader):
    
    def create_entity(self, token: str):
        if token == PLAYER:
            return VulnerablePlayer()
        elif token == HOSPITAL:
            return Hospital()
        elif token == ZOMBIE:
            return Zombie()


class TrackingZombie(Zombie):

    def display(self):
        return TRACKING_ZOMBIE

    def step(self, position: Position, game: Game):
        player = game.get_grid().find_player()
        grid = game.get_grid()
        distance = 999
        p = None
        n = position.add(Position(0,-1))
        if None == grid._dict.get(n):
            if distance > player.distance(n) and grid.in_bounds(n):
                distance = player.distance(n)
                p = n
        elif PLAYER == grid._dict.get(n).display():
            grid._dict.get(n).infect()
            return
        e = position.add(Position(1,0))
        if None == grid._dict.get(e):
            if distance > player.distance(e) and grid.in_bounds(e):
                distance = player.distance(e)
                p = e
        elif PLAYER == grid._dict.get(e).display():
            grid._dict.get(e).infect()
            return
        w = position.add(Position(-1,0))
        if None == grid._dict.get(w):
            if distance > player.distance(w) and grid.in_bounds(w):
                distance = player.distance(w)
                p = w
        elif PLAYER == grid._dict.get(w).display():
            grid._dict.get(w).infect()
            return
        s = position.add(Position(0,1))
        if None == grid._dict.get(s):
            if distance > player.distance(s) and grid.in_bounds(s):
                distance = player.distance(s)
                p = s
        elif PLAYER == grid._dict.get(s).display():
            grid._dict.get(s).infect()
            return
        if p != None:
            grid.move_entity(position, p)


class Pickup(Entity):

    def __init__(self):
        self._durability = self.get_durability()

    def get_durability(self):
        return LIFETIMES[self.display()]

    def get_lifetime(self):
        return self._durability

    def hold(self):
        if self.get_lifetime() > 0:
            self._durability = self.get_lifetime() - 1

    def __repr__(self):
        return f"{self.__class__.__name__}({self.get_lifetime()})"


class Garlic(Pickup):

    def display(self):
        return GARLIC


class Crossbow(Pickup):

    def display(self):
        return CROSSBOW


class Inventory():

    def __init__(self):
        self._itmes = []

    def step(self):
        for i in self.get_items()[:]:
            i.hold()
            if i.get_lifetime() == 0:
                self.get_items().remove(i)

    def add_item(self, item: Pickup):
        self._itmes.append(item)

    def get_items(self):
        return self._itmes

    def get_item(self, pickup_id: str):
        for i in self._itmes:
            if i.display() == pickup_id:
                return i

    def contains(self, pickup_id: str):
        for i in self._itmes:
            if i.display() == pickup_id:
                return True
        return False

    
class HoldingPlayer(VulnerablePlayer):

    def __init__(self):
        self._inventory = Inventory()
        self._infect = False
        
    def get_inventory(self):
        return self._inventory

    def infect(self):
        if self._inventory.contains(GARLIC):
            print("The garlic protected you")
            return
        super().infect()

    def step(self, position: Position, game: Game):
        self._inventory.step()


class AdvancedGame(IntermediateGame):

    def move_player(self, offset: Position):
        grid = super().get_grid()
        inventory = self.get_player().get_inventory()
        is_step = True
        new_player = grid.find_player().add(offset)
        if grid._dict.get(new_player) != None:
            if (grid._dict[new_player].display() == GARLIC):
                if inventory.contains(GARLIC):
                    inventory.get_item(GARLIC)._durability = grid._dict[new_player].get_durability()
                else:
                    inventory.add_item(Garlic())
                grid._dict[new_player] == None
                is_step = False
            elif (grid._dict[new_player].display() == CROSSBOW):
                if inventory.contains(CROSSBOW):
                    inventory.get_item(CROSSBOW)._durability = grid._dict[new_player].get_durability()
                else:
                    inventory.add_item(Crossbow())
                grid._dict[new_player] == None
                is_step = False
        super().move_player(offset)
        if is_step:
            inventory.step()
        

class AdvancedMapLoader(IntermediateMapLoader):

    def create_entity(self, token: str):
        if token == PLAYER:
            return HoldingPlayer()
        elif token == HOSPITAL:
            return Hospital()
        elif token == ZOMBIE:
            return Zombie()
        elif token == TRACKING_ZOMBIE:
            return TrackingZombie()
        elif token == GARLIC:
            return Garlic()
        elif token == CROSSBOW:
            return Crossbow()


class AdvancedTextInterface(TextInterface):

    def draw(self, game: Game):
        board_repr = ""
        horizontal_border = BORDER * (self.size + 2) + "\n"
        board_repr += horizontal_border
        for row in range(self.size):
            board_repr += BORDER
            for col in range(self.size):
                dit = game.get_grid().serialize()
                cell_content = dit.get((col, row), " ") 
                board_repr += cell_content
            board_repr += BORDER + "\n"    
        board_repr += horizontal_border
        itmes = game.get_player().get_inventory().get_items()
        board_repr += "\n" + HOLDING_MESSAGE + "\n"
        for i in itmes:
            board_repr += i.__repr__() + "\n"
        print(board_repr)

    def handle_action(self, game: Game, action: str):
        grid = game.get_grid()
        inventory = game.get_player().get_inventory()
        if action == FIRE:
            if inventory.contains(CROSSBOW):
                direction = input(FIRE_PROMPT)
                if direction in DIRECTIONS:
                    if direction == UP:
                        p = Position(0, -1)
                    elif direction == DOWN:
                        p = Position(0, 1)
                    elif direction == LEFT:
                        p = Position(-1, 0)
                    elif direction == RIGHT:
                        p = Position(1, 0)
                    if grid._dict.get(grid.find_player().add(p)) != None and (grid._dict.get(grid.find_player().add(p)).display() in ZOMBIES):
                        grid.remove_entity(grid.find_player().add(p))
                        game.step()
                        inventory.step()
                        print("Successfully wiped out zombie!")
                        return
                    else:
                        print(NO_ZOMBIE_MESSAGE)
                        return
                else:
                    print(INVALID_FIRING_MESSAGE)
                    return
            else:
                print(NO_WEAPON_MESSAGE)
                return
        super().handle_action(game, action)


def main():
    """Entry point to gameplay."""
    print("Implement your solution and run this file")
    m_str = "maps/basic4.txt"
    result,len = load_map(m_str)
    map = AdvancedMapLoader()
    is_continue = True
    while is_continue:
        game = AdvancedGame(map.load(m_str))
        t = AdvancedTextInterface(len)
        t.play(game)
        str_continue = input("Do you want to play again?")
        if str_continue.lower().lower() == "n":
            is_continue = False
            print("Bye")
    

if __name__ == "__main__":
    main()
