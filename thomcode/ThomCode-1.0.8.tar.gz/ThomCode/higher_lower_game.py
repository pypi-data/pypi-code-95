import random,time

def NumQuestion():
    while True:
        try:
            num = int(input()) 
        except ValueError:
            print( "sorry, but this is not a number, please try again" )
            continue
        return num
    

def higher_lower_game():

    naam = input ("\n\nWelcome, let's play a game, but first let's start with, what's your name? ")
    print ("Heey", naam ,"nice to meet you!")
    time.sleep(2)
    print ("Shall we start with the game then?")
    time.sleep(2)
    print ("\n\nOkay, I have a number between 0 and 1000 in my mind and you have to guess what that number is.")
    time.sleep(4)
    print ("Now that that's clear" ,naam, "we can start, let me think of a number first...")
    time.sleep(5)
    print ("\nOkay i came up with one")

    C = "j"
    D = 0
    E = 1000

    while C != "no":
        B = random.randint(0,1000)
        print ("What number do you think it is?")
        A = NumQuestion()

        while A != B:
            if A > B:
                if A-B > 300:
                    print("\nMUCH lower! Take another guess.")
                    A = NumQuestion()
                    D +=1
                elif A-B > 20:       
                    print ("\nlower, Take another guess.")
                    A = NumQuestion()
                    D +=1
                else:
                    print ("\nYou are very warm but still need to go a little bit lower!")
                    A = NumQuestion()
                    D +=1
            else:
                if B-A > 300:
                    print("\nMUCH higher! Take another guess.")
                    A = NumQuestion()
                    D +=1
                elif B-A > 20:       
                    print ("\nHigher, Take another guess.")
                    A = NumQuestion()
                    D +=1
                else:
                    print ("\nYou are very warm but still need to go a little higher!")
                    A = NumQuestion()
                    D +=1

        D +=1
        print ("\n\n\nYES, congratulations",naam,"You guessed it in" ,D, "times!")
        time.sleep(2)
        if D < E:
            E = D
            print ("That's your best score so far,",naam,"!")
            time.sleep(2)
        else:
            print ("Unfortunately, the current score is " ,E, " but you can try again to establish a new high score!")
            time.sleep(3)

        print ("Would you like to try again?")
        time.sleep(2)

        D = 0
        F = False


        while F != True:

            C = input ("Type 'yes' or 'no'. ")
            if C == "yes":
                print ("\nNice!!! let me think of one more...")
                time.sleep(5)
                print ("\nOkay I have a new number in my mind")
                F = True
            elif C == "no":
                print ("\nAwh... That's to bad, see you next time",naam,"\n\n")
                F = True
            elif C == "NO!":
                print ("\nWhoa keep it calm",naam,"... I didn't know you thought it was such a boring game...\n\n")
                time.sleep(5)
                print ("If it's so hard for you" ,naam, "I know a solution for that.")
                time.sleep(4)
                print ("!!!!Self-destruct activated!!!!")
                time.sleep(4)
                print ("5")
                time.sleep(1)
                print ("4")
                time.sleep(1)
                print ("3")
                time.sleep(1)
                print ("2")
                time.sleep(1)
                print ("1")
                time.sleep(1)
                print ("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
                C = "no"
                F = True
            else:
                print ("\nSorry I didn't quite get that" ,naam, "can you say that again?")

higher_lower_game = higher_lower_game()