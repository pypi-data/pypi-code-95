#!/usr/bin/env python3
""" Makes a post request for every jpeg image in a directory.

    This script is used for google's IT_automation class. The directory
    contains images for every fruit that will be displayed in customers website.
"""
import requests
import os


def post_images(url, image_directory):
    """ This function makes a post request for every jpeg image in a directory.
    Args:
        url(string): The url the post request will be made to.
        image_directory(string): Directory path containing jpeg images.
    Returns:
        None
    """
    for root, dirs, files in os.walk(image_directory):
        files = [f for f in files if not[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for file in files:
            if '.jpeg' in file:
                image_path = os.path.join(root, file)
                with open(image_path, 'rb') as im:
                    request = requests.post(url, files={'file': im})
                    if request.status_code != 201:
                        raise Exception(
                            'POST error status={}'.format(request.status_code))


"""def main():
    url = "http://localhost/upload/"

    image_directory = os.path.expanduser('~') + '/Documents' \
                                                '/google_class' \
                                                '/project_8' \
                                                '/supplier-data' \
                                                '/images'

    post_images(url, image_directory)


if __name__ == "__main__":
    main()
"""