from argparse import ArgumentParser
import argparse
from cryoloBM.bmtool import BMTool
from cryolo.utils import Filament, BoundBox
from cryolo.CoordsIO import read_cbox_boxfile, write_cbox_file, write_coords_file
from dataclasses import dataclass
from typing import Tuple, List, Dict
import numpy as np
import os
import copy
import glob
import tqdm

@dataclass
class RotationMeta:
    filename_unrotated : str
    filename_rotated : str
    rotation : Tuple[float, float, float] # x,y,z
    dimension_orig : Tuple[int, int, int] # x,y,z
    dimension_rotated : Tuple[int, int, int] # x,y,z


class RotateCBOXCoords(BMTool):



    def run(self, args):
        cbox_path = args.input
        meta_path = args.meta
        output_path= args.out
        propagation = args.propagation
        do_zsplit = args.nozsplit==False
        zfloat = args.zfloat

        cbox_files = self.get_cbox_files_paths(cbox_path)
        rotation_data = self.get_rotation_data(meta_path)
        matched_pairs = self.match_cbox_rotation_data(cbox_files=cbox_files, rotation_meta=rotation_data)
        for cbox_path, rotation_meta in tqdm.tqdm(matched_pairs, desc="Rotate"):
            cbox_dat = read_cbox_boxfile(cbox_path)
            is_filament = isinstance(cbox_dat[0], Filament)
            if is_filament:
                # filament path
                rotated_dat= self.rotate_filaments(filaments=cbox_dat, meta=rotation_meta)

                if do_zsplit:
                    rotated_dat_new = []
                    for fil in rotated_dat:
                        rotated_boxes = self.zsplit_filament_2(fil.boxes, propagation)
                        for boxes in rotated_boxes:
                            f = Filament(boxes)
                            rotated_dat_new.append(f)
                    rotated_dat = rotated_dat_new


            else:
                # bounding box path
                rotated_dat = self.rotate_boundingbox(boxes=cbox_dat, meta_path=rotation_meta)
                if not zfloat:
                    for box in rotated_dat:
                        box.z = int(round(box.z))

            filename = os.path.splitext(os.path.basename(rotation_meta.filename_unrotated))[0]

            out_cbox = os.path.join(output_path,"CBOX/")
            os.makedirs(out_cbox, exist_ok=True)
            out_file_pth = os.path.join(out_cbox, filename+".cbox")
            write_cbox_file(path=out_file_pth, coordinates=rotated_dat)


            coords_dat = None
            if is_filament:
                coords_dat = self.generate_coords_array_filaments(rotated_dat)
            else:
                coords_dat = self.generate_coords_array(rotated_dat)

            out_coords = os.path.join(output_path, "COORDS/")
            os.makedirs(out_coords, exist_ok=True)
            out_file_pth = os.path.join(out_coords, filename + ".coords")
            np.savetxt(out_file_pth, coords_dat[:,:3], fmt='%f')

            out_coords = os.path.join(output_path, "COORDS_FID/")
            os.makedirs(out_coords, exist_ok=True)
            out_file_pth = os.path.join(out_coords, filename + ".coords")
            np.savetxt(out_file_pth, coords_dat, fmt='%f')


            #write_coords_file(path=out_file_pth, boxes=coords_dat)



    def generate_coords_array_filaments(self, data: List[Filament]):
        all_fil_coords = []
        for i, fil in enumerate(data):
            coords = self.generate_coords_array(fil.boxes)
            id = np.array([i]*len(fil.boxes))
            id = id.reshape((len(id),1))
            coords_fid = np.append(coords, id, axis=1)
            all_fil_coords.append(coords_fid)
        return np.concatenate(all_fil_coords)

    def generate_coords_array(self, data: List[BoundBox]):
        coords_dat = np.empty(shape=(len(data), 3))
        for i, box in enumerate(data):
            coords_dat[i, 0] = box.x + box.w/2
            coords_dat[i, 1] = box.y + box.h/2
            coords_dat[i, 2] = box.z
        return coords_dat

    @staticmethod
    def match_cbox_rotation_data(cbox_files: List[str], rotation_meta: List[RotationMeta]):
        pairs=[]
        for meta in rotation_meta:
            for pth in cbox_files:
                filename = os.path.splitext(os.path.basename(pth))[0]
                if filename in meta.filename_rotated:
                    pairs.append((pth,meta))
        return pairs



    def create_parser(self, parentparser: ArgumentParser) -> ArgumentParser:
        parser_cbox_rotate = parentparser.add_parser(
            self.get_command_name(),
            help="Given coordinates of from a rotated tomogram it rotates them back to a unrotated tomogram.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        req = parser_cbox_rotate.add_argument_group(
            "Required arguments",
            "Add filament prior information to star",
        )

        req.add_argument(
            "-i",
            "--input",
            required=True,
            help="Path to folder with CBOX files that are to rotate ",
        )

        req.add_argument(
            "-m",
            "--meta",
            required=True,
            help="Path to meta file",
        )

        req.add_argument(
            "-p",
            "--propagation",
            default=2,
            type=int,
            help="Propagation factor for filament boxes. If a filament box is at position z after applying the rotation, the box is also added to slice z+-i with i in range of [-p,p]",
        )

        req.add_argument(
            "-o",
            "--out",
            required=True,
            help="Path to output dir.",
        )

        req.add_argument(
            "--nozsplit",
            default=False,
            action="store_true",
        )

        req.add_argument(
            "--zfloat",
            default=False,
            action="store_true",
        )

        return parser_cbox_rotate


    def get_command_name(self) -> str:
        return "rotate"

    @staticmethod
    def get_rotation_data(meta: str) -> List[RotationMeta]:
        import pandas as pd
        dat = pd.read_csv(meta, header=None)
        meta_data=[]
        for _, row in dat.iterrows():
            meta = RotationMeta(
                filename_unrotated=row[0],
                filename_rotated=row[1],
                rotation=(float(np.radians(row[2])),
                          float(np.radians(row[3])),
                          float(np.radians(row[4]))),
                dimension_orig=(row[5],row[6],row[7]),
                dimension_rotated=(row[8],row[9],row[10]),
            )
            meta_data.append(meta)
        return meta_data

    @staticmethod
    def get_cbox_files_paths(pth: str):
        files = glob.glob(os.path.join(pth,"*.cbox"))
        return files

    def rotate_boundingbox(self, boxes : List[BoundBox], meta : RotationMeta) -> List[BoundBox]:
        '''
        Rotates the bounding boxes according rotation meta
        '''

        # create numpy array with x,y,z, apply necessary conversions
        coords = np.zeros(shape=(len(boxes),3))

        for i, b in enumerate(boxes):
            coords[i,0] = b.x + b.w/2
            coords[i,1] = b.y + b.h/2
            coords[i,2] = b.z

        rotated_boxes = []

        points = self.rotate_points(coords_raw=coords, meta=meta)
        for row_index, row in enumerate(points):
            box = BoundBox(x=row[0]-boxes[row_index].w/2,
                           y=row[1]-boxes[row_index].h/2,
                           z=row[2],
                           w=boxes[row_index].w,
                           h=boxes[row_index].h,
                           c=boxes[row_index].c,
                           depth=1)
            rotated_boxes.append(box)

        return rotated_boxes

    @staticmethod
    def zsplit_filament_2(boxes: List[BoundBox], propagation: int) -> List[List[BoundBox]]:
        '''
        Splits filament into sub-filaments with constant z value
        '''
        def add_box_to_dict(box_dict: Dict, box: BoundBox, w:int=1):
            for i in range(-w, (w+1)):
                if (box.z+i) not in box_dict:
                    box_dict[box.z+i] = []

            for i in range(-w, (w + 1)):
                b_cpy = copy.deepcopy(box)
                b_cpy.z = b_cpy.z + i
                box_dict[b_cpy.z].append(b_cpy)

        splitted_filaments: List[Filament] = []
        boxes_per_slice = {}

        for b in boxes:
            b = copy.deepcopy(b)
            b.z = int(np.round(b.z))
            add_box_to_dict(boxes_per_slice, b, propagation)
        list_boxes = []
        for key in boxes_per_slice:
            list_boxes.append(boxes_per_slice[key])
            #f = Filament(boxes=boxes_per_slice[key])
            #splitted_filaments.append(f)

        return list_boxes


    def rotate_filaments(self, filaments : List[Filament],
                         meta : RotationMeta
                         ) -> List[Filament]:
        '''
        Rotates the filament positions.
        '''

        rotated_filaments: List[Filament] = []

        for filament in filaments:
            boxes = filament.boxes
            rotated_boxes = [self.rotate_boundingbox(boxes=boxes,meta=meta)]
            for boxes in rotated_boxes:
                f = Filament(boxes=boxes)
                rotated_filaments.append(f)

        return rotated_filaments


    def rotate_points(self, coords_raw, meta : RotationMeta):

        # calc from meta
        thickness_rot = meta.dimension_rotated[2]
        thickness_ori= meta.dimension_orig[2]
        rot_angles_xyz = meta.rotation
        tomogram_dimensions_original = (meta.dimension_orig[0],meta.dimension_orig[1])
        # Translation to shift the origin to the center
        '''
        coords_columnsplit = np.hsplit(coords_raw, 4)
        coords = np.column_stack(
            (coords_columnsplit[0], coords_columnsplit[1], coords_columnsplit[2])
        )
        '''
        #print(coords_raw)
        coords = coords_raw
        recoords_matrix = np.array([-meta.dimension_rotated[0] / 2, -meta.dimension_rotated[1] / 2,
                                    -float(thickness_rot / 2)])
        coords_shifted = np.add(coords, recoords_matrix)

        # Invert coords array for rotation
        coords_inv = coords_shifted.swapaxes(0, 1)

        # Calculate rotation matrix
        rotx, roty, rotz = rot_angles_xyz
        R_z = np.array(
            [[np.cos(rotz), -np.sin(rotz), 0], [np.sin(rotz), np.cos(rotz), 0], [0, 0, 1]]
        )
        R_y = np.array(
            [[np.cos(roty), 0, np.sin(roty)], [0, 1, 0], [-np.sin(roty), 0, np.cos(roty)]]
        )
        R_x = np.array(
            [[1, 0, 0], [0, np.cos(rotx), -np.sin(rotx)], [0, np.sin(rotx), np.cos(rotx)]]
        )
        R = np.dot(R_x, np.dot(R_y, R_z))
        R_inv = np.linalg.inv(R)

        # Rotate the points
        new_coords_inv = np.dot(R_inv, coords_inv)

        # Revert coords and shift back the origin to the corner
        new_coords = new_coords_inv.swapaxes(0, 1)

        recoords_matrix_inv = np.array(
            [tomogram_dimensions_original[0] / 2, tomogram_dimensions_original[1] / 2,
             float(thickness_ori / 2)]
        )  # Half dimension orignal tomogram
        new_coords_recoords = np.add(new_coords, recoords_matrix_inv)
       # final = np.column_stack((new_coords_recoords))
        return new_coords_recoords