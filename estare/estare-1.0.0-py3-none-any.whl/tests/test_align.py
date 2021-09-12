import unittest
import numpy as np
from skimage.io import imsave, imread
import os
from estare.src import align



class TestAlign(unittest.TestCase):
    

    @classmethod
    def setUpClass(self):
        from tests.reference_markers import reference_markers
        os.makedirs('./tests/test_results', exist_ok=True)
        targets, markers = reference_markers()
        np.save('./tests/test_images/pivot.npy', targets)
        np.save('./tests/test_images/target.npy', markers)


    @classmethod
    def tearDownClass(self):        

        for garbage_file in os.listdir('./tests/test_images'):
            os.remove(f'./tests/test_images/{garbage_file}')
            
        for garbage_file in os.listdir('./tests/test_results'):
            os.remove(f'./tests/test_results/{garbage_file}')            


        
    def test_offset(self):        
        
        del_x, del_y, theta, theta_rad = align.find_offset('./tests/test_images/pivot.npy',
                                                           './tests/test_images/target.npy')

        self.assertAlmostEqual(del_x, 26.74381464587602,
                               msg="Offset in the x-dir. is wrong.")
        
        self.assertAlmostEqual(del_y, -5.370829292101147,
                               msg="Offset in the y-dir. is wrong.")
        
        self.assertAlmostEqual(theta, 0.481598055901971,
                               msg="Rotation angle in degrees is wrong.")
        
        self.assertAlmostEqual(theta_rad, -0.008405471746693104,
                               msg="Rotation angle n radians is wrong.")


    def test_detrans(self):

        x_range = 400
        y_range = 300
        
        x_array = np.ones((x_range, y_range), dtype=int)
        y_array = np.ones((x_range, y_range), dtype=int)

        del_x = 1
        del_y = 1

        x_detrans, y_detrans = align.detrans(x_array, y_array, x_range,
                                             y_range, del_x, del_y)

        #TODO: check the entire arrays using numpy tests
        self.assertEqual(x_detrans[0, 0], -1)

        x_detrans, y_detrans = align.detrans_scalar(x_array, y_array, x_range,
                                             y_range, del_x, del_y)

        #TODO: check the entire arrays using numpy tests
        self.assertEqual(x_detrans[0, 0], -1)
        
        
    def test_derotate(self):
              
        del_x, del_y, theta, theta_rad = align.find_offset('./tests/test_images/pivot.npy',
                                                           './tests/test_images/target.npy')
        
        test_size=4
        
        x_array = np.zeros( (test_size, test_size), dtype=float )
        y_array = np.zeros( (test_size, test_size), dtype=float )
                
        for i in range(test_size):
            x_array[:,i] = [0, 1, 2, 3]
            y_array[i,:] = [0, 1, 2, 3]
        
        #TODO: rotate/derotate should not be applied to the anchor (origin)
        x_array_, y_array = align.derotate(x_array, y_array, theta, roundup=False)
        
        x_desired = np.array([[0, 0.00840537, 0.01681075, 0.02521612],
                     [0.99996467, 1.00837005, 1.01677542, 1.02518079],
                     [1.99992935, 2.00833472, 2.01674009, 2.02514547],
                     [2.99989402, 3.0082994, 3.01670477, 3.02511014]])
        
        y_desired = np.array( [[None, 0.99996467, 1.99992935, 2.99989402],
                               [-0.00840537, 0.9915593, 1.99152398, 2.99148865],
                               [-0.01681075, 0.98315393, 1.9831186, 2.98308328],
                               [-0.02521612, 0.97474856, 1.97471323, 2.9746779]] )
    
    
        np.testing.assert_almost_equal(x_array[1:, 1:], x_desired[1:, 1:])
        np.testing.assert_almost_equal(y_array[1:, 1:], y_desired[1:, 1:])


    def test_align(self):
        frame_0 = np.zeros( (270, 480), dtype=float )
       
        # pick 4 points as references
        position_1 = np.array( [200,100] ).T
        position_2 = np.array( [257,34] ).T 
        position_3 = np.array( [20,30] ).T
        position_4 = np.array( [123, 56] ).T

        # save two marker points for later stacking
        np.save('./tests/test_results/target.npy', [position_1, position_2])
        
        # mark the selected pixels in the original frame
        frame_0[position_1[0]-5:position_1[0]+5, position_1[1]-5:position_1[1]+5] = 1
        frame_0[position_2[0]-5:position_2[0]+5, position_2[1]-5:position_2[1]+5] = 1
        frame_0[position_3[0]-5:position_3[0]+5, position_3[1]-5:position_3[1]+5] = 1
        frame_0[position_4[0]-5:position_4[0]+5, position_4[1]-5:position_4[1]+5] = 1

        # save the base layer
        imsave('./tests/test_results/orig.jpeg', frame_0)
        
        # Now translate the rotated points
        transH = 15
        transW = 10

        pos1_tra = [position_1[0] + transH, position_1[1] + transW]
        pos2_tra = [position_2[0] + transH, position_2[1] + transW]
        pos3_tra = [position_3[0] + transH, position_3[1] + transW]
        pos4_tra = [position_4[0] + transH, position_4[1] + transW]

        np.testing.assert_equal(pos1_tra, [215, 110])
        np.testing.assert_equal(pos2_tra, [272,  44])
        np.testing.assert_equal(pos3_tra, [35, 40])
        np.testing.assert_equal(pos4_tra, [138,  66])

        # and now rotate them 20 deg.
        pos1_rot_tra = align.rotate(pos1_tra, 20)
        pos2_rot_tra = align.rotate(pos2_tra, 20)
        pos3_rot_tra = align.rotate(pos3_tra, 20)
        pos4_rot_tra = align.rotate(pos4_tra, 20)

        np.save('./tests/test_results/pivot.npy', [pos1_rot_tra, pos2_rot_tra])

        np.testing.assert_almost_equal(pos1_rot_tra, [164, 177])
        np.testing.assert_almost_equal(pos2_rot_tra, [241, 134])
        np.testing.assert_almost_equal(pos3_rot_tra, [19, 50])
        np.testing.assert_almost_equal(pos4_rot_tra, [107, 109])

        # Modified frame
        frame_1 = np.zeros_like(frame_0)
        frame_1[pos1_rot_tra[0]-5:pos1_rot_tra[0]+5,
                pos1_rot_tra[1]-5:pos1_rot_tra[1]+5] = 1
        
        frame_1[pos2_rot_tra[0]-5:pos2_rot_tra[0]+5,
                pos2_rot_tra[1]-5:pos2_rot_tra[1]+5] = 1
        
        frame_1[pos3_rot_tra[0]-5:pos3_rot_tra[0]+5,
                pos3_rot_tra[1]-5:pos3_rot_tra[1]+5] = 1
        
        frame_1[pos4_rot_tra[0]-5:pos4_rot_tra[0]+5,
                pos4_rot_tra[1]-5:pos4_rot_tra[1]+5] = 1

        # save the perturbed layer
        imsave('./tests/test_results/perturbed.jpeg', frame_1)
        
        # pick two of the rotated and translated points to back calculate the angle of rot.
        slope_bef = (position_2[1]-position_1[1]) / (position_2[0]-position_1[0])
        np.testing.assert_almost_equal((np.arctan(slope_bef))*180/np.pi, -49.18491612511842)

        slope_aft = (pos2_rot_tra[1]-pos1_rot_tra[1]) / (pos2_rot_tra[0]-pos1_rot_tra[0])
        np.testing.assert_almost_equal((np.arctan(slope_aft))*180/np.pi, -29.18080605249985)

        theta = (np.arctan(slope_aft))*180/np.pi - (np.arctan(slope_bef))*180/np.pi
        np.testing.assert_almost_equal(theta, 20.004110072618566)

        # derotate one of the references 
        pos1_derot = align.rotate(pos1_rot_tra, -theta)

        # compare the derotated one from its origin to calculate the relative translation  
        dxp = pos1_derot[0] - position_1[0]
        dyp = pos1_derot[1] - position_1[1]

        # Using the formulae, compute the absolute translation magnitude
        theta_rad = -theta * np.pi / 180   # radians
        del_y = ( dyp - dxp*np.tan(theta_rad) ) / \
                (np.sin(theta_rad)*np.tan(theta_rad) + np.cos(theta_rad))
        
        del_x = (dxp + del_y*np.sin(theta_rad)) / np.cos(theta_rad)

        np.testing.assert_almost_equal(del_x, 10.67414575051391)
        np.testing.assert_almost_equal(del_y, 14.52799409749281)

        # Now we can detranslate all four references
        pos1_detran = ([pos1_rot_tra[0] - del_x, pos1_rot_tra[1] - del_y] )
        pos2_detran = ([pos2_rot_tra[0] - del_x, pos2_rot_tra[1] - del_y] )
        pos3_detran = ([pos3_rot_tra[0] - del_x, pos3_rot_tra[1] - del_y] )
        pos4_detran = ([pos4_rot_tra[0] - del_x, pos4_rot_tra[1] - del_y] )

        # and now we can derotate them
        pos1_derot = align.rotate(pos1_detran, -theta)
        pos2_derot = align.rotate(pos2_detran, -theta)
        pos3_derot = align.rotate(pos3_detran, -theta)
        pos4_derot = align.rotate(pos4_detran, -theta)
       
        np.testing.assert_almost_equal(pos1_derot, [200, 100])
        np.testing.assert_almost_equal(pos2_derot, [257, 33])
        np.testing.assert_almost_equal(pos3_derot, [20,30])
        np.testing.assert_almost_equal(pos4_derot, [123, 56])

        # Reconstructed frame
        frame_3 = np.zeros_like(frame_0)

        frame_3[pos1_derot[0]-5:pos1_derot[0]+5, pos1_derot[1]-5:pos1_derot[1]+5] = 0.5
        frame_3[pos2_derot[0]-5:pos2_derot[0]+5, pos2_derot[1]-5:pos2_derot[1]+5] = 0.5
        frame_3[pos3_derot[0]-5:pos3_derot[0]+5, pos3_derot[1]-5:pos3_derot[1]+5] = 0.5
        frame_3[pos4_derot[0]-5:pos4_derot[0]+5, pos4_derot[1]-5:pos4_derot[1]+5] = 0.5

        stacked_image = align.align('./tests/test_results/orig.jpeg', './tests/test_results/perturbed.jpeg', './tests/test_results/target.npy', './tests/test_results/pivot.npy')
        #control = imread('../tests/stacked.jpeg')

        mis_align = np.linalg.norm(stacked_image - frame_0)
        #TODO: this test is problematic. Goodness of alignment changes with the algorithm
        self.assertLessEqual(np.abs(mis_align - 21.421162557285534), 1.0) 
