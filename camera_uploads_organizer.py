import argparse
import logging
import os
import re

DEST_PATH_FORMAT_FULL='full'
DEST_PATH_FORMAT_MO='month_only'
DEST_PATH_FORMAT_SHORT='short'


def organize_camera_uploads(db_location='~\Dropbox\\', destination='Photos\By Date', camera_uploads='Camera Uploads',
                            destination_format='full', do_clean=False):
    """ Organizes the Dropbox 'Camera Uploads' Folder

    Scans through source directory and subdirectories,
    and moves files whose names match the dropbox camera upload naming convention.
    Moves each matching file into corresponding year and month subdirectories within the given
    destination directory.

    Args:
        destination: directory where the files will be organized to. If not an absolute path, will be treated as
            subdirectory of db_location
        db_location: location of the 'Dropbox' directory. Defaults to standard 'Dropbox' Folder location '~/Dropbox'
        camera_uploads: location of 'Camera Uploads' folder to organize within Dropbox. Defaults to standard.
        destination_format: TODO: description
        do_clean: if True, deletes empty directories contained under the destination path

    Returns:
        bool: False if at least one matching file could not be moved

    """
    # verify argument types
    if not type(destination) is str \
            or not type(db_location) is str \
            or not type(camera_uploads) is str \
            or not type(destination_format) is str:
        raise TypeError

    # expand db_location and destination from ~/ or ~user/ format
    db_location = os.path.expanduser(db_location)
    destination = os.path.expanduser(destination)

    # confirm that the dropbox location exists
    if not os.path.isdir(db_location):
        logging.error('Dropbox directory "' + db_location + '" does not exist')
        raw_input('press return to close...')
        exit(1)

    # if given db_location ends with "/" or "\" characters, remove them
    while True:
        if db_location.endswith('/') or db_location.endswith('\\'):
            db_location = db_location[:-1]
        else:
            break

    # if given db_location does not end with a 'Dropbox' directory, append one
    if not os.path.split(db_location)[1] == 'Dropbox':
        db_location = os.path.join(db_location, 'Dropbox')

    # if destination is an absolute path, check that it a subdirectory of db_location. If it is not, exit
    # if destination is not an absolute path, assume it is a subdirectory of db_location and expand to absolute path
    if os.path.isabs(destination):
        if not destination.startswith(db_location):
            logging.error('given destination path must be a subdirectory within dropbox: "' + destination + '"')
            raw_input('press return to close...')
            exit(1)
    else:
        destination = os.path.join(db_location, destination)

    # if camera_uploads is an absolute path, check that it a subdirectory of db_location. If it is not, exit
    # if camera_uploads is not an absolute path, assume it is a subdirectory of db_location and expand to absolute path
    if os.path.isabs(camera_uploads):
        if not camera_uploads.startswith(db_location):
            logging.error('given camera_uploads path must be a subdirectory within dropbox: "' + camera_uploads + '"')
            raw_input('press return to close...')
            exit(1)
    else:
        camera_uploads = os.path.join(db_location, camera_uploads)

    # confirm that the camera uploads directory exists. If not, exit with warning
    if not os.path.isdir(camera_uploads):
        logging.warn('camera uploads directory does not exist at "' + camera_uploads + '"')
        exit(0)

    # compile camera upload filename pattern for use later
    cam_up_pattern = re.compile(
        r'^(\d{4})-(\d{2})-(\d{2}) (\d{2})\.(\d{2})\.(\d{2})'  # date & time
        r'( HDR)?(-\d+)?( \((.+)\'s conflicted copy \1-\2-\3\))?(-[1-9])?'  # optional bits
        r'\.([^\s]+)$'  # file extension
    )

    dest_path_patterns = {
        DEST_PATH_FORMAT_FULL   : ['{destination_directory}', '{year}', '{month:02d}', '{day:02d}', '{file_name}'],
        DEST_PATH_FORMAT_MO     : ['{destination_directory}', '{year}', '{month:02d}', '{file_name}'],
        DEST_PATH_FORMAT_SHORT  : ['{destination_directory}', '{year}', '{month:02d}.{day:02d}', '{file_name}'],
    }

    # function to recursively remove empty directories under given path
    def clean_empty_directories(path):
        # return None if path is not a directory
        if not os.path.isdir(path):
            return

        # create list of items found in given directory
        path_items = os.listdir(path)

        # if directory is empty, delete it
        if path_items == [] or path_items == ['.dropbox']:
            print '"' + path + '" is empty. Removing...'
            try:
                os.rmdir(path)
            except OSError:
                print 'could not remove "' + path + '"'

        # if directory is not empty, recurse for each item in directory
        else:
            for item in path_items:
                clean_empty_directories(os.path.join(path, item))

    def move_files(source_directory, destination_directory):

        move_success = True  # If a file cannot be moved, this will be set to False

        # cycle through every item in source directory
        for filename in os.listdir(source_directory):

            # build full path for each item
            file_path = os.path.join(source_directory, filename)

            # Recurse for subdirectories and continue to next item
            if os.path.isdir(file_path):

                # If the subdirectory is the destination directory, skip it
                if file_path == destination_directory:
                    continue
                # recurse for subdirectory and assign the subdirectory's success or failure to a boolean
                sub_success = move_files(file_path, destination_directory)

                # If recursion returned False, then this will also return False
                if not sub_success:
                    move_success = False

                # move on to the next item
                continue

            # check that the filename matches the camera upload naming convention. If not, continue
            match = cam_up_pattern.match(filename)
            if match is None:
                continue

            # creating list of path elements for destination
            new_path_data = {'destination_directory' : destination_directory,
                             'year'                  : int(match.group(1)),  # extract year from file name (i.e. 2015)
                             'month'                 : int(match.group(2)),  # extract month from file name (i.e. 04)
                             'day'                   : int(match.group(3)),  # extract day from file name (i.e. 13)
                             'file_name'             : filename,
                             }

            # build destination path
            new_path = (os.path.join(*dest_path_patterns[destination_format])).format(**new_path_data)

            try:
                # perform the move
                os.renames(file_path, new_path)
                print filename, " successfully moved"
            except OSError:
                # if move failed, function will return False
                logging.error('failed to move file: "' + file_path + '" to "' + new_path + '"')
                move_success = False

        return move_success

    # begin moving and assign return value to a boolean
    complete_success = move_files(camera_uploads, destination)

    # remove empty directories
    if do_clean:
        print 'Beginning to search for and remove empty directories'
        clean_empty_directories(destination)

    return complete_success


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dropbox', '-db', action='store', nargs=1, default='~\Dropbox\\', type=str,
                        metavar='"PATH"', dest='db_location', help='Location of the Dropbox directory.')
    parser.add_argument('--destination', '-dst', action='store', nargs=1, default='Photos\By Date', type=str,
                        metavar='"PATH"', help='Location of the destination direction where the files will \
                         be organized. Must be under the Dropbox Directory\' file tree.')
    parser.add_argument('--camera-uploads', '-cu', action='store', nargs=1, default='Camera Uploads', type=str,
                        metavar='"PATH"', help='Location of the source directory. Must be under the \
                        Dropbox directory\'s file tree.')
    parser.add_argument('--destination-format', '-df', choices=[DEST_PATH_FORMAT_FULL,
                                                                DEST_PATH_FORMAT_MO,
                                                                DEST_PATH_FORMAT_SHORT], default=DEST_PATH_FORMAT_FULL,
                        action='store', dest='destination_format', type=str,
                        help='Select one of formats to store destination files.')
    parser.add_argument('--clean', '-cl', action='store_true', dest='do_clean',
                        help="If this flag is present, empty directories under the destination path will be deleted.")

    args = vars(parser.parse_args())

    def safe_list_get (l, idx, default):
        try:
            return l[idx]
        except IndexError:
            return default

    success = organize_camera_uploads(db_location=safe_list_get(args['db_location'], 0, None),
                                      destination=safe_list_get(args['destination'], 0, None),
                                      camera_uploads=args['camera_uploads'],
                                      destination_format=args['destination_format'],
                                      do_clean=args['do_clean'])

    if success:
        print 'completed successfully'
    else:
        print 'completed with some errors'