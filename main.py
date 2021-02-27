import argparse

import connection
import sync
import upload
import data
import drive_info

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Google Drive Synchronization')
    parser.add_argument('--sync', help='Enter path to folder to synchronize')
    parser.add_argument('--upload', help='Enter path to folder for uploading')
    parser.add_argument('--set_secret_file', help='Enter path to client_secret_file')

    args = parser.parse_args()

    if args.set_secret_file:
        connection.set_client_secret_files(args.set_secret_file)
    else:
        service = connection.get_drive_service()
        try:
            root_id = data.get_root()
        except FileExistsError as ex:
            print(f'{ex}\n Continue and create the file (y/n)')
            if input().startswith('y'):
                drive_root_id = drive_info.get_drive_root_id(service)
                data.add_root(drive_root_id)

        if args.sync:
            sync.sync(service, args.sync)
        elif args.upload:
            upload.upload_folder(service, args.upload)
