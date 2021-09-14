"""
Title: 60 Python Patterns
Author: Rushikesh Kundkar
Description: Given below are the functions implementing 60 different patterns in python.
"""

print("Welcome to",__name__)

def rect1(row,column,char='* '):
    for i in range(row):
        print(char*column)

def rect2(row,column,char='* '):
    for i in range(row):
        for i in range(column):
            print(char,end='')
        print()

def numRect1(row,column):
    for i in range(1,row+1):
        print( (str(i)+' ') * column )

def numRect2(row,column):
    for i in range(1,row+1):
        for j in range(1,column+1):
            print((str(j)+' '), end="")
        print()

def revNumRect1(row,column):
    for i in range(row,0,-1):
        print( ( str(i) + " ")*column  )

def revNumRect2(row,column):
    for i in range(row):
        for j in range(column,0,-1):
            print(str(j), end=" ")
        print()    

def alphaRect1(row,column):
    for i in range(row):
        print((chr(65+i)+' ')*column)

def alphaRect2(row,column):
    for i in range(row):
        for j in range(column):
            print(chr(65+j), end=" ")
        print()

def revAlphaRect1(row,column):
    for i in range(row,0,-1):
        print( (chr(64+i)+' ')*column)

def revAlphaRect2(row,column):
    for i in range(row):
        for j in range(column,0,-1):
            print( chr(64+j), end = ' ' )
        print()

def leftPyramid(height,char='* '):
    num_of_stars = 1
    for i in range(height):
        print(char*num_of_stars)
        num_of_stars+=1

def numPyramid1(height):
    for i in range(1,height+1):
        print((str(i) + ' ')*i)

def numPyramid2(height):
    for i in range(2,height+2):
        for j in range(1,i):
            print(j, end=' ')
        print()

def numPyramid3(height):
    for i in range(height):
        for j in range(i+1,0,-1):
            print(str(j), end=' ' )
        print()

def numPyramid4(height):
    adjuster = 0
    for i in range(height+1):
        for j in range(i,i+adjuster):
            print(str(j), end = ' ')
        adjuster+=1
        print()

def alphaPyramid1(height):
    for i in range(height):
        print( (chr(65+i) + ' ' )*(1+i) )

def alphaPyramid2(height):
    for i in range(height):
        for j in range(i):
            print(chr(65+j) , end=' ')
        print()

def alphaPyramid3(height):
    for i in range(1,height+1):
        for j in range(i,0,-1):
            print( chr(64+j), end = ' '    )
        print()

def downLeftPyramid(height,char='* '):
    for i in range(height,0,-1):
        print(char*i)

def downNumPyramid1(height):
    for i in range(1,height+1):
        print( (str(i) + ' ')*(height+1-i) )

def downNumPyramid2(height):
     for i in range(height,0,-1):
        for j in range(1,i+1):
            print(str(j), end=' ')
        print()

def downNumPyramid3(height):
    for i in range(height,0,-1):
        for j in range(i,0,-1):
            print(str(j), end=' ')
        print()

def downAlphaPyramid1(height):
    for i in range(height,0,-1):
        print( (chr(65+(height-i)) + ' ')*i )

def downAlphaPyramid2(height):
    for i in range(height,0,-1):
        for j in range(i):
            print(chr(65+j), end = ' ')
        print()

def downAlphaPyramid3(height):
    for i in range(height,0,-1):
        for j in range(i,0,-1):
            print( chr(64+j) , end = " ")
        print()

def revDownNumPyramid1(height):
    for i in range(height,0,-1):
        print( (str(i) + ' ')*i  )

def revDownNumPyramid2(height):
    for i in range(height):
        for j in range(height,i,-1):
            print(j, end = ' ')
        print()

def revDownAlphaPyramid1(height):
    for i in range(height,0,-1):
        print( (chr(64+i) + ' ')*i )

def revDownAlphaPyramid2(height):
    for i in range(height):
        for j in range(height,i,-1):
            print( chr(64+j) , end = ' ')
        print()

def rightPyramid(height,char='* '):
    for i in range(height+1):
        print('  '*(height - i) + i*char )

def rightNumPyramid1(height):
    spaces = height+1
    for i in range(spaces):
        print( '  '*(spaces - i) +  ( str(i) + " " )*i )

def rightNumPyramid2(height):
    for i in range(2,height+2):
        for j in range(height+2-i,0,-1):
            print('  ', end='')
        for k in range(1,i):
            print(k, end = ' ')
        print()

def rightNumPyramid3(height):
    for i in range(height):
        print('  '*(height-i), end = '')
        for j in range(i+1,0,-1):
            print(str(j), end=' ' )
        print() 

def rightAlphaPyramid1(height):
    for i in range(height):
        print( '  '*(height - i) +  ( chr(65+i) + " " )*(i+1) )  

def rightAlphaPyramid2(height):
    for i in range(2,height+2):
        for j in range(height+2-i,0,-1):
            print('  ', end='')
        for k in range(1,i):
            print(chr(64+k), end = ' ')
        print()

def revAlphaPyramid3(height):
    for i in range(height):
        print('  '*(height-i), end = '')
        for j in range(i+1,0,-1):
            print(chr(64+j), end=' ' )
        print() 

def downRightPyramid(height,char='* '):
    for i in range(height,0,-1):
        for k in range(height-i+1):
            print(' ', end = ' ')
        for j in range(i,0,-1):
            print(char, end='')
        print()

def rightDownRevNumPyramid1(height):
    for i in range(height,0,-1):
        for j in range(height - i + 1):
            print('  ', end='')
        for k in range(i,0,-1):
            print(str(i), end=' ')
        print()

def rightDownNumPyramid(height):
    for i in range(height):
        for j in range(i):
            print('  ', end = '')
        for k in range(height,i,-1):
            print(str(height+1-k) , end = ' ') # Adjustment is done by some operations
        print()

def rightDownRevAlphaPyramid(height):
    for i in range(height,0,-1):
        for j in range(height - i + 1):
            print('  ', end='')
        for k in range(i,0,-1):
            print(chr(64+i), end=' ')
        print()

def rightDownAlphaPyramid(height):
    for i in range(height):
        for j in range(i):
            print('  ', end = '')
        for k in range(height,i,-1):
            print(chr(64+height+1-k) , end = ' ') # just change str to chr
        print()

def centredPyramid(height, char = '* '):
    for i in range(1,height+1):
        print(' '*(height-i) + char*i)

def centredNumPyramid1(height):
    for i in range(1,height + 1):
        print( ' '*(height + 1- i), end='')

        for j in range(1,i):
            print( str(i) , end = '' )

        for k in range(i):
            print(str(i), end = '' )
        print()
       
def centredOddNumPyramid(height):
    for i in range(1,height + 1):
        print( ' '*(height + 1- i), end='')

        for j in range(1,i):
            print( str(2*i-1) , end = '' )

        for k in range(i):
            print(str(2*i - 1), end = '' )
        print()   

def centredAlphaPyramid1(height):
    for i in range(1,height + 1):
        print( ' '*(height + 1- i), end='')

        for j in range(1,i):
            print( chr(64+i) , end = '' )

        for k in range(i):
            print(chr(64+i), end = '' )
        print()

def centredOddAlphaPyramid(height):
    for i in range(1,height + 1):
        print( ' '*(height + 1- i) , end='')

        for j in range(i):
            print( chr( 64 + 2*i - 1 ) , end = '' )

        for k in range(1,i):
            print(chr( 64 + 2*i - 1 ), end = '' )
        print()  

def centredNumPyramid2(height):                                #    1
    adjuster = 0                                               #   123
    for i in range(2,height+2):                                #  12345
  # The pattern is shown above. We break it into two simple patterns and print them simultaneously                               
        for j in range(height+1-i,0,-1): # Printing the required no of spaces(range is selected for the inner loops)
            print(' ', end='')

        for l in range(1,i):           # This loop prints 1 -->      #     1
            print(l, end = '')                                       #    12
                                                                     #   123
        for k in range(i,i+adjuster):  # This loop prints 2 --> #     (empty space)    
            print(k,end = '')                                   #   3   
                                                                #   45
        print()          # The adjuster controls the length of numbers of pattern 2 it increases with i  
        adjuster+=1      # Therefore we see that in pattern 2, as we move down vertically, the number increases
                         # and the row of numbers grows. (empty in first line, 3 in second, 45 in third  line.)

def centredNumPyramid3(height):
    adjuster = 0 ;balancer=1
    for i in range(1,height+1):              
                                              
        for kb in range(height+1,i,-1):       
            print('  ', end = '')

        for j in range(i+adjuster,i,-1):      # This Pattern is same as the revRowCentredNumPyramid()
            print(str(j), end = ' ')          # But it uses the two adjustment logic
                                              # The later is simple to Understand
        for j in range(i+adjuster+1,i,-1):
            print(str(j-balancer), end = ' ')

        adjuster+=1 ; balancer+=1
        print()          
             
def revRowCentredNumPyramid(height):                     #     1
    adjuster = 1                                         #    321
    for i in range(height):                              #   54321

        for j in range(height+1-i,0,-1):# Printing the required no of spaces(range is selected for the inner loops)
            print(' ', end='')
        
        for k in range(i+adjuster,i,-1):  # This loop prints 1 -->   #     1
            print(k,end = '')                                        #    32
                                                                     #   543
        for l in range(i,0,-1):  # This loop prints 2 --> #   (empty)
            print(l, end = '')                            #    1
                                                          #   21
        print()      # This time, the adjuster works with a reverse range therefore you see the digits repeating
        adjuster+=1  # because of the range function (see the above function for adjuster).The second loop
                     # is made to collapse in first iteration and though, it prints the pattern 2 when iterated
                     # seperatedly but it adjusts itself adjacent to the above pattern bcoz of end = ''

def centredAlphaPyramid2(height):            
    adjuster = 0                              
    for i in range(2,height+2):               
                                         
        for j in range(height+1-i,0,-1): 
            print(' ', end='')           

        for l in range(1,i):                # This Pattern is an exact copy of centredNumPyramid2()
            print(chr(64+l), end = '')      # The only difference here is that the numbers are carefully
                                            # casted into alphabets by using the chr(ASCII) function
        for k in range(i,i+adjuster):
            print(chr(64+k),end = '')

        print()
        adjuster+=1

def revRowCentredAlphaPyramid(height):
    adjuster = 1
    for i in range(height):

        for j in range(height+1-i,0,-1):
            print(' ', end='')
        
        for k in range(i+adjuster,i,-1):    # This Pattern is an exact copy of revRowCentredNumPyramid()
            print(chr(64+k),end = '')       # The only difference here is that the numbers are carefully
                                            # casted into alphabets by using the chr(ASCII) function
        for l in range(i,0,-1):
            print(chr(64+l), end = '')
        
        print()
        adjuster+=1

def centredNumPyramid4(height):            #     0
    adjuster = 1                           #    101
    for i in range(height,0,-1):           #   21012

        for j in range(i,0,-1):  # Printing the required no of spaces(range is selected for the inner loops)
            print(' ', end = '')
        
        for k in range(i,i+adjuster):           # This loop prints 1 --> #     0
            print(height-k, end = '')                                    #    10
                                                                         #   210
        for l in range(1,height-i+1):  # This loop prints 2 --> #   (empty)
            print(l,end = '')                                   #    1
                                                                #   12
        adjuster+=1
        print()
        # In this case, the first loop uses the adjuster. Note that now we are printing height-k and not k 
        # The row expands as we move to new line therefore we see 0,10,210 in 1st,2nd and 3rd line respectively
        # As i decreases the adjuster increases which increases the row size every new line
        # But the sum i+adjuster remains same and is equal height which explains the stable printing of zeroes
        # every newline (please read this very carefully)
        # The second loop prints the pattern 2 when compiled but in the whole pattern it gets adjusted because of
        # end = ''
          
def centredAlphaPyramid3(height):
    adjuster = 1
    for i in range(height,0,-1):
        for j in range(i,0,-1):
            print(' ', end = '')
        
        for k in range(i,i+adjuster):         # This Pattern is an exact copy of revRowCentredNumPyramid()
            print(chr(65+height-k), end = '') # The only difference here is that the numbers are carefully
                                              # casted into alphabets by using the chr(ASCII) function
        for l in range(1,height-i+1): 
            print(chr(65+l),end = '')
            
        adjuster+=1
        print()
#406 needs commenting
def centredNumPyramid5(height):        
    for i in range(1,height+1):

        for k in range(height+1-i,0,-1):
            print(' ', end = ' ')

        for j in range(1,i):
            print(j, end = ' ')

        for f in range(i,0,-1):
            print(f,end = ' ')
        
        print()

def centredAlphaPyramid4(height):
    for i in range(1,height+1):

        for k in range(height+1-i,0,-1):
            print(' ', end = ' ')

        for j in range(1,i):
            print(chr(64+j), end = ' ')

        for f in range(i,0,-1):
            print(chr(64+f),end = ' ')
        
        print()

def centredNumPyramid6(height):
    spaces = height+1
    for i in range(spaces):
        print( ' '*(spaces - i) +  ( str(i) + " " )*i ) 

def centredAlphaPyramid5(height):
    for i in range(1,height+1):

        for k in range(height+1-i,0,-1):
            print(' ', end = ' ')

        for j in range(1,i):
            print(chr(64+j), end = ' ')

        for f in range(i,0,-1):
            print(chr(64+f),end = ' ')
        
        print()

def downCentredPyramid(height,char = '* '):
    for i in range(height,0,-1):
        print( " "*(height-i), end = '' )
        print( char*i )  
#14 july
def downCentredNumPyramid1(height):
    for i in range(height,0,-1):
        print( ' '*(height-i) , end = '' )
        print( ( str(i) + ' ' )*i )
    
def downCentredOddNumPyramid(height):
    for i in range(height,0,-1):
        print( ' '*(height-i) , end = '' )
        print( ( str(2*i-1) + ' ' )*i )

def numSquare(height):
    for i in range(1,height+1):
        for j in range(i,i+height):
            print(j,end = ' ')
        print()