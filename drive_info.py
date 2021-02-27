def get_drive_root_id(drive_service):
    folders = drive_service.files().list(
        q=f"mimeType = 'application/vnd.google-apps.folder'",
        fields='files(id, name, parents)'
    ).execute()

    for item in folders.get('files'):
        item_parent = drive_service.files().get(
            fileId=item['parents'][0],
            fields='id, name, parents'
        ).execute()
        if 'parents' not in item_parent:
            root_id = item_parent.get('id')
            return root_id


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


# def get_drive_folder_by_name_and_parent(drive_service, name, parent_id):
#     query = f"name = '{name}' and " \
#             f"mimeType = 'application/vnd.google-apps.folder'" \
#             f" and '{parent_id}' in parents"
#
#     folders = drive_service.files().list(
#         q=query,
#         fields='files(id, name)'
#     ).execute().get('files')
#     if len(folders) > 0:
#         fol_id = folders[0].get('id')
#         return fol_id
#     else:
#         raise FileNotFoundError(f'File with name: {name} and parent_id: {parent_id} doesn\'t exist')


# def get_folder_id(drive_service, folder_name, parents: str = None):
#     if parents:
#         parents_folders = parents.strip('/').split('/')
#         parent_id = get_folder_id(drive_service, parents_folders[0])
#         for item in parents.split('/')[1:]:
#             try:
#                 parent_id = get_drive_folder_by_name_and_parent(drive_service, item, parent_id)
#             except FileNotFoundError as ex:
#                 logging.error(ex)
#                 return None
#         try:
#             folder_id = get_drive_folder_by_name_and_parent(drive_service, folder_name, parent_id)
#             return folder_id
#         except FileNotFoundError as ex:
#             logging.error(ex)
#             return None
#     else:
#         folders = drive_service.files().list(
#             q=f"name = '{folder_name}' and"
#               f"mimeType = 'application/vnd.google-apps.folder'",
#             fields='files(id, parents, name)'
#         ).execute()
#         for item in folders.get('files'):
#             item_parent = drive_service.files().get(
#                 fileId=item['parents'][0],
#                 fields='parents'
#             ).execute()
#             if 'parents' not in item_parent:
#                 return item.get('id')