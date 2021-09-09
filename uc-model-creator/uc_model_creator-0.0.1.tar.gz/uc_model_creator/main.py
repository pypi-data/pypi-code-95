import argparse

from uc_model_creator.uc_model_creator import ModelCreator


def main():
    parser = argparse.ArgumentParser(prog='uc_model_creator', description='uc_model_creator')

    parser.add_argument('-output', metavar='O', type=str, nargs='+',
                        help='the path where is model located after creation')
    parser.add_argument('-images_folder', metavar='F', type=str, nargs='+',
                        help='the folder path where is located images')

    args = parser.parse_args()
    output = args.output
    images_folder = args.images_folder

    if not output:
        raise Exception("param 'output' is required")
    if not images_folder:
        raise Exception("param 'images_folder' is required")

    model_creator = ModelCreator(output=output[0], image_folder=images_folder[0])
    model_creator.save_model()
    print("==========================================")
    print(f'Model successfully saved in {output[0]}')
    print("==========================================")
