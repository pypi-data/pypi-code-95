from typing import List

from magnumapi.geometry.CosThetaGeometry import HomogenizedCosThetaGeometry


class AnsysInputBuilder:
    """ An AnsysInputBuilder class with methods used to create an ANSYS coil geometry input

    """

    @classmethod
    def write_geometry_input_file(cls, homo_geometry: HomogenizedCosThetaGeometry, model_path: str) -> None:
        """ Class method writing a geometry parameters for ANSYS input file from a homogenized cos-theta geometry

        :param homo_geometry: a homogenized cos-theta geometry
        :param model_path: a path to model input
        """
        output_text = cls.prepare_ansys_model_input(homo_geometry)

        with open(model_path, 'w') as file_write:
            for output_text_el in output_text:
                file_write.write(output_text_el + '\n')

    @staticmethod
    def prepare_ansys_model_input(homo_geometry: HomogenizedCosThetaGeometry) -> List[str]:
        """ Static method preparing an ANSYS model input

        :param homo_geometry:
        :return:
        """
        n_layers = homo_geometry.get_number_of_layers()
        blocks_per_layer = homo_geometry.get_number_of_blocks_per_layer()
        return AnsysInputBuilder.generate_ansys_input_text(homo_geometry, n_layers, blocks_per_layer)

    @staticmethod
    def generate_ansys_input_text(homo_geometry: HomogenizedCosThetaGeometry, n_layers, blocks_per_layer) -> List[str]:
        """ Method generating an ANSYS coil geometry input text from a homogenized cos-theta geometry

        :param homo_geometry: homogenized cos-theta geometry
        :param n_layers: number of layers
        :param blocks_per_layer: number of blocks per layer
        :return: a list of model inputs
        """
        model_inputs = []
        model_inputs.append('! Example Input File\n')
        model_inputs.append('! -------------------\n')
        model_inputs.append('! - Standard\n')
        model_inputs.append('/UNITS,SI\n')
        model_inputs.append('pi = acos(-1)\n')
        model_inputs.append('*afun,deg		 ! Specifies the units for angular functions in parameter expressions\n')
        model_inputs.append('tref,293\n')
        model_inputs.append('! -------------------\n')
        model_inputs.append('! Set-up arrays\n')
        model_inputs.append('! *dim,V_Field,array,1,1\n')
        model_inputs.append('! *dim,V_Nlay,array,1,1\n')
        model_inputs.append('! *dim,V_blocks,array,1,1\n')
        model_inputs.append('! *dim,V_current,array,1,1\n')
        model_inputs.append('! *dim,V_rad,array,1,2\n')
        model_inputs.append('! *dim,V_turns,array,1,1\n')
        model_inputs.append('! *dim,V_corners,array,2,4\n')
        model_inputs.append('\n')
        model_inputs.append('! General\n')

        model_inputs.append('Nlay = %d\n' % n_layers)
        model_inputs.append('\n')

        radius_inner_prev = None
        index_layer = -1
        index_block = 0
        for block in homo_geometry.blocks:
            if radius_inner_prev != block.block_def.radius_inner:
                index_block = 0
                index_layer += 1
                model_inputs.append('! Layer\n')
                model_inputs.append('Nb%d = %d\n' % (index_layer + 1, blocks_per_layer[index_layer]))
                model_inputs.append('current%d = %f\n' % (index_layer + 1, block.block_def.current))
                model_inputs.append('r%d1 = %fe-3\n' % (index_layer + 1, block.block_def.radius_inner))
                model_inputs.append('r%d2 = %fe-3\n' % (index_layer + 1, block.block_def.radius_outer))

            model_inputs.append('! Block\n')
            model_inputs.append('Nc%d%d = %d\n' % (index_layer + 1, index_block + 1, block.block_def.nco))
            model_inputs.append('\n')
            model_inputs.append('! Save angles\n')
            model_inputs.append('t%d%d_1 = %.4f\n' % (index_layer + 1, index_block + 1, block.block_def.phi_0))
            model_inputs.append('t%d%d_2 = %.4f\n' % (index_layer + 1, index_block + 1, block.block_def.phi_1))
            model_inputs.append('t%d%d_3 = %.4f\n' % (index_layer + 1, index_block + 1, block.block_def.phi_2))
            model_inputs.append('t%d%d_4 = %.4f\n' % (index_layer + 1, index_block + 1, block.block_def.phi_3))

            if index_block + 1 == blocks_per_layer[index_layer]:
                # Fixes the first 2 angles of the 1st block to be 0 / assumes mid-plane shim thickness = 0
                model_inputs.append('\n')
                model_inputs.append('t%d1_1 = 0\n' % (index_layer + 1))
                model_inputs.append('t%d1_2 = 0\n' % (index_layer + 1))
                model_inputs.append('\n')

            index_block += 1
            radius_inner_prev = block.block_def.radius_inner

        model_inputs.append('! Names\n')
        model_inputs.append('r1 = r11\n')
        model_inputs.append('r%d = r%d2\n' % (n_layers + 1, n_layers))
        model_inputs.append('rout = r%d\n' % (n_layers + 1))
        model_inputs.append('Nlayers = Nlay\n')

        model_inputs.append('\n')
        model_inputs.append('! -------------------------------------\n')
        model_inputs.append('! - Geometry parameters\n')
        model_inputs.append('! ---- Filler\n')
        model_inputs.append('*set, fillerth, 5e-3\n')

        model_inputs.append('\n')
        model_inputs.append('! ---- Yoke\n')
        model_inputs.append('*set,yoketh,260e-3\n')

        model_inputs.append('\n')
        model_inputs.append('! Update geometry\n')
        model_inputs.append('*set, rin_yoke, rout + fillerth\n')
        model_inputs.append('*set, rout_yoke, rin_yoke + yoketh\n')

        model_inputs.append('\n')
        model_inputs.append('! -------------------------------------\n')
        model_inputs.append('! Interlay Contact - Filler is Nlayers+1\n')
        model_inputs.append('! Glue = 5 , Sliding = 0\n')
        model_inputs.append('ilay_12 = 5\n')
        model_inputs.append('ilay_23 = 0\n')
        model_inputs.append('ilay_34 = 5\n')
        model_inputs.append('ilay_45 = 0\n')
        model_inputs.append('! -------------------------------------\n')
        model_inputs.append('! Mesh Parameters\n')
        model_inputs.append('mpar = 1\n')
        model_inputs.append('\n')
        model_inputs.append('mesh_azim_size = mpar*2e-3    ! Coil Azimuthal\n')
        model_inputs.append('mesh_radial_size = mpar*2e-3    ! Coil Radial\n')
        model_inputs.append('\n')
        model_inputs.append('msize_aperture = mpar*1e-3\n')
        model_inputs.append('msize_filler = mpar*3e-3\n')
        model_inputs.append('msize_yoke = mpar*10e-3\n')
        model_inputs.append('\n')
        model_inputs.append('!!!!!!!!!!!!!!!!!!!!!!!\n')
        model_inputs.append('! Friction Parameters !\n')
        model_inputs.append('!!!!!!!!!!!!!!!!!!!!!!!\n')
        model_inputs.append('mu_single = 0.0\n')
        model_inputs.append('mu_g10_coil = mu_single\n')
        model_inputs.append('mu_ti_coil = mu_single\n')
        model_inputs.append('mu_ti_g10 = mu_single\n')
        model_inputs.append('mu_g10_ss = mu_single\n')
        model_inputs.append('mu_alu_iron = mu_single\n')
        model_inputs.append('mu_ss_ss = mu_single\n')
        model_inputs.append('mu_ss_ti = mu_single\n')
        model_inputs.append('mu_ss_iron = mu_single\n')

        return model_inputs
