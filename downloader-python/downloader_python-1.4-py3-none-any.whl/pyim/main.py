import turtle
import random

def main():
    turtle.speed(0)
    turtle.hideturtle()
    a={}
    with open('test.pyim','w') as f:
        for i in range(0,160,10):
            for j in range(0,160,10):
                a[str(i)+':'+str(j)] = [random.randint(0,255),
                                       random.randint(0,255),
                                       random.randint(0,255)]
        f.write(str(a))
    with open('test.pyim') as f:
        a = eval(f.read())
    for i in a:
        b = i.split(':')
        turtle.penup()
        
        turtle.goto((int(b[0]),int(b[1])))
        turtle.pendown()
        st = '#'
        
        for j in a[i]:
            
            if len(hex(j)[2:]) < 2:
                
                wdwdw = '0'+hex(j)[2:]
            else:
                wdwdw = hex(j)[2:]
            st+=wdwdw
            print(hex(j)[2:])

        
        turtle.color(st)
        
        turtle.begin_fill()
        for i in range(4):
            
            turtle.left(360/4)
            turtle.forward(10)
        turtle.end_fill()
            
    turtle.color('#000000')
main()
