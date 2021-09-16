import pandas as pd
import evemarkettools as emt
import math

invTypes = emt.fuzz_static_dump()
materials = emt.fuzz_static_dump('https://www.fuzzwork.co.uk/dump/latest/industryActivityMaterials.csv.bz2')
quantities = emt.fuzz_static_dump('https://www.fuzzwork.co.uk/dump/latest/industryActivityProducts.csv.bz2')
# remove all of the test reaction formulas
quantities = pd.merge(quantities, invTypes.loc[invTypes['published'] == 1])[list(quantities.columns)]
probabilities = emt.fuzz_static_dump('https://www.fuzzwork.co.uk/dump/latest/industryActivityProbabilities.csv.bz2')

def input_materials(type_id: int, quantity: int, me: int = 0, prod_type: str = 'manufacturing', prices: bool = False) -> pd.DataFrame:
    """
    Calculates the input materials needed for production (manufacturing or reaction). Uses a single production step
    
    Args:
        type_id: what item to produce
        quantity: how much to produce
        me: material efficiency of the blueprints
        prod_type: what type of production ('reaction' or 'manufacturing')
        prices: whether to calculate prices for the input materials (adds columns price)
        
    Return: 
        returns a pandas dataframe with the columns 'type_id', 'type_name', 'quantity' ('price' if prices = True)
    """
    actID = {'manufacturing': 1, 'reaction': 11}
    mats = pd.DataFrame(columns=['type_id', 'type_name', 'quantity'])
    if type_id in quantities.loc[(quantities['activityID'] == actID[prod_type]) & (quantities['productTypeID'] == type_id)].values:  # item can be manufactured

        if prod_type == 'reaction':
          bpid = productToFormula(type_id)

        elif prod_type == 'manufacturing':
          bpid = productToBP(type_id)
        
        else:  
          raise ValueError("thats not a valid manufacturing type. options are 'reaction', 'manufacturing'")

        qPerRun = quantPerRun(bpid)
        runs = quantity // qPerRun

        if runs > 0:
            for _, row in materials.loc[(materials['activityID'] == actID[prod_type]) & (materials['typeID'] == bpid)].iterrows():

                if prod_type == 'reaction':
                  quant = row['quantity'] * runs

                elif prod_type == 'manufacturing':
                  quant = me_formula(row['quantity'],me) * runs

                mats = mats.append({'type_id': row['materialTypeID'], 'type_name': emt.typeIDToName(row['materialTypeID']), 'quantity': quant}, ignore_index=True)
                
        
        # buys the product instead of manufacturing more of it than needed
        if int(runs * qPerRun) < int(quantity):
            mats = mats.append({'type_id': type_id, 'type_name': emt.typeIDToName(type_id), 'quantity': quantity - (runs * qPerRun)},ignore_index=True)
    
    mats = mats.groupby(['type_id', 'type_name']).sum().reset_index()
    mats = mats.astype({"type_id": int, "quantity": int})

    if prices:
        mats = emt.add_price(mats)

    return mats

def vertical_production(type_id: int, quantity: int, me: int = 0, prod_type: str = 'manufacturing' , prices: bool = False) -> pd.DataFrame:
    """
    Calculates the input materials needed for vertical manufacturing (producing as much as possible)

    Args:
        type_id: type_id of the item to produce
        quantity: how much of the item to produce
        me: material efficiency of the blueprints
        prod_type: what type of production ('reaction' or 'manufacturing')
        prices: whether to calculate the prices for the input materials (additional column 'price')

    Returns:
        returns a dataframe with the columns 'type_id', 'type_name', 'quantity', 'price' (if prices is set to true)
    """
    actID = {'manufacturing': 1, 'reaction': 11}
    mats = pd.DataFrame(columns=['type_id', 'type_name', 'quantity'])

    if type_id in quantities.loc[(quantities['activityID'] == actID[prod_type]) & (quantities['productTypeID'] == type_id)].values:  # item can be manufactured

        if prod_type == 'reaction':
          bpid = productToFormula(type_id)

        elif prod_type == 'manufacturing':
          bpid = productToBP(type_id)
        
        else:  
          raise ValueError("thats not a valid manufacturing type. options are 'reaction', 'manufacturing'")

        qPerRun = quantPerRun(bpid)
        runs = quantity // qPerRun

        if runs > 0:

            for _, row in materials.loc[(materials['activityID'] == actID[prod_type]) & (materials['typeID'] == bpid)].iterrows():

                if prod_type == 'reaction':
                  quant = row['quantity'] * runs

                elif prod_type == 'manufacturing':
                  quant = me_formula(row['quantity'],me) * runs

                mats = mats.append(vertical_production(row['materialTypeID'], quant, prod_type = prod_type) ,ignore_index=True)
                
        
        # buys the product instead of manufacturing more of it than needed
        if int(runs * qPerRun) < int(quantity):
            mats = mats.append({'type_id': type_id, 'type_name': emt.typeIDToName(type_id), 'quantity': quantity - (runs * qPerRun)},ignore_index=True)

    else:  # item cannot be manufactured
        mats = mats.append({'type_id': type_id, 'type_name': emt.typeIDToName(type_id), 'quantity': quantity}, ignore_index=True)

    mats = mats.groupby(['type_id', 'type_name']).sum().reset_index()
    mats = mats.astype({"type_id": int, "quantity": int})

    if prices:
        mats = emt.add_price(mats)

    return mats

def vertical_production_runs(type_id: int, quantity: int, me: int = 10, prod_type: str = 'manufacturing') -> pd.DataFrame:
    """
    Calculates the blueprint/reaction runs needed for vertical manufacturing (producing as much as possible)

    Args:
        type_id: what item/ship to produce
        quantity: how much of the item to produce
        me: material efficiency of the blueprints
        prod_type: what type of production ('manufacturing' or 'reaction')

    Returns:
        returns a dataframe with the columns 'type_id', 'type_name', 'runs'
    """
    actID = {'manufacturing': 1, 'reaction': 11}
    mat_runs = pd.DataFrame(columns=['type_id', 'type_name', 'runs'])

    if type_id in quantities.loc[(quantities['activityID'] == actID[prod_type]) & (quantities['productTypeID'] == type_id)].values:  # item can be manufactured

        if prod_type == 'reaction':
          bpid = productToFormula(type_id)

        elif prod_type == 'manufacturing':
          bpid = productToBP(type_id)
        
        else:  
          raise ValueError("thats not a valid manufacturing type. options are 'reaction', 'manufacturing'")

        qPerRun = quantPerRun(bpid)
        runs = quantity // qPerRun
        if runs > 0:
            mat_runs = mat_runs.append({'type_id': type_id, 'type_name': emt.typeIDToName(type_id), 'runs': runs}, ignore_index=True)
            for _, row in materials.loc[(materials['activityID'] == actID[prod_type]) & (materials['typeID'] == bpid)].iterrows():

                if prod_type == 'reaction':
                  quant = row['quantity'] * runs

                elif prod_type == 'manufacturing':
                  quant = me_formula(row['quantity'],me) * runs

                mat_runs = mat_runs.append(
                    vertical_production_runs(row['materialTypeID'], quant, prod_type = prod_type))

    return mat_runs.reset_index(drop=True)

def invention_probability(type_id: int, rem: int = 5, science1: int = 5, science2: int = 5,
                          decryptor: int = 1) -> float:
    base = probabilities['probability'].loc[(probabilities['typeID'] == type_id)].iloc[0]
    return base * (1 + ((rem / 40) + ((science1 + science2) / 30))) * decryptor

def me_formula(quantity: int, me: int = 0) -> int:
    return max(1, math.ceil(round((quantity * ((100 - me) / 100)), 2)))

def productToFormula(type_id: int) -> int:
    if type_id not in quantities['productTypeID'].loc[quantities['activityID'] == 11].values:
        raise ValueError(f"{type_id} is not a reaction")
    return quantities['typeID'].loc[(quantities['productTypeID'] == type_id)].iloc[0]

def formulaToProduct(type_id: int) -> int:
    if type_id not in quantities['typeID'].loc[quantities['activityID'] == 11].values:
        raise ValueError(f"{type_id} is not a reaction formula")
    return quantities['productTypeID'].loc[(quantities['typeID'] == type_id)].iloc[0]

def T2ItemToT1BPC(type_id: int) -> int:
    if type_id not in quantities['productTypeID'].loc[quantities['activityID'] == 1].values:
        raise ValueError(f"{type_id} doesnt have a corresponding t1 blueprint")
    t2bpc = quantities['typeID'].loc[(quantities['activityID'] == 1) & (quantities['productTypeID'] == type_id)].iloc[0]
    return quantities['typeID'].loc[(quantities['activityID'] == 8) & (quantities['productTypeID'] == t2bpc)].iloc[0]

def bpToProduct(type_id: int) -> int:
    if type_id not in quantities['typeID'].values:
        raise ValueError(f"{type_id} is not a blueprint")
    return quantities['productTypeID'].loc[(quantities['activityID'] == 1) & (quantities['typeID'] == type_id)].iloc[0]

def productToBP(type_id: int) -> int:
    if type_id not in quantities.loc[(quantities['activityID'] == 1) & (quantities['productTypeID'] == type_id)].values:
        raise ValueError(f"{type_id} doesnt have a corresponding blueprint")
    return quantities['typeID'].loc[(quantities['activityID'] == 1) & (quantities['productTypeID'] == type_id)].iloc[0]

def quantPerRun(type_id: int) -> int:
    if type_id not in quantities['typeID'].values:
        raise ValueError(f"{type_id} is not a blueprint")
    return quantities['quantity'].loc[(quantities['typeID'] == type_id)].iloc[0]