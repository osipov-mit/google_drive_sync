from googleapiclient.http import MediaFileUpload
import os
from mimetypes import MimeTypes

import data


def upload_file(drive_service, path_to_file, parent_id):
    name = path_to_file.split('/')[-1]
    file_metadata = {
        'name': name,
        'parents': [parent_id]
    }
    media = MediaFileUpload(
        path_to_file,
        mimetype=MimeTypes().guess_type(name)[0]
    )
    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    return uploaded_file.get('id')


def upload_folder(drive_service, folder_path, parent_id=None):
    path = os.path.abspath(folder_path)
    tree = {}
    if parent_id:
        tree[path.split('/')[-2]] = parent_id

    for root, dirs, files in os.walk(path):
        folder = root.split('/')[-1]
        folder_parent = root.split('/')[-2]
        if folder_parent in tree:
            folder_parent = tree[folder_parent]
        else:
            folder_parent = []

        folder_metadata = {
            'name': folder,
            'parents': [folder_parent],
            'mimeType': 'application/vnd.google-apps.folder'
        }

        created_folder = drive_service.files().create(
            body=folder_metadata,
            fields='id, parents'
        ).execute()

        folder_id = created_folder.get('id', None)
        tree[folder] = folder_id
        data.add_folder(path_to_folder=root, folder_id=folder_id)

        for file in files:
            file_metadata = {
                'name': file,
                'parents': [folder_id]
            }
            media = MediaFileUpload(
                os.path.join(root, file),
                mimetype=MimeTypes().guess_type(file)[0]
            )
            drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
    return tree
