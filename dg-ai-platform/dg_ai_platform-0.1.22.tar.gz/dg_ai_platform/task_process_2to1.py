from dg_ai_platform.dg_platform import ITaskProcess
from PIL import Image

class TaskProcess2to1(ITaskProcess):
    def __init__(self):
        super().__init__()

    def inference(self, input_list, output_list, options=None):
        # load input
        img1 = Image.open(input_list[0]).convert('RGB')
        img2 = Image.open(input_list[1]).convert('RGB')

        # process
        img1 = img1.resize(size=(512, 512))
        img2 = img2.resize(size=(512, 512))
        # use option param
        if options is not None:
            if 'scale' in options:
                scale_v = options['scale']
                img1 = img1.resize((int(img1.width * scale_v), int(img1.height * scale_v)))
                img2 = img2.resize((int(img2.width * scale_v), int(img2.height * scale_v)))
        output = Image.blend(img1, img2, 0.5)
        output = output.resize((output.width, output.height))

        #save output
        output.save(output_list[0])