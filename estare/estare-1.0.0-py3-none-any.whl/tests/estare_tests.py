
import numpy as np


frame_1 = '/home/minter/workdir/Central_backup/Pictures/Test_images_for_estare_Ramberget_Dec_2020/DSC00281.JPG'

a_1 = [1270, 1953]
b_1 = [1289, 2087]

np.save('pivot.npy', (a_1, b_1))

frame_2 = '/home/minter/workdir/Central_backup/Pictures/Test_images_for_estare_Ramberget_Dec_2020/DSC00282.JPG'

a_2 = [1281, 1969]
b_2 = [1301, 2102]

np.save('target.npy', (a_2, b_2))
