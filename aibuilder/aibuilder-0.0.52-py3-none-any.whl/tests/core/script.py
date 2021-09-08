import subprocess


def main(keyvault, name):
    return f"D:\\fix_content_type.ps1 {keyvault} {name}"


file_path = "D:\\key_vault_info.csv"

with open(file_path) as f:
    for line in f.readlines():
        line = line.strip()
        keyvault, name = line.split(",")
        keyvault = keyvault.strip()
        name = name.strip()
        result = main(keyvault, name)
        print(result)
