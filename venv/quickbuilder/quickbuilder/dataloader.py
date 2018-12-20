import os, json

DATA_PATH = 'quickbuilder/data'

def load_factions():
    from qb.models import Faction

    fpath = os.path.join(DATA_PATH, 'factions/factions.json')

    with open(fpath, 'r') as rf:
        fdata = json.load(rf)
        for frow in fdata:
            if not Faction.objects.filter(xws=frow['xws']).exists():
                new_faction = Faction(name=frow['name'], xws=frow['xws'], ffg=frow.get('ffg', None))
                new_faction.save()


def load_upgrades():
    from qb.models import Upgrade, UPGRADE_TYPES

    fdir = os.path.join(DATA_PATH, 'upgrades')
    u_files = os.listdir(fdir)

    for u in u_files:
        with open(os.path.join(fdir, u)) as rf:
            fdata = json.load(rf)
            for frow in fdata:
                if not Upgrade.objects.filter(xws=frow['xws']).exists():
                    sides = [{'title':'', 'text':''}, {'title':'', 'text':''}]
                    for s in frow['sides']:
                        sides[1 if sides[0]['title'] else 0] = {'title':s.get('title', ''), 'text':s.get('ability', '')}

                    slots = frow['sides'][0]['slots']

                    new_upgrade = Upgrade(name=frow['name'],
                                          xws=frow['xws'],
                                          limited=frow.get('limited', ''),
                                          slot=UPGRADE_TYPES[slots[0]],
                                          slot2=UPGRADE_TYPES[slots[1]] if len(slots)>1 else None,
                                          ability=sides[0]['text'],
                                          ability_title=sides[0]['title'],
                                          ability2=sides[1]['text'],
                                          ability2_title=sides[1]['title'],
                                    )
                    new_upgrade.save()
                    print("++ Upgrade loaded: {}".format(new_upgrade.name))
                else:
                    print("-- Upgrade skipped: {}".format(frow['name']))


def load_ships():
    from qb.models import Ship, Pilot, SIZE_TYPES, FACTION_TYPES

    fdir = os.path.join(DATA_PATH, 'pilots')
    for fct in os.listdir(fdir):
        subdir = os.path.join(fdir, fct)
        for s in os.listdir(subdir):
            with open(os.path.join(subdir, s)) as rf:
                sdata = json.load(rf)
                if not Ship.objects.filter(xws=sdata['xws']).exists():
                    # check a pilot for ship abilities
                    if sdata['pilots']:
                        sa = list(sdata['pilots'])[0].get('shipAbility', {'name':'', 'text':''})
                    else:
                        sa = {'name':'', 'text':''}
                    new_ship = Ship(name=sdata['name'],
                                    xws=sdata['xws'],
                                    size=SIZE_TYPES[sdata['size']],
                                    faction=FACTION_TYPES[sdata['faction']],
                                    ability=sa['text'],
                                    ability_title=sa['name']
                                )
                    new_ship.save()
                    print('Loaded ship: {}'.format(new_ship.name))
                else:
                    print('Skipped ship: {}'.format(sdata['name']))
                    new_ship = Ship.objects.get(xws=sdata['xws'])
                for p in sdata['pilots']:
                    if not Pilot.objects.filter(xws=p['xws']).exists():
                        new_pilot = Pilot(name=p['name'],
                                          xws=p['xws'],
                                          limited=p.get('limited', ''),
                                          caption=p.get('caption', ''),
                                          initiative=p.get('initiative', 1),
                                          ability=p.get('ability', ''),
                                          ship=new_ship
                                    )
                        new_pilot.save()
                        print('Loaded pilot: {}'.format(new_pilot.name))
                    else:
                        print('Skipped pilot: {}'.format(p['name']))


def load_quickbuilds():
    from qb.models import Pilot, Upgrade, QuickBuild

    fdir = os.path.join(DATA_PATH, 'pilots')
    for fct in os.listdir(fdir):
        subdir = os.path.join(fdir, fct)
        for s in os.listdir(subdir):
            with open(os.path.join(subdir, s)) as rf:
                qbdata = json.load(rf)
                for qb in qbdata['quick-builds']:
                    threat = qb['threat']

                    pilot = Pilot.objects.get(xws=qb['xws'])

