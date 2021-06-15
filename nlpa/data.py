import json
import copy

def clean_db_users(db_users):

    output = {}
    for user in db_users:
        if user.payment_plan is not None:
            pp = json.loads(user.payment_plan)
            entries = pp['entries']
            projects = pp['portfolios']
        else:
            entries = 0
            projects = 0
        output[user.email] = {
                'name': '%s %s'%(user.first_name,user.last_name),
                'id': str(user.id),
                'email': user.email,
                'username': user.username,
                'payment_status': user.payment_status,
                'entries': entries,
                'projects': projects,
                'uploads': user.entry_set.count(),
                'in_db': True
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
        'email': m['email_address'],
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


        try:
            cid = c['client_reference_id']
            email = db_user_by_id[ cid ]['email']
        except:
            if c.get('customer_details'):
                email = c['customer_details']['email']
            else:
                email = '%s?'%c['client_reference_id']
        # this is used to get back to db account email adress from purchae email address (hopefully)
        email_by_cus_id[c['customer']] = email
        data =  {
            'email': email,
            'id': c['client_reference_id'],
            'in_stripe': True
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

        output[c['email']] = {
            'email': c['email'],
            'user_id': c['id'],
            'name': c['name'],
            }

    return output
