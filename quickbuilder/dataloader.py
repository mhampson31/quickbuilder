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
    from qb.models import Ship, Pilot, Action, ShipAction, PilotAction, Faction, SIZE_TYPES

    fdir = os.path.join(DATA_PATH, 'pilots')
    for fct in os.listdir(fdir):
        subdir = os.path.join(fdir, fct)
        for s in os.listdir(subdir):
            with open(os.path.join(subdir, s)) as rf:
                sdata = json.load(rf)
                faction = Faction.objects.get(name=sdata['faction'])

                if not Ship.objects.filter(xws=sdata['xws']).filter(faction_id=faction.id).exists():
                    print('New ship')
                    # check a pilot for ship abilities
                    if sdata['pilots']:
                        sa = list(sdata['pilots'])[0].get('shipAbility', {'name':'', 'text':''})
                    else:
                        sa = {'name':'', 'text':''}
                    new_ship = Ship(name=sdata['name'],
                                    xws=sdata['xws'],
                                    size=SIZE_TYPES[sdata['size']],
                                    faction=faction,
                                    ability=sa['text'],
                                    ability_title=sa['name']
                                )
                    #ship stats
                    for s in sdata['stats']:
                        v = int(s['value'])

                        if s['type'] == 'attack':
                            if s['arc'] == 'Front Arc':
                                new_ship.front = v
                            elif s['arc'] == 'Single Turret Arc':
                                new_ship.turret = v
                            elif s['arc'] == 'Double Turret Arc':
                                new_ship.doubleturret = v
                            elif s['arc'] == 'Rear Arc':
                                new_ship.rear = v
                            elif s['arc'] == 'Full Front Arc':
                                    new_ship.full_front = v
                            elif s['arc'] == 'Full Rear Arc':
                                    new_ship.full_rear = v
                            else:
                                print('Error: bad arc {}'.format(s['arc']))
                        elif s['type'] == 'agility':
                            new_ship.agility = v
                        elif s['type'] == 'hull':
                            new_ship.hull = v
                        elif s['type'] == 'shields':
                            new_ship.shields = v
                        else:
                            print('Error: bad stat type {}'.format(s['type']))

                    new_ship.save()
                    print('Loaded ship: {}'.format(new_ship.name))

                    ship_actions = sdata['actions']
                    for a in ship_actions:
                        action = Action.objects.get(name=a['type'])
                        hard = True if a['difficulty'] == 'Red' else False
                        new_action = ShipAction(action=action, hard=hard)
                        if 'linked' in a:
                            l = a['linked']
                            new_action.linked_action = Action.objects.get(name=l['type'])
                            new_action.linked_hard = True if l['difficulty'] == 'Red' else False
                        new_action.ship = new_ship
                        print('    {}'.format(new_action))
                        new_action.save()

                else:
                    #print('Skipped ship: {}'.format(sdata['name']))
                    new_ship = Ship.objects.filter(faction_id=faction.id).get(xws=sdata['xws'])
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
                        if 'force' in p:
                            new_pilot.force = int(p['force']['value'])
                        if 'charges' in p:
                            new_pilot.charge = int(p['charges']['value'])
                            new_pilot.charge_regen =  int(p['charges']['value']) > 0

                        new_pilot.save()
                        print('Loaded pilot: {}'.format(new_pilot.name))

                        pilot_actions = p.get('shipActions', [])
                        for a in pilot_actions:
                            action = Action.objects.get(name=a['type'])
                            hard = True if a['difficulty'] == 'Red' else False
                            new_action = PilotAction(action=action, hard=hard)
                            if 'linked' in a:
                                l = a['linked']
                                new_action.linked_action = Action.objects.get(name=l['type'])
                                new_action.linked_hard = True if l['difficulty'] == 'Red' else False
                            new_action.pilot = new_pilot
                            new_action.save()

                    else:
                        #print('Skipped pilot: {}'.format(p['name']))
                        pass

flist = (
    'Rebel Alliance',
    'Galactic Empire',
    'Scum and Villainy',
    'Resistance',
    'First Order',
    'Galactic Republic',
    'Separatist Alliance')


def load_quickbuilds(flist=flist):
    from qb.models import Pilot, Upgrade, QuickBuild, Build, Faction

    fdir = os.path.join(DATA_PATH, 'quick-builds')
    for fct in os.listdir(fdir):
        # figure out the faction from the filename
        fname = fct.replace('-', ' ')[:-5].title()
        # title case capitalizes And but most places the json provides it lowercase. This is just a quick hack to
        # make sure it works
        if fname[:4] == 'Scum':
            fname= 'Scum and Villainy'

        if fname in flist:
            faction = Faction.objects.get(name=fname)
            qbfile = os.path.join(fdir, fct)
            print('{} quick builds'.format(fname))
            with open(qbfile) as rf:

                qbdata = json.load(rf)
                for qb in qbdata['quick-builds']:
                    new_qb = QuickBuild(threat = qb['threat'], faction=faction)
                    new_qb.save()
                    print('Loaded new quick build.')
                    for p in qb['pilots']:
                        pilot = Pilot.objects.get(xws=p['id'])
                        b = Build(quickbuild=new_qb, pilot=pilot)
                        print(' + Adding {} to the current build.'.format(pilot.name))
                        b.save()
                        if 'upgrades' in p:
                            for u in p['upgrades'].values():
                                print(u)
                                b.upgrades.add(*[Upgrade.objects.get(xws=c) for c in u])


def load_actions():
    from qb.models import Ship, Action, ShipAction, Faction

    fdir = os.path.join(DATA_PATH, 'pilots')
    for fct in os.listdir(fdir):
        subdir = os.path.join(fdir, fct)
        for s in os.listdir(subdir):
            with open(os.path.join(subdir, s)) as rf:
                sdata = json.load(rf)
                faction = Faction.objects.get(name=sdata['faction'])
                ship = Ship.objects.filter(xws=sdata['xws']).filter(faction_id=faction.id)[0]



def rebuild():
    # Assuming an empty database...
    from qb.models import Action

    with open(os.path.join(DATA_PATH, 'actions/actions.json', 'r')) as rf:
        af = json.load(rf)
        for a in af:
            if a['name'] == 'Slam':
                a['name'] = 'SLAM'
            new_action = Action(name=a['name'], icon=a['xws'], description='')
            new_action.save()
            print("Loaded {}".format(new_action.name))

    print("Loading Factions")
    load_factions()

    print("Loading Upgrades")
    load_upgrades()

    print("Loading Ships")
    load_ships()

    print("Loading Quick Builds")
    load_quickbuilds()


