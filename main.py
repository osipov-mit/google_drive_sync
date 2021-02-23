import argparse
from connection import get_credentials, get_drive_service
from sync import sync

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Google Drive Synchronization')
    parser.add_argument('--sync',  help='Enter path to folder to synchronizate')
    parser.add_argument('--upload', help='Enter path to folder for uploading')

    args = parser.parse_args()
    if args.sync:
        credentials = get_credentials()
        service = get_drive_service(credentials)
        sync(service, args.sync)
    elif args.upload:
        print('upload')
    else:
        print('nothing')



