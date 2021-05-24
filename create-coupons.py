#!/usr/bin/env python
import stripe
import yaml
stripe.api_key = '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'

coupons = yaml.safe_load(open("coupons_live.yaml"))

for coupon in coupons:

    if 'code' not in coupon and 'name' in coupon:
        coupon['id'] = '%s%s'%(coupon['name'].split(' ')[1].upper(),coupon['amount'])
    else:
        coupon['id'] = '%s%s'%(coupon['code'], coupon['amount'])

    if 'name' not in coupon:
        coupon['cname'] = coupon['id']
    else:
        coupon['cname'] = '%s (%s)'%(coupon['name'], coupon['id'])
    print('Creating:')
    print(coupon)
    try:
        response = stripe.Coupon.create(
          percent_off=coupon['amount'],
          duration="forever",
          id=coupon['id'],
          name=coupon['cname'],
        )
        print('Response:')
        print(response)
    except stripe.error.InvalidRequestError as e:
        print(e)
