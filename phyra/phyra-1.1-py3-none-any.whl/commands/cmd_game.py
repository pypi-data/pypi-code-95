import click
import random

@click.group()
def cli():
    '''Phyra Simple Game'''

################## Guess The Number Game ##################

@cli.command()
def gtn():
    '''Guess The Number Game'''
    def guess(x):
      random_number = random.randint(1, x)
      guess = 0
      while guess != random_number:
          guess = int(input(f'Guess a number between 1 and {x}: '))
          if guess < random_number:
              print('Too low.')
          elif guess > random_number:
              print('Too high.')
  
      print(f'Congrats. You have guessed the number {random_number} correctly!!')
    
    guess(10)

################## Rock Papaer Scissors Game ##################

@cli.command()
def rps():
    '''Rock Papaer Scissors Game'''
    def play():
        user = input("What's your choice? 'r' for rock, 'p' for paper, 's' for scissors\n")
        computer = random.choice(['rock', 'paper', 'scissors'])
        print(f'Computer : {computer}')

        if user == computer:
            return 'Tie Game!'

        # r > s, s > p, p > r
        if is_win(user, computer):
            return 'You won!'

        return 'You lost!'

    def is_win(player, opponent):
        # return true if player wins
        # r > s, s > p, p > r
        if (player == 'r' and opponent == 'scissors') or (player == 's' and opponent == 'paper') \
            or (player == 'p' and opponent == 'rock'):
            return True

    print(play())