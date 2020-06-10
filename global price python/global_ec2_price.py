#!/usr/bin/env python

from __future__ import division
import requests
import pandas as pd
import os
import json
import awspricing
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://admin:changeme@database-1.csmg1iyz8zqb.us-east-2.rds.amazonaws.com:3306/testdemo_global')
import datetime
import numpy as np
from numpy import *

start = datetime.datetime.now().strftime('%Y-%m-%d')
end = (datetime.datetime.now()+datetime.timedelta(days=100)).strftime('%Y-%m-%d')

offering_class = 'standard'

ec2_offer_code = 'AmazonEC2'
ec2_offer = awspricing.offer('AmazonEC2')
ec2_file_name = 'offer_{}_current'.format(ec2_offer_code)

offers = requests.get('https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/index.json')
ec2_offer_path = offers.json()['offers']['AmazonEC2']['currentVersionUrl']
ec2offer = requests.get('https://pricing.us-east-1.amazonaws.com%s' % ec2_offer_path).json()

on_demand_price = []
r_type = []
r_vcpu = []
r_location = []
r_memory = []
r_operatingSystem = []
r_tenancy = []
r_preinstalled_software = []
PerchaseOption = ['All Upfront']
LeaseContractLength = ['1yr']
leasecontractlength = ['3yr']
reserve_price = {}
reserve_price['1yr_all'] = []
reserve_price['3yr_all'] = []
for sku, data in ec2offer['products'].items():
    if data['productFamily'] != 'Compute Instance':
        # skip anything that's not an EC2 Instance
        continue
    ec2_type = data['attributes']['instanceType']

    ec2_os = data['attributes']['operatingSystem']

    site = data['attributes']['location']
    ec2_region = ""
    if site == "US East (N. Virginia)":
        ec2_region = "us-east-1"
    if site == "US East (Ohio)":
        ec2_region = "us-east-2"
    if site == "US West (N. California)":
        ec2_region = "us-west-1"
    if site == "US West (Oregon)":
        ec2_region = "us-west-2"
    if site == "Asia Pacific (Hong Kong)":
        ec2_region = "ap-east-1"
    if site == "Asia Pacific (Mumbai)":
        ec2_region = "ap-south-1"
    if site == "Asia Pacific (Osaka-Local)":
        ec2_region = "ap-northeast-3"
    if site == "Asia Pacific (Seoul)":
        ec2_region = "ap-northeast-2"
    if site == "Asia Pacific (Singapore)":
        ec2_region = "ap-southeast-1"
    if site == "Asia Pacific (Sydney)":
        ec2_region = "ap-southeast-2"
    if site == "Asia Pacific (Tokyo)":
        ec2_region = "ap-northeast-1"
    if site == "Canada (Central)":
        ec2_region = "ca-central-1"
    if site == "EU (Frankfurt)":
        ec2_region = "eu-central-1"
    if site == "EU (Ireland)":
        ec2_region = "eu-west-1"
    if site == "EU (London)":
        ec2_region = "eu-west-2"
    if site == "EU (Paris)":
        ec2_region = "eu-west-3"
    if site == "EU (Stockholm)":
        ec2_region = "eu-north-1"
    if site == "Middle East (Bahrain)":
        ec2_region = "me-south-1"
    if site == "South America (Sao Paulo)":
        ec2_region = "sa-east-1"    
    for yra in LeaseContractLength:
		for yrb in leasecontractlength:
			for p_option in PerchaseOption:
				try:
					a_price = ec2_offer.reserved_upfront(
						ec2_type,
						operating_system=ec2_os,
						lease_contract_length='1yr',
						tenancy=data['attributes']['tenancy'],
						preinstalled_software=data['attributes']['preInstalledSw'],
						offering_class=offering_class,
						purchase_option=p_option,
						region=ec2_region,
					)
				except:
					a_price = "0"
				try:
					b_price = ec2_offer.reserved_upfront(
						ec2_type,
						operating_system=ec2_os,
						lease_contract_length='3yr',
						tenancy=data['attributes']['tenancy'],
						preinstalled_software=data['attributes']['preInstalledSw'],
						offering_class=offering_class,
						purchase_option=p_option,
						region=ec2_region,
					)
				except:
					b_price = "0"
				try:
					o_price = ec2_offer.ondemand_hourly(
						ec2_type,
						operating_system=ec2_os,
						tenancy=data['attributes']['tenancy'],
						preinstalled_software=data['attributes']['preInstalledSw'],
						region=ec2_region,
					)
				except:
					o_price = "0"
				on_demand_price.append(o_price)
				r_type.append(ec2_type)
				r_vcpu.append(data['attributes']['vcpu'])
				r_location.append(site)
				r_memory.append(data['attributes']['memory'].replace(
					" GiB", "").replace(",", ""))
				r_operatingSystem.append(ec2_os)
				r_tenancy.append(data['attributes']['tenancy'])
				r_preinstalled_software.append(
					data['attributes']['preInstalledSw'])

				if p_option == 'All Upfront':
					if yra == '1yr':
						reserve_price['1yr_all'].append(a_price)

					if yrb == '3yr':
						reserve_price['3yr_all'].append(b_price)

OD_month_744hours = [i * 744 for i in on_demand_price]
OD_year_365days = [j * 24 * 365 for j in on_demand_price]


df = pd.DataFrame({'vcpu': r_vcpu, 'memory': r_memory,
    'location': r_location,
    "tenancy": r_tenancy,
    "os": r_operatingSystem,
    "all_upfront_price_1yr": reserve_price['1yr_all'],
    'type': r_type,
    "on_demand_price": on_demand_price,
    'OD_month_744hours': OD_month_744hours,
    'OD_year_365days': OD_year_365days,
    'pre_installedSW': r_preinstalled_software,
	'all_upfront_price_3yr': reserve_price['3yr_all']})
df[['vcpu', 'memory', 'all_upfront_price_1yr', 'on_demand_price', 'OD_month_744hours', 'OD_year_365days', 'all_upfront_price_3yr']] = df[[
    'vcpu', 'memory', 'all_upfront_price_1yr', 'on_demand_price', 'OD_month_744hours', 'OD_year_365days', 'all_upfront_price_3yr']].astype('float')
df.drop_duplicates(subset=['type', 'vcpu', 'memory', 'location', 'tenancy', 'os', 'all_upfront_price_1yr',
                           'on_demand_price', 'OD_month_744hours', 'OD_year_365days', 'all_upfront_price_3yr'], keep='first', inplace=True)
df = df[(df.all_upfront_price_1yr > 0) | (
     df.on_demand_price > 0) ]
df = df.reset_index(drop=True)
cols = ['type', 'vcpu', 'memory', 'location', 'tenancy', 'os', 'pre_installedSW', 'on_demand_price', 'OD_month_744hours', 'OD_year_365days', 'all_upfront_price_1yr', 'all_upfront_price_3yr']
df = df.ix[:,cols]
df = df.sort_values('type', ascending=True)
print (df)
df.to_sql('demo002', engine)
