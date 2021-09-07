
"""Content-Type and accept headers for json"""
json_content_accept = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

"""Content-Type headers"""
json_content = {'Content-Type': 'application/json'}
form_urlencoded_content = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}

"""Accept headers"""
json_accept = {'Accept': 'application/json'}
text_accept = {'Accept': 'text/plain'}
html_accept = {'Accept': 'text/html'}
xml_accept = {'Accept': 'application/xml'}


"""header for Atlassian to not check token"""
no_check_atlassian_token = {'X-Atlassian-Token': 'no-check'}
