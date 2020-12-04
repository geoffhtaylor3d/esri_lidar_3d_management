import zipfile
import os

# User inputs
in_directory = r'imagery'
out_directory = r'imagery_zipped'

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


def zipper_gdb(in_folder, out_file_path):
    assert in_folder.endswith('.gdb'), "Error: file extension {0} not detected in in_folder".format(".gdb")
    out_file = '{0}'.format(out_file_path)
    ensure_dir(out_file)
    with zipfile.ZipFile(out_file, 'w') as zipMe:
        for root, dirs, files in os.walk(in_folder):
            for f in files:
                if not f.endswith('.lock'):
                    zipMe.write(os.path.join(root, f))


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
