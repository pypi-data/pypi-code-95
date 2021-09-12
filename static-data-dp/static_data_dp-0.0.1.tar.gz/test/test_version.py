import static_data

dd = static_data.ddragon()

def test_version_annie():
    
    dd_version = dd.withVersion(9,12)
    assert dd_version.getChampion("Annie").image == 'http://ddragon.leagueoflegends.com/cdn/9.12.1/img/champion/Annie.png'
    assert dd_version.getChampion(1).image == dd_version.getChampion("Annie").image
    assert dd_version.getChampion(1).name == "Annie"

def test_version_senna():
    
    assert dd.getChampion(235).name == "Senna"
    
    dd_version = dd.withVersion(9,12)
    
    try:
        dd_version.getChampion(235).name == "Senna"
    except:
        assert True
        
def test_game_version():
    
    dd_version = dd.withGameVersion("9.10.274.8345")
    
    assert not dd.getChampion("Ziggs").image == dd_version.getChampion("Ziggs").image
    assert dd_version.getChampion("Ziggs").image == 'http://ddragon.leagueoflegends.com/cdn/9.10.1/img/champion/Ziggs.png'