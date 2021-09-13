import static_data

dd = static_data.ddragon()

def test_icon_1():
    assert dd.getIcon(1).image[-5:] == "1.png"
    assert dd.getIcon(1).name is None

def test_icon_666():
    assert dd.getIcon(666).image[-7:] == "666.png"
    assert dd.getIcon(666).name is None

def test_icon_placeholder():
    assert dd.getIcon("placeholder").image[-15:] == "placeholder.png"
    assert dd.getIcon("placeholder").name is None
    
    
# I'm not an icon
def test_no_icon():
    try:
        dd.getIcon("Canisback")
    except:
        assert True