from fetch import FETCHED_DIR
from datetime import datetime
from os.path import join
from os import makedirs
import json


SRC_LEGISLATORS_FILENAME = join(FETCHED_DIR, 'legislators-current.json')
SRC_SOCMED_FILENAME = join(FETCHED_DIR, 'legislators-social-media.json')
SRC_COMMITMEMBERS_FILENAME = join(FETCHED_DIR, 'committee-membership-current.json')
SRC_COMMITTEES_FILENAME = join(FETCHED_DIR, 'committees-current.json')

DEST_DIR = join('bootstrap', 'wrangled')
DEST_LEGISLATORS_FILENAME = join(DEST_DIR, 'legislators.json')
DEST_COMMITTEES_FILENAME = join(DEST_DIR, 'committees.json')

def wrangle_committees():
    all_committees = []
    with open(SRC_COMMITTEES_FILENAME) as rf:
        committees = json.load(rf)

    # for every committee and subcommittee, add the
    # current membership
    for maincom in committees:
        mainx = {}
        for key in maincom.keys():
            mainx[key] = maincom[key]
        # done copying, now add our own keeys
        mainx['committee_id'] = maincom['thomas_id']
        mainx['chamber'] = maincom['type'].capitalize()
        mainx['parent_id'] = None
        mainx['full_name'] = mainx['name']
        # OK, now we deal with subcommittees
        if mainx.get('subcommittees'):
            # remove 'subcommittees' key
            x_subcommittees = mainx['subcommittees']
            # replace it with just a list of ids
            mainx['subcommittees'] = []
            for s in x_subcommittees:
                # inherit some properties
                s['parent_id'] = mainx['committee_id']
                s['chamber'] = mainx['chamber']
                subid = mainx['committee_id'] + s['thomas_id']
                s['committee_id'] = subid
                s['full_name'] = '{0} Subcommittee On {1}'.format(mainx['chamber'], mainx['name'])
                s['subcommittees'] = [] # subcoms don't have subcoms
                mainx['subcommittees'].append(subid)
                all_committees.append(s)
        else:
            mainx['subcommittees'] = []
        all_committees.append(mainx)
    # outside of the for loop
    # we now want to append member data
    with open(SRC_COMMITMEMBERS_FILENAME) as rf:
        memdata = json.load(rf)
    # for each committee in all_committees
    for com in all_committees:
        # have to use get instead of []
        # as not all committees exist currently
        memz = memdata.get(com['committee_id'], [])
        com['members'] = memz

    # write it
    with open(DEST_COMMITTEES_FILENAME, 'w') as wf:
        json.dump(all_committees, wf, indent=2)



def wrangle_legislators():
    today = datetime.now()
    makedirs(DEST_DIR, exist_ok=True)
    with open(SRC_LEGISLATORS_FILENAME) as rf:
        datarows = json.load(rf)
    with open(SRC_SOCMED_FILENAME) as rf:
        socrows = json.load(rf)
    with open(SRC_COMMITMEMBERS_FILENAME) as rf:
        commemdata = json.load(rf)


    mypeeps = []

    for row in datarows:
        p = {}
        # set the name
        p['first_name'] = row['name']['first']
        p['last_name'] = row['name']['last']
        p['full_name'] = row['name']['official_full']
        # set the biography
        p['birthdate'] = row['bio']['birthday']
        _dayslived = (today - datetime.strptime(p['birthdate'], '%Y-%m-%d')).days
        p['years_lived'] = round(_dayslived / 365, 1)
        p['gender'] = row['bio']['gender']
        p['religion'] = row['bio'].get('religion')
        # set the ids
        p['bioguide_id'] = row['id']['bioguide']
        # now that we have bioguide_id, let's hardcode the image URL
        p['image_url'] = "https://theunitedstates.io/images/congress/225x275/{}.jpg".format(p['bioguide_id'])
        p['govtrack_id'] = row['id']['govtrack']
        p['opensecrets_id'] = row['id']['opensecrets']
        p['thomas_id'] = row['id']['thomas']
        p['fec_ids'] = row['id']['fec']
        # derive party and role and tenure from terms
        xterm = row['terms'][-1]
        p['party'] = xterm['party']
        p['state'] = xterm['state']
        # Derive total number of days in office
        # to keep things simple, we'll include the latest term
        days_served = 0
        p['terms_served'] = 0
        for term in row['terms'][0:-2]:
            p['terms_served'] += 1
            datex = datetime.strptime(term['start'], '%Y-%m-%d')
            datey = datetime.strptime(term['end'], '%Y-%m-%d')
            days_served += (datey - datex).days
        # manually calculate days served in current term
        days_served += (today - datetime.strptime(xterm['start'], '%Y-%m-%d')).days
        p['terms_served'] += 1
        p['years_served'] = round(days_served / 365, 2)


        # Now figure out exact title...
        _ttype = xterm['type']
        if  _ttype == 'rep':
            p['title'] = 'Representative'
            p['district'] = xterm['district']
            p['senate_class'] = None
            p['state_rank'] = None
        elif _ttype == 'sen':
            p['title'] = 'Senator'
            p['district'] = None
            p['senate_class'] = xterm['class']
            p['state_rank'] = xterm['state_rank']
        else:
            p['title'] = _ttype
            p['district'] = None
            p['senate_class'] = None
            p['state_rank'] = None

        # finally, add social media

        socdata = next((s for s in socrows if s['id']['bioguide'] == p['bioguide_id']), None)
        p['social_media_accounts'] = {} if socdata is None else socdata['social']



        # finally, finally, add committees
        p['committees'] = []
        for com_id, members in commemdata.items():
            pm = next((m for m in members if m['bioguide'] == p['bioguide_id']), None)
            if pm:
                p['committees'] = {'committee_id': com_id, 'rank': pm['rank'] }



        # all done with this row, append it to mypeeps
        mypeeps.append(p)


    ## all done with looping, now write to file
    with open(DEST_LEGISLATORS_FILENAME, 'w') as wf:
        json.dump(mypeeps, wf, indent=2)




if __name__ == '__main__':
    # just in case someone runs script from command line
    print("Wrangling legislators data")
    print("\tReading from", SRC_LEGISLATORS_FILENAME)
    wrangle_legislators()
    print("\tWrote to", DEST_LEGISLATORS_FILENAME)

    print("Wrangling committees data")
    print("\tReading from", SRC_COMMITMEMBERS_FILENAME, 'and', SRC_COMMITTEES_FILENAME)
    wrangle_committees()
    print("\tWrote to", DEST_COMMITTEES_FILENAME)

