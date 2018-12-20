from .models import QuickBuild, Faction, make_lnames


def random_list(threat, faction_id):
    from random import choice
    remaining = threat
    build_list = []
    lnames = make_lnames()
    while remaining > 0:
        qb = QuickBuild.objects.filter(faction_id=faction_id).filter(threat__lte=remaining)
        if not qb.exists():
            break
        new_build = choice(qb)
        too_many_limited = False
        for k in lnames:
            bnames = new_build.limited_names[k]
            for b in bnames:
                if lnames[k].count(b) + bnames.count(b) > int(k):
                    too_many_limited = True
        if not too_many_limited:
            build_list.append(new_build)
            for k in lnames:
                lnames[k].extend(new_build.limited_names[k])
            remaining = remaining - new_build.threat
    return build_list






