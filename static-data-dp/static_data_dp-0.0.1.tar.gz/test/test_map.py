import static_data

dd = static_data.ddragon()

def test_map_sr():
    assert dd.getMap(11).image[-9:] == "map11.png"
    assert dd.getMap(11).name == "Summoner's Rift"

def test_map_ha():
    assert dd.getMap(12).image[-9:] == "map12.png"
    assert dd.getMap(12).name == "Howling Abyss"    
    
    
# I'm not a map
def test_no_map():
    try:
        dd.getMap("Canisback")
    except:
        assert True