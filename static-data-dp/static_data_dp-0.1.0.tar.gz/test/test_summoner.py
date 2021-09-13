import static_data

dd = static_data.ddragon()

def test_summoner_flash():
    
    assert dd.getSummoner("Flash").image[-17:] == 'SummonerFlash.png'
    assert dd.getSummoner(4).image == dd.getSummoner("Flash").image
    assert dd.getSummoner(4).name == "Flash"

def test_summoner_ignite():
    
    assert dd.getSummoner("Ignite").image[-15:] == 'SummonerDot.png'
    assert dd.getSummoner(14).image == dd.getSummoner("Ignite").image
    assert dd.getSummoner(14).name == "Ignite"
    
# I'm not a summoner spell
def test_no_summoner():
    try:
        dd.getSummoner("Canisback")
    except:
        assert True