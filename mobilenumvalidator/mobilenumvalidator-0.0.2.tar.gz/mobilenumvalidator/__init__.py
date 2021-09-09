import re

def clean_no(no):
    no = re.sub(r'[^0-9]', '', no)
    return no

def validate_no(no):
    flag = False
    if len(no) >= 8 and len(no) <= 11:
        pass
    else:
        flag = True
    return flag

def format_no(no, state_code):
    #Ex: 61410206170 -> 0410206170
    if no.startswith('61') and len(no) == 11:
        local_no = no[-8:]
        area_code = no[2]
        no = '0' + area_code + local_no
    #Ex: 0410206170, 13XX XXX XXX, 18XX XXX XXX
    elif (no.startswith('0') and len(no) == 10) or no.startswith('13') or no.startswith('18'):
        pass
    #Ex: 410206170 -> 0410206170
    elif not(no.startswith('0')) and len(no) == 9:
        no = '0' + no
    #Ex - not a fixed line: 10206170 -> 0410206170
    elif no[0] not in ['9','8','7','4','5','6','3','2'] and len(no) == 8:
        no = '04' + no
    elif state_code in ['NSW', 'ACT'] and len(no) == 8:
        no = '02' + no
    elif state_code in ['VIC', 'TAS'] and len(no) == 8:
        no = '03' + no
    elif state_code == 'QLD' and len(no) == 8:
        no = '07' + no
    elif state_code in ['WA', 'SA', 'NT'] and len(no) == 8:
        no = '08' + no    
    return no

def validator(no, state_code):
    no_cleaned = clean_no(no)
    validator_flag = validate_no(no_cleaned)
    if validator_flag:
        return no_cleaned, validator_flag
    else:
        no_formatted = format_no(no_cleaned, state_code)
        return no_formatted, validator_flag