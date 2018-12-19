import os, json

DATA_PATH = 'quickbuilder/data'

def load_ability(arow):
    from qb.models import Ability

    if not Ability.objects.filter(title=arow['title']).exists():
        new_ability = Ability(title=arow['title'], text=arow['text'])
        new_ability.save()


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
    from qb.models import Ability, Upgrade, UPGRADE_TYPES

    fdir = os.path.join(DATA_PATH, 'upgrades')
    u_files = os.listdir(fdir)

    for u in u_files:
        with open(os.path.join(fdir, u)) as rf:
            fdata = json.load(rf)
            for frow in fdata:
                if not Upgrade.objects.filter(xws=frow['xws']).exists():
                    sides = [None, None]
                    for s in frow['sides']:
                        load_ability({'title':s['title'], 'text':s['ability']})
                        sa = Ability.objects.get(title=s['title'])
                        sides[1 if sides[0] else 0] = sa

                    slots = frow['sides'][0]['slots']

                    new_upgrade = Upgrade(name=frow['name'],
                                          xws=frow['xws'],
                                          limited=frow['limited'] if frow['limited'] else '',
                                          cost=frow['cost']['value'],
                                          slot=UPGRADE_TYPES[slots[0]],
                                          slot2=UPGRADE_TYPES[slots[1]] if len(slots)>1 else None,
                                          ability=sides[0],
                                          side2=sides[1] if len(sides)>1 else None
                                          )
                    print(new_upgrade.name)
                    new_upgrade.save()




