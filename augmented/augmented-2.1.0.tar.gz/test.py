import augmented
arucoar = augmented.arucoar()
imgAug = {0: 'assets/unnamed.jpg',
          1: 'assets/unnamed.jpeg',
          2: 'assets/unnamed2.jpeg',
          3: 'assets/loading.gif'}
arucoar.setup(imgAug)
while True:
    arucoar.start(display=bool)
