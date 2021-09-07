import requests
from bs4 import BeautifulSoup


def ekstraksi_data():
    """
    Tanggal: 02 September 2021
    Waktu: 07:22:36 WIB
    Magnitudo: 2.7
    Kedalaman: 13 km
    Lokasi: LS=4.01 BT=122.49
    Pusat Gempa: Pusat gempa berada di darat 2.8 Km BaratLaut Baruga
    Dirasakan (Skala MMI): II Kendari
    :return:
    """

    try:
        content = requests.get("https://bmkg.go.id")
    except Exception:
        return None

    if content.status_code == 200:
        soup = BeautifulSoup(content.text, "html.parser")

        result = soup.find("div", {"class": "col-md-6 col-xs-6 gempabumi-detail no-padding"})
        result = result.findChildren("li")

        i = 0
        tanggal = None
        waktu = None
        magnitudo = None
        kedalaman = None
        ls = None
        bt = None
        pusat_gempa = None
        dirasakan = None

        for res in result:
            if i == 0:
                date = res.text.split(", ")
                tanggal = date[0]
                waktu = date[1]
            if i == 1:
                magnitudo = res.text
            elif i == 2:
                kedalaman = res.text
            elif i == 3:
                koordinat = res.text.split(" - ")
                ls = koordinat[0]
                bt = koordinat[1]
            elif i == 4:
                pusat_gempa = res.text
            elif i == 5:
                dirasakan = res.text
            i += 1

        hasil = dict()
        hasil["tanggal"] = tanggal
        hasil["waktu"] = waktu
        hasil["magnitudo"] = magnitudo
        hasil["kedalaman"] = kedalaman
        hasil["lokasi"] = {"ls": ls, "bt": bt}
        hasil["pusat_gempa"] = pusat_gempa
        hasil["dirasakan"] = dirasakan

        return hasil

    else:
        return None


def tampilkan_data(result):
    if result is None:
        print("Tidak dapat menampilkan data gempa terkini")
        return

    print("Gempa Terakhir Berdasarkan BMKG")
    print(f"Tanggal : {result['tanggal']}")
    print(f"Waktu : {result['waktu']}")
    print(f"Magnitudo : {result['magnitudo']}")
    print(f"Kedalaman : {result['kedalaman']}")
    print(f"Lokasi : {result['lokasi']['ls']}, {result['lokasi']['bt']}")
    print(f"Pusat Gempa : {result['pusat_gempa']}")
    print(f"Dirasakan : {result['dirasakan']}")


if __name__ == "__main__":
    result = ekstraksi_data()
    tampilkan_data(result)
