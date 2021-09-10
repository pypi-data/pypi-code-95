import rsa
import os
import pickle
from dataclasses import dataclass, field
from gitlab_kaban_report.constants import HERE


@dataclass
class EncryptRSA:
    public: str = field(init=False, repr=False, default="")
    private: str = field(init=False, repr=False, default="")

    def get_keys(self) -> None:
        files = os.listdir(HERE)
        if "rsa_id" not in files:
            public_key, private_key = rsa.newkeys(512)
            with open(os.path.join(HERE, "rsa_id"), "wb") as f:
                pickle.dump(private_key, f)
                self.private = private_key
            
            with open(os.path.join(HERE, "rsa_id.pub"), "wb") as f:
                pickle.dump(public_key, f)
                self.public = public_key
        else:
            with open(os.path.join(HERE, "rsa_id"), "rb") as f:
                self.private = pickle.load(f)
            
            with open(os.path.join(HERE, "rsa_id.pub"), "rb") as f:
                self.public = pickle.load(f)

    def encrypt(self, string: str) -> bytes:
        self.get_keys()
        return rsa.encrypt(string.encode(), self.public)

    def decrypt(self, string: bytes) -> str:
        self.get_keys()
        return rsa.decrypt(string, self.private).decode()
