import static_data

dd = static_data.ddragon()

def test_rune_hail():
    
    assert dd.getRune(9923).image[-16:] == 'HailOfBlades.png'
    assert dd.getRune(9923).image == dd.getRune('Hail of Blades').image
    assert dd.getRune(9923).name == 'Hail of Blades'

def test_rune_aftershock():
    
    assert dd.getRune(8439).image[-21:] == 'VeteranAftershock.png'
    assert dd.getRune(8439).image == dd.getRune('Aftershock').image
    assert dd.getRune(8439).name == 'Aftershock'
    
# I'm not a rune
def test_no_rune():
    try:
        dd.getRune("Canisback")
    except:
        assert True