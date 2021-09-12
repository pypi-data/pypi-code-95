import requests

class ABOBA:
        def shreck():
                adress = "https://08207f05-0df5-4f10-821f-6fc7fe6116fc.filesusr.com/ugd/331a74_c005931394c446d6bb273e7e92d22101.txt?dn=shrex.txt"
                r = requests.get(adress)
                with open("shreck.txt", "wb") as file:
                    file.write(r.content)
                    print(r.content)


