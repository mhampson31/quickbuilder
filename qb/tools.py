import logging
from random import choice

from .models import Build, QuickBuild, Faction, make_lnames

logger = logging.getLogger(__name__)


class QuickList(object):
    def __init__(self, max_threat, faction_id, build_objs=[], build_ids=[]):
        self.max_threat = max_threat
        self.faction_id = faction_id
        self.build_list = []
        self.rejects = []
        self.lnames = make_lnames()

        # build_objs could be used to pass already-created QuickBuild objects into the build list, avoiding a DB query.
        for new_build in build_objs:
            self.add_build(new_build)

        # build_ids is similar to build_objs, except it's a just ID numbers.
        for new_build in QuickBuild.objects.filter(id__in=build_ids):
            self.add_build(new_build)

    @property
    def threat(self):
        return sum([b.threat for b in self.build_list])

    def add_build(self, new_build):
        """
        Takes a QuickBuild object and, if it wouldn't violate Limited constraints, adds it to the list.
        :param new_build: a QuickBuild object
        :return: False if the QuickBuild would add too many copies of a limited card; otherwise True
        """
        for pip in self.lnames:
            # What we're doing here: Each limited card can occur at most n times in a list, where n is the number of
            # limited pips in front of the name on the card. (Usually, one.) So the quick list uses a dict called lnames
            # where each globally-defined pip count is a key, and each limited pilot or upgrade card with that name
            # gets appended to the list with its pip count. If we try to add a quick build that has a limited card that's
            # already at its limit for the list, we want to reject it.
            bnames = new_build.limited_names[pip]
            for name in bnames:
                if self.lnames[pip].count(name) + bnames.count(name) > int(pip):
                    logging.info('Nope, too many copies of {}.'.format(name))
                    # We want to keep track of quick builds we can't use, to avoid trying them again later
                    self.rejects.append(new_build.id)
                    return False
        logger.info('Adding {} to the list.'.format(new_build))
        self.build_list.append(new_build)
        self.build_list.sort(key=lambda x: x.threat, reverse=True)
        for k in self.lnames:
            self.lnames[k].extend(new_build.limited_names[k])
        return True

    def random_fill(self):
        threat = self.max_threat - self.threat
        all_builds = QuickBuild.objects.filter(faction_id=self.faction_id).filter(threat__lte=threat)
        rejects = []
        while threat > 0:
            try:
                new_build = choice([b for b in all_builds if b.threat <= threat and b.id not in rejects])
            except IndexError:  # random.choice raises this exception if new_build is empty
                logging.info('No ships left with threat <= {}'.format(threat))
                break
            self.add_build(new_build)
            threat = self.max_threat - self.threat
            logging.info('{} remaining threat points to spend.'.format(threat))