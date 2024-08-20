import os

import requests
import json
import hashlib

import urllib.parse

import threading

"""
Information:

hash: sha1
minecraft: 1.20.1

Environment Variable:

-- Prism --
$INST_NAME
$INST_ID
$INST_DIR
$INST_MC_DIR
$INST_JAVA
$INST_JAVA_ARGS


"""


# noinspection PyDefaultArgument
def scan_folder(folder: str, ignored: list = []) -> dict:
    """
    :param folder: Path to scan
    :param ignored: file and folder to ignore from initial folder
    :return: hash of file and his path exemple:{HASH: PATH, ...}
    """

    if ignored is None:
        ignored = []
    output = {}

    for i in os.listdir(folder):
        if i in ignored:
            continue
        file = os.path.join(folder, i)
        if os.path.isfile(file):
            hash_sha1 = hashlib.sha1(open(file, 'rb').read()).hexdigest()
            output[hash_sha1] = file
        else:
            folder_data = scan_folder(file)
            for j in folder_data:
                output[j] = folder_data[j]
    return output

def rearrange(data: list, key: str) -> dict:
    """
    :param data: list to rearrange
    :param key: key to rearrange to
    :return: dict of the rearranged list exemple: [{A: X}, {A:Y}] -> {X:{A:X}, Y:{A:Y}}
    """
    output = {}

    for i in data:
        output[i[key]] = i
    return output

def download(url: str, path):
    try:
        with open(path, 'wb+') as files:
            files.write(requests.get('/'.join(url.split('/')[:3]) + '/' + urllib.parse.quote('/'.join(url.split('/')[3:]))).content)
        print('File Downloaded:', os.path.split(path)[-1])
    except Exception as e:
        print('Something fucked up here in download() ! :', e)


class Main:
    def __init__(self):
        print("""
        Script made by jojoblackfr
        
        """)


        self.Manifest_Url = "http://launcher.epicexplorers.fr/files/"

        print(' ----- Requesting Instance Information ----- ')
        self.Instance = json.loads(requests.get(self.Manifest_Url).content)
        self.Ignored = self.Instance['EpicExplorers']['ignored'] + ['icon.png']
        self.Url = self.Instance['EpicExplorers']['url']

        print(' ----- Requesting Files Manifest ----- ')
        self.Server_Files = json.loads(requests.get(self.Url).content)
        self.Server_Hash = rearrange(self.Server_Files, 'hash')

        print(' ----- Scanning Local Files ----- ')
        self.Path = os.environ['INST_MC_DIR']
        self.Local = scan_folder(self.Path, ignored=self.Ignored)

    # Don't ask how I know that, I just know
        self.To_Remove = [hash_str for hash_str in self.Local if hash_str not in self.Server_Hash]
        self.To_Download = [hash_str for hash_str in self.Server_Hash if hash_str not in self.Local]

        self.Thread = {}

        print(' ----- Removing Unwanted Files ----- ')
        self.Remove()

        print(' ----- Downloading Missing Files ----- ')
        self.Download()

        print(' ----- Verifying File Integrity ----- ')
        self.Verify()


    def Verify(self):
        out = []

        for files in self.Server_Files:
            path = os.path.join(self.Path, files['path'])
            file_hash = files['hash']

            if os.path.exists(path):
                if file_hash != hashlib.sha1(open(path, 'rb').read()).hexdigest():
                    out.append(self.Server_Hash[file_hash])

        if out:
            print(os.path.join(self.Path, out[0]['path']))
            for i in out:
                print(i['url'], urllib.parse.quote(i['url']))
            print(out)
            raise Exception('Something FUCKED UP with ... idk, try figuring out yourself')
        else:
            print(' ----- Verification Completed ----- ')
            return True

    def Download(self):
        for files in self.To_Download:
            total_path = os.path.join(self.Path, self.Server_Hash[files]['path'])
            if not os.path.exists('/'.join(total_path.split('/')[:-1])):
                os.makedirs('/'.join(total_path.split('/')[:-1]))

            self.Thread[files] = threading.Thread(target=download, args=(self.Server_Hash[files]['url'], total_path))

        for thread in self.Thread:
            self.Thread[thread].start()
        for thread in self.Thread:
            self.Thread[thread].join()

        print(' ----- All File Downloaded ----- ')

    def Remove(self):
        for files in self.To_Remove:
            print('Removing:', os.path.split(self.Local[files])[-1])
            os.remove(self.Local[files])
        print(' ----- All Unwanted file Deleted ----- ')


main = Main()
