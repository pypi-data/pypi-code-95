from dg_ai_platform.dg_platform import ITaskProcess
from PIL import Image, ImageOps

class TaskProcess1to1(ITaskProcess):
    def __init__(self):
        super().__init__()

    def inference(self, input_list, output_list, options=None):
        #load input
        img1 = Image.open(input_list[0]).convert('RGB')

        #use option param
        if options is not None:
            if 'scale' in options:
                scale_v = options['scale']
                img1 = img1.resize((int(img1.width * scale_v), int(img1.height * scale_v)))
        #Process images
        img1 = ImageOps.grayscale(img1)

        #save output
        img1.save(output_list[0])