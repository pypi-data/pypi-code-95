import static_data

dd = static_data.ddragon()

def test_champion_Annie():
    
    assert dd.getChampion("Annie").image[-9:] == "Annie.png"
    assert dd.getChampion(1).image == dd.getChampion("Annie").image
    assert dd.getChampion(1).name == "Annie"
    assert dd.getChampion("Annie").id == "1"
    
    
def test_champion_Pyke():
    
    assert dd.getChampion("Pyke").image[-8:] == "Pyke.png"
    assert dd.getChampion(555).image == dd.getChampion("Pyke").image
    assert dd.getChampion(555).name == "Pyke"
    assert dd.getChampion("Pyke").id == "555"
    
    
# I'm not a champion
def test_no_champion():
    try:
        dd.getChampion("Canisback")
    except:
        assert True