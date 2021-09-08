import re
import json
import requests
import user_agent

def get_page(q, retry = True):
    s   = requests.Session()
    s.headers["User-Agent"] = user_agent.generate_user_agent()

    while True:
        try:
            req = s.get("https://duckduckgo.com/", params = {"q": q.replace(" ", "+")})
            break
        except Exception as e:
            if retry != True:
                raise e

    if req.status_code != 200:
        raise ValueError("HTTP ERROR %s" % (req.status_code))

    t = re.findall("t\.js[^\'|\"]*", req.text)
    d = re.findall("d\.js[^\'|\"]*", req.text)

    treq = s.get(f"https://duckduckgo.com/{t[0]}")
    if treq.status_code != 200:
        raise ValueError("HTTP ERROR %s" % (treq.status_code))

    dreq = s.get(f"https://links.duckduckgo.com/{d[0]}")
    if dreq.status_code != 200:
        raise ValueError("HTTP ERROR %s" % (dreq.status_code))

    return dreq.text

def getAbstractInfo(page):
    start = re.search("DDG.duckbar.add\(", page)

    if start == None:
        return None

    start = start.span()[1]
    end   = re.search("}}\)", page[start:len(page)])
    end   = end.span()[1]+start-1

    return json.loads(page[start:end])

def getURLs(page):
    start = re.search("DDG.pageLayout.load\(\'d\',", page).span()[1]
    end   = re.search("}]\)", page[start:len(page)]).span()[1]
    end   += start-1

    out = []
    for child in json.loads(page[start:end]):
        if len(child) == 1:
            continue

        out.append(
            {
                "link": child["c"],
                "description": child["a"],
                "server": child["i"]
            }
        )

    return out

