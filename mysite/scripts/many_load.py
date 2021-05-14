import csv  # https://docs.python.org/3/library/csv.html

# https://django-extensions.readthedocs.io/en/latest/runscript.html

# python3 manage.py runscript many_load

from unesco.models import Site, Category, Iso, Region, State


def run():
    fhand = open('unesco/load.csv')
    reader = csv.reader(fhand)
    next(reader)  # Advance past the header

    Site.objects.all().delete()
    Category.objects.all().delete()
    Iso.objects.all().delete()
    Region.objects.all().delete()
    State.objects.all().delete()

    # Format
    # email,role,course
    # jane@tsugi.org,I,Python
    # ed@tsugi.org,L,Python

    for row in reader:
        print(row)

        c, created = Category.objects.get_or_create(name=row[7])
        i, created = Iso.objects.get_or_create(name=row[10])
        r, created = Region.objects.get_or_create(name=row[9])
        s, created = State.objects.get_or_create(name=row[8])
        try:
            y = int(row[3])
        except:
            y = None
        try:
            area = float(row[6])
        except:
            area = None

        #r = Membership.LEARNER
        #if row[1] == 'I':
        #    r = Membership.INSTRUCTOR
        si = Site(name=row[0],area_hectares=area,year=y,category=c,iso=i,region=r,state=s)
        si.save()