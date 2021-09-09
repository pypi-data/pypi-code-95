# from cs202courseware.ug2report1 import Report1

import pickle
import os
import glob
import shutil
import time
import zipfile
import io
import inspect
import subprocess

def compile_docker_image(Dockerfile, tag=None):
    assert os.path.isfile(Dockerfile)
    base = os.path.dirname(Dockerfile)
    if tag == None:
        tag = os.path.basename(base)
    os.system(f"cd {base} && docker build --tag {tag} .")
    return tag


def student_token_file_runner(host_tmp_dir, student_token_file, instructor_grade_script, grade_file_relative_destination):
    """
    :param Dockerfile_location:
    :param host_tmp_dir:
    :param student_token_file:
    :param ReportClass:
    :param instructor_grade_script:
    :return:
    """
    assert os.path.exists(student_token_file)
    assert os.path.exists(instructor_grade_script)
    start = time.time()

    with open(student_token_file, 'rb') as f:
        results = pickle.load(f)
    sources = results['sources'][0]

    with io.BytesIO(sources['zipfile']) as zb:
        with zipfile.ZipFile(zb) as zip:
            zip.extractall(host_tmp_dir)
    # Done extracting the zip file! Now time to move the (good) report test class into the location.

    gscript = instructor_grade_script
    print(f"{sources['report_relative_location']=}")
    print(f"{sources['name']=}")

    print("Now in docker_helpers.py")
    print(f'{gscript=}')
    print(f'{instructor_grade_script=}')
    gscript_destination = host_tmp_dir + "/" + grade_file_relative_destination
    print(f'{gscript_destination=}')

    shutil.copy(gscript, gscript_destination)

    # Now everything appears very close to being set up and ready to roll!.
    d = os.path.normpath(grade_file_relative_destination).split(os.sep)
    d = d[:-1] + [os.path.basename(instructor_grade_script)[:-3]]
    pycom = ".".join(d)

    """
    docker run -v c:/Users/tuhe/Documents/2021/python-docker/tmp:/app python-docker python3 -m cs202courseware.ug2report1_grade
    """
    pycom = "python3 -m " + pycom # pycom[:-3]
    print(f"{pycom=}")

    token_location = host_tmp_dir + "/" + os.path.dirname( grade_file_relative_destination ) + "/*.token"

    elapsed = time.time() - start
    # print("Elapsed time is", elapsed)
    return pycom, token_location


def docker_run_token_file(Dockerfile_location, host_tmp_dir, student_token_file, instructor_grade_script=None):
    """
    This thingy works:

    To build the image, run:
    docker build --tag python-docker .

    To run the app run:

    docker run -v c:/Users/tuhe/Documents/2021/python-docker/tmp:/app python-docker > output.log

    """
    # A bunch of tests. This is going to be great!
    assert os.path.exists(Dockerfile_location)
    start = time.time()

    with open(student_token_file, 'rb') as f:
        results = pickle.load(f)
    sources = results['sources'][0]

    if os.path.exists(host_tmp_dir):
        shutil.rmtree(host_tmp_dir)

    with io.BytesIO(sources['zipfile']) as zb:
        with zipfile.ZipFile(zb) as zip:
            zip.extractall(host_tmp_dir)
    # Done extracting the zip file! Now time to move the (good) report test class into the location.
    gscript = instructor_grade_script

    student_grade_script = host_tmp_dir + "/" + sources['report_relative_location']
    instructor_grade_script = os.path.dirname(student_grade_script) + "/"+os.path.basename(gscript)
    shutil.copy(gscript, instructor_grade_script)

    """
    docker run -v c:/Users/tuhe/Documents/2021/python-docker/tmp:/home python-docker python3 -m cs202courseware.ug2report1_grade
    """
    dockname = os.path.basename( os.path.dirname(Dockerfile_location) )

    tmp_grade_file =  sources['name'] + "/" + sources['report_relative_location']

    pycom = ".".join( sources['report_module_specification'][:-1] + [os.path.basename(gscript)[:-3],] )
    pycom = "python3 -m " + pycom

    tmp_path = os.path.abspath(host_tmp_dir).replace("\\", "/")
    dcom = f"docker run -v {tmp_path}:/home {dockname} {pycom}"
    cdcom = f"cd {os.path.dirname(Dockerfile_location)}"
    fcom = f"{cdcom}  && {dcom}"
    print("> Running docker command")
    print(fcom)
    init = time.time() - start
    # thtools.execute_command(fcom.split())
    subprocess.check_output(fcom.split(), shell=True).decode("utf-8")
    host_tmp_dir +"/" + os.path.dirname(tmp_grade_file) + "/"
    tokens = glob.glob( os.path.dirname(instructor_grade_script) + "/*.token" )
    for t in tokens:
        print("Source image produced token", t)
    elapsed = time.time() - start
    print("Elapsed time is", elapsed, f"({init=} seconds)")
    return tokens[0]
