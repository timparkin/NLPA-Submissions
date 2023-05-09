import json
import copy
from userauth.models import CustomUser as User
from allauth.account.admin import EmailAddress
from nlpa.settings.config import CURRENT_YEAR



# # STRIPE SESSION USERS
#    stripe.api_key = settings.STRIPE_SECRET_KEY
#    email_by_cus_id, ss_users, sessions = clean_ss_users(stripe.checkout.Session.list(limit=100), db_users)
#
#    # STRIPE CUSTOMERS
#    sc_users = clean_sc_users(stripe.Customer.list(limit=100))

def clean_db_users(db_users):

    output = {}

    for user in db_users:

        primary_emails = EmailAddress.objects.filter(user=user.id, primary=True)
        if primary_emails:
            email = primary_emails[0].email
        else:
            email = user.email

        # if user.payment_status and 'checking' in user.payment_status:
        #     print('%s,'%email)

        if user.payment_plan is not None:
            pp = json.loads(user.payment_plan)
            entries = pp['entries']
            projects = pp['portfolios']
            entry_objects = user.entry_set.filter(year=CURRENT_YEAR)
        else:
            entries = 0
            projects = 0
            entry_objects = user.entry_set.filter(year=CURRENT_YEAR)

        N_P1 = 0
        N_P2 = 0
        N_E = 0
        for e in entry_objects:
            if e.category == 'P1':
                N_P1+=1
            elif e.category == 'P2':
                N_P2+=1
            else:
                N_E+=1

        output[email] = {
                'name': '%s %s'%(user.first_name,user.last_name),
                'id': str(user.id),
                'email': email,
                'username': user.username,
                'payment_status': user.payment_status,
                'payment_plan': user.payment_plan,
                'entries': entries,
                'entry_objects': entry_objects,
                'projects': projects,
                'uploads': user.entry_set.filter(year=CURRENT_YEAR).count(),
                'np1': N_P1,
                'np2': N_P2,
                'ne': N_E,
                'in_db': True,
                'is_young_entrant': user.is_young_entrant,
                'date_of_birth': user.date_of_birth,
                'project_title_one': user.project_title_one,
                'project_description_one': user.project_description_one,
                'project_title_two': user.project_title_two,
                'project_description_two': user.project_description_two,
                'date_joined': user.date_joined,
                }

    return output

def clean_mc_users(mc_users):

    output = {}
    for m in mc_users['members']:
        tags = m['tags']
        mc_discount = None
        mc_optin = None
        mc_monster = None
        for t in tags:
            if t['name'] == 'discount':
                mc_discount = True
            if t['name'] == 'optin':
                mc_optin = True
            if t['name'] == 'optinmonster':
                mc_monster = True

        output[m['email_address']] = {
        'mc_email': m['email_address'],
        'in_mailchimp': True,
        'mc_optin': mc_optin,
        'mc_discount': mc_discount,
        'mc_monster': mc_monster
        }

    return output

def clean_ss_users(ss_users, db_users):

    output = {}

    email_by_cus_id = {}

    db_user_by_id={}

    sessions = []

    for email, db_user in db_users.items():
        db_user_by_id[db_user['id']] = db_user

    for c in ss_users.auto_paging_iter():
        #print(c['amount_total'])
        try:
            cid = c['client_reference_id']
            if c['customer_details'] is not None:
                email = c['customer_details']['email']
            else:
                email = db_user_by_id[ cid ]['email']
        except:
                email = '%s?'%c['client_reference_id']
        # this is used to get back to db account email adress from purchae email address (hopefully)
        email_by_cus_id[c['customer']] = email
        data =  {
            'ss_email': email,
            'cr_id': c['client_reference_id'],
            'in_stripe': True,
            'locales': c['locale'],
            }
        if c['payment_status'] == 'paid':
            data['paid'] = c['amount_total']
            data['unpaid'] = 0
        if c['payment_status'] == 'unpaid':
            data['unpaid'] = c['amount_total']
            data['paid'] = 0

        d = copy.copy(data)
        sessions.append(d)
        if email not in output:
            output[email] = data
        else:
            output[email]['paid'] += data['paid']
            output[email]['unpaid'] += data['unpaid']

    return email_by_cus_id, output, sessions


def clean_sc_users(sc_users):

    output = {}
    for c in sc_users.auto_paging_iter():


        if c['address'] is not None:
            output[c['email']] = {
                'sc_email': c['email'],
                'user_id': c['id'],
                'sc_name': c['name'],
                'city': c.get('address',{}).get('city'),
                'country': c.get('address',{}).get('country'),
                'postcode': c.get('address',{}).get('postal_code'),
                }
        else:
            output[c['email']] = {
                'sc_email': c['email'],
                'user_id': c['id'],
                'sc_name': c['name'],
                'city': '',
                'country': '',
                'postcode': '',
                }

    return output

def get_entries(users):
    user = User.objects.get(id=612)
    entries = user.entry_set.all()
    for n,e in enumerate(entries):
        print(n,e.filename,e.id)
    return
