import string, os
from pathlib import Path
class Encryption:
    def __init__(self, path):
        if path.endswith("enc") or path.endswith("ENC"):
            raise ValueError("File is already encrypted.")
        else:
            self.__path = path
            if not os.path.exists(f"{Path(path).parent}/Encrypted"):
                os.makedirs(f"{Path(path).parent}/Encrypted", exist_ok=True)
            self.__Folder = f"{Path(path).parent}/Encrypted"

    def ceaser_encrypt(self):
        with open(self.__path, "r", encoding="utf-8") as f:
            text = f.read()
            translation = str.maketrans(string.ascii_letters, "".join(sorted(string.ascii_letters, reverse= True)))
            enc_text = text.translate(translation)

        new_file_path = Path(self.__Folder) / (Path(self.__path).stem + ".enc")
        with open(new_file_path, "w", encoding="utf-8") as f:
            f.write(enc_text)
class Decryption():
    def __init__(self, path, suffix="text"):
        if not path.endswith("ENC") or not path.endswith("enc"):
            raise ValueError("File is not encrypted.")
        else:
            self.__path = path
            self._suffix = suffix

    def ceaser_decrypt(self):
        with open(self.__path, "r", encoding="utf-8") as f:
            text = f.read()
            translation = str.maketrans("".join(sorted(string.ascii_letters, reverse= True)), string.ascii_letters)
            dec_text = text.translate(translation)

        new_file_path = Path(self.__path).parents[1] / (Path(self.__path).stem + self._suffix)
        print(new_file_path)
        with open(new_file_path, "w", encoding="utf-8") as f:
            f.write(dec_text)