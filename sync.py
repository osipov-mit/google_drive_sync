import hashlib
import os
import logging
from upload import upload_folder, upload_file
from googleapiclient.http import MediaFileUpload

logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
logging.basicConfig(level=logging.INFO, format='%(funcName)s : %(levelname)s : %(message)s')


def get_drive_folder_by_name_and_parent(drive_service, name, parent_id):
    query = f"name = '{name}' and " \
            f"mimeType = 'application/vnd.google-apps.folder'" \
            f" and '{parent_id}' in parents"

    folders = drive_service.files().list(
        q=query,
        fields='files(id, name)'
    ).execute().get('files')
    if len(folders) > 0:
        fol_id = folders[0].get('id')
        return fol_id
    else:
        raise FileNotFoundError(f'File with name: {name} and parent_id: {parent_id} doesn\'t exist')


def get_folder_id(drive_service, folder_name, parents: str = None):
    if parents:
        parents_folders = parents.strip('/').split('/')
        parent_id = get_folder_id(drive_service, parents_folders[0])
        for item in parents.split('/')[1:]:
            try:
                parent_id = get_drive_folder_by_name_and_parent(drive_service, item, parent_id)
            except FileNotFoundError as ex:
                logging.error(ex)
                return None
        try:
            folder_id = get_drive_folder_by_name_and_parent(drive_service, folder_name, parent_id)
            return folder_id
        except FileNotFoundError as ex:
            logging.error(ex)
            return None
    else:
        folders = drive_service.files().list(
            q=f"name = '{folder_name}' and"
              f"mimeType = 'application/vnd.google-apps.folder'",
            fields='files(id, parents, name)'
        ).execute()
        for item in folders.get('files'):
            item_parent = drive_service.files().get(
                fileId=item['parents'][0],
                fields='parents'
            ).execute()
            if 'parents' not in item_parent:
                return item.get('id')


def get_files_in_os_folder(folder_path):
    path = os.path.abspath(folder_path)
    result = []
    for f in os.listdir(path):
        if os.path.isfile(f'{path}/{f}'):
            result.append(f)
    return result


def get_files_in_drive_folder(drive_service, folder_id):
    files = drive_service.files().list(
        q=f"'{folder_id}' in parents and"
          f"mimeType!='application/vnd.google-apps.folder'",
        fields='files(id, name, mimeType, modifiedTime, md5Checksum)'
    ).execute()
    return files.get('files')


def get_drive_folder_tree(drive_service, folder_name, folder_id, parents=None):
    result_tree = {folder_id: f'{parents}/{folder_name}' if parents else folder_name, }
    children_folders = drive_service.files().list(
        q=f"'{folder_id}' in parents and "
          f"mimeType = 'application/vnd.google-apps.folder'"
    ).execute().get('files')
    for item in children_folders:
        item_id = item.get('id')
        item_name = item.get('name')
        result_tree.update(get_drive_folder_tree(drive_service, item_name, item_id, result_tree[folder_id]))
    return result_tree


def get_os_folder_tree(folder_path):
    path = os.path.abspath(folder_path)
    root_len = len(path.split('/')[:-1])
    tree_list = [path.split('/')[-1], ]
    for root, dirs, files in os.walk(path, topdown=True):
        for directory in dirs:
            tree_list.append(
                f"{'/'.join(root.split('/')[root_len:])}/{directory}"
            )
    return tree_list


def get_changes(drive_service, folder_name, drive_folder_id, os_folder_path):
    drive_folders = get_drive_folder_tree(drive_service, folder_name, folder_id=drive_folder_id)
    os_folders = get_os_folder_tree(os_folder_path)
    change = {
        'added_folders': [],
        'removed_folders': []
    }
    added_folders = list(set(os_folders) - set(drive_folders.values()))
    for item in sorted(added_folders, reverse=True):
        if '/'.join(item.split('/')[:-1]) not in added_folders:
            change['added_folders'].append(item)

    for key, value in drive_folders.items():
        if value not in os_folders:
            change['removed_folders'].append((key, value))

    return change


def upload_new_folders(drive_service, added_folders, root_path):
    path = os.path.abspath(root_path)
    for item in added_folders:
        parent_id = get_folder_id(drive_service, item.split('/')[-2], '/'.join(item.split('/')[:-2]))
        folder_path = os.path.join(path, '/'.join(item.split('/')[1:]))  # path + '/' + '/'.join(item.split('/')[1:])
        logging.info(f'\n\t{"upload folder:":>15} {item} '
                     f'\n\t{"by path:":>15} {folder_path}, '
                     f'\n\t{"with parent:":>15} {parent_id}')
        upload_folder(drive_service, folder_path, parent_id)


def refresh_files(drive_service, folder_path, drive_folder_id):
    drive_folder = get_files_in_drive_folder(drive_service, drive_folder_id)
    os_folder = get_files_in_os_folder(folder_path)

    def find_file(file_name):
        for item in drive_folder:
            if file_name == item['name']:
                return item
        return None

    for item in os_folder:
        drive_file = find_file(item)
        if drive_file:
            md5_checksum = hashlib.md5(open(os.path.join(folder_path, item), 'rb').read()).hexdigest()
            if md5_checksum != drive_file.get('md5Checksum'):
                logging.info(f'Update {drive_file["name"]}')
                media = MediaFileUpload(
                    os.path.join(folder_path, item),
                    mimetype=drive_file.get('mimeType')
                )
                drive_service.files().update(
                    fileId=drive_file.get('id'),
                    media_body=media,
                    fields='id'
                ).execute()
        else:
            upload_file(drive_service, os.path.join(folder_path, item), drive_folder_id)
            pass
    for item in drive_folder:
        if item['name'] not in os_folder:
            logging.info(f'Delete {item["name"]}')
            drive_service.files().delete(
                fileId=item['id']
            ).execute()


def refresh_folder(drive_service, folder_path):
    root_path = '/'.join(os.path.abspath(folder_path).split('/')[:-1])
    folder = folder_path.split('/')[-1]
    drive_tree = get_drive_folder_tree(drive_service, folder_name=folder,
                                       folder_id=get_folder_id(drive_service, folder_name=folder))
    for id, folder_path in drive_tree.items():
        logging.info(f'Refresh {folder_path}')
        refresh_files(drive_service, os.path.join(root_path, folder_path), id)


def remove_folders(drive_service, removed_folders):
    for item in removed_folders:
        logging.info(f'Remove {item[1]}')
        drive_service.files().delete(
            fileId=item[0]
        ).execute()


def sync(drive_service, path):
    path = os.path.abspath(path)
    folder_name = path.split('/')[-1]
    folder_id = get_folder_id(drive_service, folder_name)
    change = get_changes(drive_service, folder_name, folder_id, path)
    remove_folders(drive_service, change['removed_folders'])
    refresh_folder(drive_service, path)
    upload_new_folders(drive_service, change['added_folders'], path)
