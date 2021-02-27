import os
import pickle
from pprint import pprint as pp
import logging

logging.basicConfig(level=logging.INFO, format='%(funcName)s : %(levelname)s : %(message)s')


def is_root(func):
    def wrapper(*args, **kwargs):
        karguments = {}
        if 'path_to_folder' in kwargs.keys():
            karguments['path_to_folder'] = kwargs['path_to_folder']
        else:
            karguments['path_to_folder'] = args[0]

        if 'folder_id' in kwargs.keys():
            karguments['folder_id'] = kwargs['folder_id']
        elif len(args) > 1:
            karguments['folder_id'] = args[1]

        if karguments['path_to_folder'] != 'drive_root':
            karguments['path_to_folder'] = os.path.abspath(karguments['path_to_folder'])
        return func(**karguments)

    return wrapper


@is_root
def add_folder(path_to_folder, folder_id):
    if os.path.exists('folders.pickle'):
        data = pickle.load(open('folders.pickle', 'rb'))
        if path_to_folder not in data.keys():
            data[path_to_folder] = folder_id
        else:
            print(f'Folder with the path: "{path_to_folder}" already exists.\n'
                  f'Do you want to change id of this folder on drive (y/n)?')
            if input().startswith('y'):
                data[path_to_folder] = folder_id
            else:
                return None
        pickle.dump(data, open('folders.pickle', 'wb'))
    else:
        data = {
            path_to_folder: folder_id
        }
        pickle.dump(data, open('folders.pickle', 'wb'))


@is_root
def get_folder(path_to_folder):
    if os.path.exists('folders.pickle'):
        data = pickle.load(open('folders.pickle', 'rb'))
        if path_to_folder in data.keys():
            return data[path_to_folder]
        else:
            raise ValueError(f'Folder with the path: "{path_to_folder}" does not exist in the added folders.')
    else:
        raise FileExistsError(f'File "folders.pickle" with data about the added folders does not exist')


def add_root(root_id):
    add_folder('drive_root', folder_id=root_id)


def get_root():
    try:
        root_id = get_folder('drive_root')
    except ValueError as ex:
        root_id = None

    return root_id


def get_all_folders():
    folders = pickle.load(open('folders.pickle', 'rb'))
    return folders


