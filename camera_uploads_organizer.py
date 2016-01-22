# import argparse
import logging
import os
import re


# todo: set up argument parsing
# parser = argparse.ArgumentParser(description='')


def organize_camera_uploads(db_location='~\Dropbox\\', destination='Photos\By Date', camera_uploads='Camera Uploads',
                            by_day=True):
    """ Organizes the Dropbox 'Camera Uploads' Folder

    Scans through source directory and subdirectories,
    and moves files whose names match the dropbox camera upload naming convention.
    Moves each matching file into corresponding year and month subdirectories within the given
    destination directory.

    The destination directory

    Naming Convention:
    'YYYY-MM-DD HH.MM.SS-V.ext' where YYYY is year, MM is month, DD is day,
    HH is hour in 24-hour format, MM is minute,  SS is seconds, and ext is file extension.
    The '-V' portion only appears when more than one photo is taken within the same second,
    where the V is a digit denoting the order in which these intra-second pictures were taken)

    Args:
        destination: directory where the files will be organized to. If not an absolute path, will be treated as subdirectory of db_location
        db_location: location of the 'Dropbox' directory. Defaults to standard 'Dropbox' Folder location '~/Dropbox'
        camera_uploads: location of 'Camera Uploads' folder to organize within Dropbox. Defaults to standard.
        by_day: if True, organizes images into day subdirectories under each month directory

    Returns:
        bool: False if  'Camera Uploads' directory could not be found or at least one matching file could not be moved

    """

    # verify argument types
    if not type(destination) is str \
            or not type(db_location) is str \
            or not type(camera_uploads) is str \
            or not type(by_day) is bool:
        raise TypeError

    # region setup and format the path variables

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

    # endregion

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
            match = re.compile('^(\d{4})-(\d{2})-(\d{2}) (\d{2})\.(\d{2})\.(\d{2})(-\d*)?\.(.{3,})$').match(filename)
            if match is None:
                continue

            # build destination path
            new_path = os.path.join(destination_directory,
                                    match.group(1),  # extract year from file name (i.e. 2015)
                                    match.group(2),  # extract month from file name (i.e. 04)
                                    match.group(3),  # extract day from file name (i.e. 13)
                                    filename)

            new_path = os.path.join(new_path, filename)
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

    return complete_success


# run the function with default arguments
success = organize_camera_uploads()

if success:
    print 'completed successfully'
else:
    print 'completed with some errors'

raw_input('press return to close...')
