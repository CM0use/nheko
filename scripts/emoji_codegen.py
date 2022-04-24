#!/usr/bin/env python3

import sys
import re
from unidecode import unidecode
from jinja2 import Template


class Emoji(object):
    def __init__(self, code, shortname, unicodename):
        self.code = ''.join(['\\U'+c.rjust(8, '0') for c in code.strip().split(' ')])
        self.shortname = shortname
        self.unicodename = unicodename

def generate_qml_list(**kwargs):
    tmpl = Template('''
const QVector<Emoji> emoji::Provider::emoji = {
    {%- for c in kwargs.items() %}
    // {{ c[0].capitalize() }}
    {%- for e in c[1] %}
    Emoji{QStringLiteral(u"{{ e.code }}"), QStringLiteral(u"{{ e.shortname }}"), QStringLiteral(u"{{ e.unicodename }}"), emoji::Emoji::Category::{{ c[0].capitalize() }}},
    {%- endfor %}
    {%- endfor %}
};
    ''')
    d = dict(kwargs=kwargs)
    print(tmpl.render(d))
# FIXME: Stop this madness
def humanize_keypad(num): 
    match num: 
        case "0": 
            return "zero" 
        case "1": 
            return "one"
        case "2": 
            return "two"
        case "3": 
            return "three"
        case "4": 
            return "four"
        case "5": 
            return "five"
        case "6": 
            return "six" 
        case "7": 
            return "seven" 
        case "8": 
            return "eight"
        case "9": 
            return "nine"
        case "10": 
            return "ten"
        case "*": 
            return "asterisk"
        case "#": 
            return "hash"
        case _: 
            return None
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: emoji_codegen.py /path/to/emoji-test.txt /path/to/shortcodes.txt')
        sys.exit(1)

    filename = sys.argv[1]
    shortcodefilename = sys.argv[2]

    people = []
    nature = []
    food = []
    activity = []
    travel = []
    objects = []
    symbols = []
    flags = []

    categories = {
        'Smileys & Emotion': people,
        'People & Body': people,
        'Animals & Nature': nature,
        'Food & Drink': food,
        'Travel & Places': travel,
        'Activities': activity,
        'Objects': objects,
        'Symbols': symbols,
        'Flags': flags,
        'Component': symbols
    }
    shortcodeDict = {} 
    # for my sanity - this strips newlines
    for line in open(shortcodefilename, 'r', encoding="utf8"): 
        longname, shortname = line.strip().split(':')
        shortcodeDict[longname] = shortname
    current_category = ''
    for line in open(filename, 'r', encoding="utf8"):
        if line.startswith('# group:'):
            current_category = line.split(':', 1)[1].strip()

        if not line or line.startswith('#'):
            continue

        segments = re.split(r'\s+[#;] ', line.strip())
        if len(segments) != 3:
            continue

        code, qualification, charAndName = segments

        # skip unqualified versions of same unicode
        if qualification != 'fully-qualified' and qualification != 'component' :
            continue
        

        char, name = re.match(r'^(\S+) E\d+\.\d+ (.*)$', charAndName).groups()
        shortname = name
        
        # discard skin tone variants for sanity
        # __contains__ is so stupid i hate prototype languages
        if name.__contains__("skin tone") and qualification != 'component': 
            continue
        if qualification == 'component' and not name.__contains__("skin tone"): 
            continue
        #TODO: Handle skintone modifiers in a sane way
        if shortname in shortcodeDict: 
            shortname = shortcodeDict[shortname]
        else:
            shortname = shortname.lower()
            if shortname.endswith(' (blood type)'): 
                shortname = shortname[:-13]
            if shortname.endswith(': red hair'): 
                shortname = "red_haired_" + shortname[:-10]
            if shortname.endswith(': curly hair'): 
                shortname = "curly_haired_" + shortname[:-12]
            if shortname.endswith(': white hair'): 
                shortname = "white_haried_" + shortname[:-12]
            if shortname.endswith(': bald'): 
                shortname = "bald_" + shortname[:-6]
            if shortname.endswith(': beard'): 
                shortname = "bearded_" + shortname[:-7]
            if shortname.endswith(' face'): 
                shortname = shortname[:-5]
            if shortname.endswith(' button'): 
                shortname = shortname[:-7] 
            if shortname.endswith(' banknote'): 
                shortname = shortname[:-9]
            keycapmtch = re.match(r'^keycap: (.+)$', shortname)
            if keycapmtch: 
                keycapthing, = keycapmtch.groups()
                type(keycapthing)
                num_name = humanize_keypad(keycapthing) 
                if num_name: 
                    shortname = num_name
                else: 
                    raise Exception("incomplete keycap " + keycapthing + ", fix ur code")
                
            # FIXME: Is there a better way to do this?
            matchobj = re.match(r'^flag: (.*)$', shortname) 
            if matchobj: 
                country, = matchobj.groups() 
                shortname = country + " flag"
            shortname = shortname.replace("u.s.", "us")
            shortname = shortname.replace("&", "and")
            shortname = shortname.replace("-", "_")
            shortname, = re.match(r'^_*(.+)_*$', shortname).groups()
            shortname = re.sub(r'\W', '_', shortname) 
            shortname = re.sub(r'_{2,}', '_', shortname) 
            shortname = unidecode(shortname)
        categories[current_category].append(Emoji(code, shortname, name))

    # Use xclip to pipe the output to clipboard.
    # e.g ./codegen.py emoji.json | xclip -sel clip
    # alternatively - delete the var from src/emoji/Provider.cpp, and do ./codegen.py emojis shortcodes >> src/emoji/Provider.cpp
    generate_qml_list(people=people, nature=nature, food=food, activity=activity, travel=travel, objects=objects, symbols=symbols, flags=flags)
