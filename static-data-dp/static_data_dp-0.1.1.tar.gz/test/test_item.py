import static_data

dd = static_data.ddragon()

def test_item_boots():
    
    assert dd.getItem(1001).image[-8:] == "1001.png"
    assert dd.getItem(1001).name == 'Boots'
    assert dd.getItem("Boots").id == '1001'

def test_item_bfsword():
    
    assert dd.getItem(1038).image[-8:] == "1038.png"
    assert dd.getItem(1038).name == 'B. F. Sword'
    
    
# I'm not an item
def test_no_item():
    try:
        dd.getItem("Canisback")
    except:
        assert True