from dg_ai_platform.dg_platform import ITaskProcess
from PIL import Image, ImageOps
from dg_ai_platform.utils import get_dynamic_outputs

class TaskProcess1toN(ITaskProcess):
    def __init__(self):
        super().__init__()

    def inference(self, input_list, output_list, options=None):
        print(options)
        img1 = Image.open(input_list[0]).convert('RGB')
        output1 = ImageOps.grayscale(img1)

        output1.save(output_list[0])
        if options is not None:
            if 'dynamic_outputs' in options:
                #If you need 4 image outputs
                d_outputs = get_dynamic_outputs(output_list, 4, ['jpg'])
                for fn in d_outputs:
                    ImageOps.posterize(img1, 1).save(fn)
                return d_outputs