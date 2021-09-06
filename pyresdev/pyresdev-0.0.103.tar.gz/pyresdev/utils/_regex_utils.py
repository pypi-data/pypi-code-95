import re
from typing import List, Tuple



EMAIL_REGEX = r'[a-zA-Z]+[\w.<->_-]+@[a-zA-Z.-]+(?:\.[a-zA-Z]+)+'
SKYPE_REGEX = r'(?:(?:callto|Callto|skype|Skype):?\s?)' \
              r'(?P<username>[a-z][a-z0-9\.,\-_]{5,31})' \
              r'(?:\?(?:add|call|chat|sendfile|userinfo))?'


def search_for_phones(text: str) -> Tuple[List[str], List[str], List[str]]:
    phones = re.findall(
        r'(?<![a-z@.,%&#-])'
        r'(?:M:? ?[–-]?\+?|mobile:? ?[–-]?\+?|Mobile:? ?[–-]?\+?|'
        r'C:? ?[–-]?\+?|cell:? ?[–-]?\+?|Cell:? ?[–-]?\+?|'
        r'O:? ?[–-]?\+?|office:? ?[–-]?\+|Office:? ?[–-]?\+?|'
        r'D:? ?[–-]?\+?|direct:? ?[–-]?\+?|Direct:? ?[–-]?\+?)'
        r'?[(]?(?:\+?\d{1,2})?[)]?[-. (]*\d{1,4}[-. )]*\d{3,4}[-. ]*\d{2,4}(?: *x\d+)?[-. ]*\d{1,7}',
        text
    )
    out: List[str] = []
    mobile: List[str] = []
    office: List[str] = []
    for x in phones:
        x = x.casefold()
        if x.startswith(("mobile", "m", "cell", "c")):
            x = x.replace("mobile", '')
            x = x.replace("m", '')
            x = x.replace("cell", '')
            x = x.replace("c", '')
            list_to_append_in = mobile
        elif x.startswith(("office", "o", "direct", "d")):
            x = x.replace("office", '')
            x = x.replace("o", '')
            x = x.replace("direct", '')
            x = x.replace("d", '')
            list_to_append_in = office
        else:
            list_to_append_in = out
        x = x.replace('–', '-')
        x = x.replace(':', ' ')
        x = re.sub(r"-+", "-", x).strip()
        x = re.sub(r"\.+", ".", x).strip()
        x = re.sub(r"^[\.-]+", "", x)
        x = re.sub(r"[\.-]+$", "", x)
        x = re.sub(r" +", " ", x).strip()
        if x.startswith(')'):
            x = x[1:].strip()
        # clean time period. Ex: 2010 - 2013 or 2018-157
        parts = x.replace('-', ' ').replace('.', ' ').split(' ')
        first_part = parts[0].replace('(', '').replace(')', '').replace('+', '').strip()
        if len(first_part) != 4 or not 1900 < int(first_part) < 2100:
            if len(x) > 8:  # Ignore company numbers and short detections
                list_to_append_in.append(x.strip())
    return out, mobile, office


def search_for_emails(text: str) -> List[str]:
    detected_emails = re.findall(EMAIL_REGEX, text)
    out = []
    for x in detected_emails:
        x = x.casefold()
        x = x.replace('–', '-')
        x_username, x_domain = split_email_username_and_domain(x)
        if x_username.count('.') <= 3 and x_username.count('-') <= 3 \
                and 'www.' not in x_username and 'www.' not in x_domain:
            out.append(x)
    return out


def split_email_username_and_domain(email: str) -> Tuple[str, str]:
    parts = email.split('@')
    return parts[0], parts[1]


def search_for_websites(text: str) -> List[str]:
    # Emails are bad detected as websites
    text_without_emails = re.sub(EMAIL_REGEX, '', text)
    text_without_skypes = re.sub(SKYPE_REGEX, '', text_without_emails).strip()
    websites = re.findall(
        r'\b(?<![@.,%&#-])(?:\w{2,10}:\/\/)?(?:(?:\w|\&\#\d{1,5};)[.-]?)+(?:\.(?:[a-z]{2,15})|'
        r'(?:(?:\\d{1,6})|(?!)))\b(?![@])(?:\/)?(?:(?:[\w\d\?\-=#:%@&.;])+'
        r'(?:\/(?:(?:[\w\d\?\-=#:%@&;.])+))*)?(?<![.,?!-])', text_without_skypes
    )
    # This domains are detected by other functions
    blacklist = {
        'fb.com', 'facebook.com', 'github.com', 'twitter.com',
        'instagram.com', 'pinterest.com', 'medium.com',
        'linkedin.com', 'telegram.me', 'telegram.org'
    }
    return list(
        filter(
            lambda website: all(x not in website for x in blacklist), websites
        )
    )


def search_for_twitter_usernames(text: str) -> List[str]:
    return [x.strip() for x in re.findall(r'(?:^|[^@\w])@(?:\w{1,15})\b', text)]


def search_for_facebook_profiles(text: str) -> List[str]:
    facebook_profiles = re.findall(
        r'(?:https?:)?\/\/(?:www\.)?(?:facebook|fb)\.com\/(?P<profile>(?![A-z]+\.php)'
        r'(?!marketplace|gaming|watch|me|messages|help|search|groups)[A-z0-9_\-\.]+)\/?',
        text
    )
    facebook_profiles_by_id = re.findall(
        r'(?:https?:)?\/\/(?:www\.)facebook.com/(?:profile.php\?id=)?(?P<id>[0-9]+)', text
    )

    join_facebook = " ".join(facebook_profiles)
    for face in facebook_profiles_by_id:
        if face not in join_facebook:
            facebook_profiles.append(face)
    return facebook_profiles


def search_for_github_usernames(text: str) -> List[str]:
    return re.findall(r'(?:https?:)?\/\/(?:www\.)?github\.com\/(?P<login>[A-z0-9_-]+)\/?', text)


def search_for_instagram_profiles(text: str) -> List[str]:
    return re.findall(
        r'(?:https?:)?\/\/(?:www\.)?(?:instagram\.com|instagr\.am)\/'
        r'(?P<username>[A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)',
        text
    )


def search_for_linkedin_profiles(text: str) -> List[str]:
    return re.findall(r'(?:https?:)?\/\/(?:[\w]+\.)?linkedin\.com\/in\/(?P<permalink>[\w\-\_À-ÿ%]+)\/?', text)


def search_for_linkedin_company(text: str) -> List[str]:
    return re.findall(
        r'(?:https?:)?\/\/(?:[\w]+\.)?linkedin\.com\/company\/(?P<company_permalink>[A-z0-9-\.]+)\/?', text
    )


def search_for_medium_user(text: str) -> List[str]:
    usernames = re.findall(r'(?:https?:)?\/\/medium\.com\/@(?P<username>[A-z0-9]+)(?:\?.*)?', text)
    users_by_id = re.findall(r'(?:https?:)?\/\/medium\.com\/u\/(?P<user_id>[A-z0-9]+)(?:\?.*)', text)
    return usernames + users_by_id


def search_for_skype(text: str) -> List[str]:
    return re.findall(SKYPE_REGEX, text)


def search_for_telegram(text: str) -> List[str]:
    return re.findall(
        r'(?:https?:)?\/\/(?:t(?:elegram)?\.me|telegram\.org)\/(?P<username>[a-z0-9\_]{5,32})\/?', text
    )