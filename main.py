import argparse
from connection import get_drive_service, set_client_secret_files, get_path_to_client_secret_file
from sync import sync
from upload import upload_folder

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Google Drive Synchronization')
    parser.add_argument('--sync',  help='Enter path to folder to synchronize')
    parser.add_argument('--upload', help='Enter path to folder for uploading')
    parser.add_argument('--set_secret_file', help='Enter path to client_secret_file')

    args = parser.parse_args()
    if args.sync:
        service = get_drive_service()
        sync(service, args.sync)
    elif args.upload:
        service = get_drive_service()
        upload_folder(service, args.upload)
    elif args.set_secret_file:
        set_client_secret_files(args.set_secret_file)
    else:
        pass
