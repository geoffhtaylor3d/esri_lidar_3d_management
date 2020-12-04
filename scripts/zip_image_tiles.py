import zipfile
import os

# User inputs
in_directory = r'imagery'
out_directory = r'imagery_zipped'


# Constants - DO NOT MODIFY
supported_folder_extensions = ['gdb']

# Begin Script


def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def zipper(in_list, out_file_path):
    out_file = '{0}.zip'.format(out_file_path)
    ensure_dir(out_file)
    with zipfile.ZipFile(out_file, 'w') as zipMe:
        for f in in_list:
            zipMe.write(f, compress_type=zipfile.ZIP_DEFLATED)


def zipper_gdb(in_gdb, out_file_name):
    assert in_gdb.endswith('.gdb'), "Error: file extension {0} not detected in in_folder".format(".gdb")
    root_dir = os.path.dirname(in_gdb)
    gdb_name = os.path.basename(in_gdb)
    myzip = zipfile.ZipFile(os.path.join(root_dir, out_file_name), 'w', zipfile.ZIP_DEFLATED)
    for folder, subfolder, file in os.walk(os.path.join(root_dir, gdb_name)):
        for each in subfolder + file:
            source = os.path.join(folder, each)
            if not source.endswith(".lock"):
                # remove the absolute path to compose arcname
                # also handles the remaining leading path separator with lstrip
                arcname = source[len(root_dir):].lstrip(os.sep)
                # write the file under a different name in the archive
                myzip.write(source, arcname=arcname)
    myzip.close()


def zip_folder(in_folder, out_file_name):
    myzip = zipfile.ZipFile(os.path.join(in_folder, out_file_name), 'w', zipfile.ZIP_DEFLATED)
    for folder, subfolder, file in os.walk(in_folder):
        for each in subfolder + file:
            source = os.path.join(folder, each)
            # remove the absolute path to compose arcname
            # also handles the remaining leading path separator with lstrip
            arcname = source[len(in_folder):].lstrip(os.sep)
            # write the file under a different name in the archive
            myzip.write(source, arcname=arcname)
    myzip.close()


# TODO: do something with folder-based file structures. ex: GDB .... user the zipper_folder_structure() function above.

file_name_list = []
files_to_zip = []
for root, dirs, files in os.walk(in_directory):
    for filename in files:
        file = os.path.join(root, filename)
        file_partitioned = filename.partition('.')[0]
        if file_partitioned not in file_name_list:
            if len(files_to_zip) > 1:
                out_file_path = files_to_zip[0].replace(in_directory, out_directory).partition('.')[0]
                zipper(files_to_zip, out_file_path)
                files_to_zip = []
            file_name_list.append(file_partitioned)
        else:
            files_to_zip.append(file)
