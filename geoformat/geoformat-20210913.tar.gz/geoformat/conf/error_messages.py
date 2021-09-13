# python version
python_inferior_to_3_7_forbidden = "you must have a version of python higher or equal to 3.7 to execute this function"

# driver
import_lib_error = "cannot run this function ! {lib} library not installed"
import_ogr_error = import_lib_error.format(lib='Python-gdal')
import_psycopg2_error = import_lib_error.format(lib='psycopg2')
import_pyproj_error = import_lib_error.format(lib='pyproj')

# path
path_not_valid = "path : {path} is not valid"
path_not_valid_file_exists_overwrite_is_false = "path : {path} exists."

# fields
missing_field = "field : {field_name} does not exists in geolayer"

# values

# non unique value
non_unique_values = "field : {field_name} contains non-unique values"
