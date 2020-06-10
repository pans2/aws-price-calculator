#!/usr/bin/env python

from __future__ import division
import requests
import pandas as pd
import os
import json
import awscnpricing
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://admin:changeme@database-1.csmg1iyz8zqb.us-east-2.rds.amazonaws.com:3306/testdemo')
import datetime
import numpy as np
from numpy import *

start = datetime.datetime.now().strftime('%Y-%m-%d')
end = (datetime.datetime.now()+datetime.timedelta(days=100)).strftime('%Y-%m-%d')
output = 'peterpan_demo_cn_rds.xlsx'

offering_class = 'standard'

rds_offer_code = 'AmazonRDS'
rds_offer = awscnpricing.offer(rds_offer_code)
rds_file_name = 'offer_{}_current'.format(rds_offer_code)

offers = requests.get('https://pricing.cn-north-1.amazonaws.com.cn/offers/v1.0/cn/index.json')
rds_offer_path = offers.json()['offers']['AmazonRDS']['currentVersionUrl']
rdsoffer = requests.get('https://pricing.cn-north-1.amazonaws.com.cn%s' % rds_offer_path).json()


on_demand_price = []
r_type = []
r_vcpu = []
r_location = []
r_memory = []
r_database_engine = []
r_license_model = []
PerchaseOption = ['All Upfront']
LeaseContractLength = ['1yr']
reserve_price = {}
reserve_price['1yr_all'] = []
reserve_price['1yr_no'] = []
reserve_price['1yr_partial'] = []
reserve_price['3yr_all'] = []
reserve_price['3yr_no'] = []
reserve_price['3yr_partial'] = []
for sku, data in rdsoffer['products'].items():
    if data['productFamily'] != 'Database Instance':
        # skip anything that's not an database Instance
        continue
    rds_type = data['attributes']['instanceType']
    rds_license = data['attributes']['licenseModel']
    db_engine = data['attributes']['databaseEngine']
    site = data['attributes']['location']
    rds_region = ""
    if site == "China (Beijing)":
        rds_region = "cn-north-1"
    if site == "China (Ningxia)":
        rds_region = "cn-northwest-1"

    for yr in LeaseContractLength:
        for p_option in PerchaseOption:
            try:
                a_price = rds_offer.reserved_upfront(
                    rds_type,
                    database_engine=db_engine,
                    license_model=rds_license,
                    lease_contract_length=yr,
                    offering_class=offering_class,
                    purchase_option=p_option,
                    region=rds_region,
                )
            except:
                a_price = "0"
            try:
                o_price = rds_offer.ondemand_hourly(
                    rds_type,
                    database_engine=db_engine,
                    license_model=rds_license,
                    region=rds_region,
                )
            except:
                o_price = "0"
            on_demand_price.append(o_price)
            r_type.append(rds_type)
            r_vcpu.append(data['attributes']['vcpu'])
            r_location.append(site)
            r_memory.append(data['attributes']['memory'].replace(
                " GiB", "").replace(",", ""))
            r_database_engine.append(db_engine)
            r_license_model.append(rds_license)

            if p_option == 'All Upfront':
                    reserve_price['1yr_all'].append(a_price)
                    reserve_price['1yr_no'].append('0')
                    reserve_price['1yr_partial'].append('0')
                    reserve_price['3yr_all'].append('0')
                    reserve_price['3yr_no'].append('0')
                    reserve_price['3yr_partial'].append('0')

OD_month_744hours = [i * 744 for i in on_demand_price]
OD_year_365days = [j * 24 * 365 for j in on_demand_price]

df = pd.DataFrame({'vcpu': r_vcpu, 'memory': r_memory,
    'location': r_location, 'databaseEngine': r_database_engine, 'licenseModel': r_license_model,
    "all_upfront_price_1yr": reserve_price['1yr_all'], 'OD_month_744hours': OD_month_744hours,
    'type': r_type, 'OD_year_365days': OD_year_365days, 
    "on_demand_price": on_demand_price})
df[['vcpu', 'memory', 'all_upfront_price_1yr', 'on_demand_price', 'OD_month_744hours', 'OD_year_365days']] = df[[
    'vcpu', 'memory', 'all_upfront_price_1yr', 'on_demand_price', 'OD_month_744hours', 'OD_year_365days']].astype('float')
df.drop_duplicates(subset=['type', 'vcpu', 'memory', 'location', 'all_upfront_price_1yr',
                           'databaseEngine', 'licenseModel', 'on_demand_price', 'OD_month_744hours', 'OD_year_365days'], keep='first', inplace=True)
df = df[(df.all_upfront_price_1yr > 0) | (
     df.on_demand_price > 0) ]
df = df.reset_index(drop=True)
cols = ['type', 'vcpu', 'memory', 'location', 'databaseEngine', 'licenseModel', 'on_demand_price', 'OD_month_744hours', 'OD_year_365days', 'all_upfront_price_1yr']
df = df.ix[:,cols]
print(df)
print (df)
df.to_sql('rdsdemo2', engine)
df.to_excel(output, sheet_name='price')
