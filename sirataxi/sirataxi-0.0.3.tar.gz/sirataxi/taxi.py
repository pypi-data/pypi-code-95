'''
0. 0-1 = 35 thb/km
1. 2-10 = 5.5 thb/km
2. 11-20 = 6.5 thb/km
3. 21-40 = 7.5 thb/km
4. 41-60 = 8 thb/km
5. 61-80 = 9 thb/km
6. 81+ = 10.5 thb/km
'''
def sirataxi(distance):
    
    #declare parameter
    d = distance #km
    f = 35
    rate1 = 5.5
    rate2 = 6.5
    rate3 = 7.5
    rate4 = 8
    rate5 = 9
    rate6 = 10.5

    if d > 1:
        f = f
        if d > 10:
            f += (9*rate1)
            if d > 20:
                f += (10*rate2)
                if d > 40:
                    f += (20*rate3)
                    if d > 60:
                        f += (20*rate4)
                        if d > 80:
                            f += (20*rate5) + (d-80)*rate6                            
                        else:
                            f += (d-60)*rate5                            
                    else:
                        f += (d-40)*rate4                        
                else:
                    f += (d-20)*rate3                    
            else:
                f += (d-10)*rate2                
        else:
            f += (d-1)*rate1                
    
    print(f'your distance: {d} km\nfare:' + '{:,}'.format(round(f)) + ' THB')

while True:
    distance = float(input('Enter km:'))
    sirataxi(distance)
    print('----------')
    
    
            


    
            
            
            
                
    
