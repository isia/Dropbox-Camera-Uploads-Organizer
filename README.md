# Dropbox Camera Uploads Organizer
a simple python script that organizes files in the [Dropbox](http://dropbox.com) "Camera Uploads" folder into year, month, and (optionally) day subdirectories

Scans through source directory and subdirectories, and moves files whose names match the dropbox camera upload naming convention. Moves each matching file into corresponding year and month subdirectories within the given destination directory.

#### Arguments
    db_location: Location of the 'Dropbox' directory. Defaults to standard 'Dropbox' Folder location '~/Dropbox'
    destination: Directory where the files will be organized to. Must be under your Dropbox directory.
    camera_uploads: location of "Camera Uploads" folder to organize within Dropbox. Defaults to standard.
    by_day: If True, organizes images into day subdirectories under each month directory. Otherwise, images will be stored in month directories. Defaults to True.

#### Todo
set up command line argument parsing

#### File Naming Convention:
    'YYYY-MM-DD HH.MM.SS-V.ext'
    where YYYY is year, MM is month, DD is day, HH is hour in 24-hour format, MM is minute,  SS is seconds, and ext is file extension.
    The '-V' portion only appears when more than one photo is taken within the same second, where the V is a digit denoting the order in which these intra-second pictures were taken
