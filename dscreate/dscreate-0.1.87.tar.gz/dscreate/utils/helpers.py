import os

def get_nbgrader_directory():
    """
    Helper function for finding the top level directory of an nbgrader course.

    This function searches for the word 'source' in the absolute path of the current working directory, and uses the
    placement of the source folder to find the top level of the nbgrader course

    Returns: str. directory path.
    """

    # Get current working directory
    path = os.getcwd()
    # Split and reverse the cwd path
    split = path.split(os.sep)[::-1]
    if 'source' not in split:
        raise ValueError('ds -generate must be run from an nbgrader assignment folder within the source/ directory.')
    # Move up a directory for each directory beneath and equal to the source directory
    top_directory = ''
    for idx in range(len(split)):
        top_directory = os.path.join(top_directory, '..')
        if split[idx] == 'source':
            break

    return top_directory