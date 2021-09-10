# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
from sylib.machinelearning.descriptors import Descriptor

class MLPClassifierDescriptor(Descriptor):
    pass

class SkorchDescriptor(Descriptor):

    def get_attribute(self, skl, attribute):
        if getattr(skl, attribute):
        	return [{'epoch': getattr(skl, attribute)[_]['epoch'],
        		 'duration': getattr(skl, attribute)[_]['dur'],
        		 'train_loss': getattr(skl, attribute)[_]['train_loss']} 
        		 for _ in range(len(getattr(skl, attribute)))]
        else:
        	return getattr(skl, attribute)
