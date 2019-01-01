from random import choice

from .models import QuickBuild, Faction, make_lnames


DEBUG = True


def random_list(threat, faction_id):
    build_list = []
    rejects = []
    lnames = make_lnames()

    print('Starting quickbuild.')

    all_builds = QuickBuild.objects.filter(faction_id=faction_id).filter(threat__lte=threat)

    while threat > 0:
        try:
            new_build = choice([b for b in all_builds if b.threat <= threat and b.id not in rejects])
        except IndexError: # random.choice raises this exception if new_build is empty
            if DEBUG: print('No ships left with threat <= {}'.format(threat))
            break
        if DEBUG: print('Trying {}'.format(new_build))
        too_many_limited = False
        for k in lnames:
            bnames = new_build.limited_names[k]
            for b in bnames:
                if lnames[k].count(b) + bnames.count(b) > int(k):
                    too_many_limited = True
                    if DEBUG: print('Nope, too many copies of {}.'.format(b))
                    rejects.append(new_build.id)
                    if DEBUG: print('Rejects: {}'.format(rejects))
                    break
        if not too_many_limited:
            if DEBUG: print('Adding {} to the list.'.format(new_build))
            build_list.append(new_build)
            for k in lnames:
                lnames[k].extend(new_build.limited_names[k])
            threat = threat - new_build.threat
            if DEBUG: print('{} remaining threat points to spend.'.format(threat))
    print('Done.')
    build_list.sort(key=lambda x: x.threat, reverse=True)
    return build_list