LIMITED_CHOICES = (
    ('1', '•'),
    ('2', '••'),
    ('3', '•••')
)

# I'm defining some choice lists a little differently, because I need to use the full descs later.
# This keeps them available.

SIZE_TYPES = {
    'Small': 'S',
    'Medium': 'M',
    'Large': 'L'
}

SIZE_CHOICES = [(v, k) for k, v in SIZE_TYPES.items()]


UPGRADE_TYPES = {
    'Astromech':'AST',
    'Cannon': 'CNN',
    'Configuration': 'CNF',
    'Crew': 'CRW',
    'Device': 'DVC',
    'Force Power': 'FRC',
    'Gunner': 'GNR',
    'Illicit': 'ILC',
    'Missile': 'MSL',
    'Modification': 'MOD',
    'Sensor':'SNS',
    'Tactical Relay': 'TAC',
    'Talent': 'TLN',
    'Tech': 'TCH',
    'Title': 'TTL',
    'Torpedo':'TRP',
    'Turret':'TRT',
    'Ship':'SHP'
}

UPGRADE_CHOICES = [(v, k) for k, v in UPGRADE_TYPES.items()]


DIFFICULTY_CHOICES = (
    ('r', 'Red'),
    ('w', 'White'),
    ('b', 'Blue')
)

ARC_CHOICES = (
    ('FT', 'Front Arc'),
    ('LE', 'Left Arc'),
    ('RI','Right Arc'),
    ('RE','Rear Arc'),
    ('FF','Full Front Arc'),
    ('FR','Full Rear Arc'),
    ('BU','Bullseye Arc'),
    ('DT','Double Turret Arc'),
    ('ST','Single Turret Arc')
)

RANGE_CHOICES = (
    ('00', '0'),
    ('11', '1'),
    ('22', '2'),
    ('33', '3'),
    ('12', '1-2'),
    ('23', '2-3'),
    ('13', '1-3')
)

QB_COLORS = ('green', 'yellow', 'orange', 'red', 'magenta', 'purple')
