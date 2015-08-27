#!/usr/bin/env/ python
# -*- coding: utf-8 -*-

import datetime
import json
import urllib
import urllib2
import requests
import re
import time


def get_new_access_token():
    url = 'https://www.googleapis.com/oauth2/v3/token'
    #    data = {'client_id': '',
    #            'client_secret': '',
    #            'refresh_token': '',
    #            'grant_type': 'refresh_token'}
    data = {'client_id': '',
            'client_secret': '',
            'refresh_token': '',
            'grant_type': 'refresh_token'}
    r = requests.post(url, data=data)
    access_token = json.loads(r.text)['access_token']
    return access_token


def get_usd_rur(d):
    # converts 1 USD in RUR
    # get_usd_rur('2015-08-10')
    # > 63.42
    d_1 = (datetime.datetime.strptime(d, '%Y-%m-%d') - datetime.timedelta(1)).strftime('%Y-%m-%d')
    d_2 = (datetime.datetime.strptime(d, '%Y-%m-%d') - datetime.timedelta(2)).strftime('%Y-%m-%d')
    d_3 = (datetime.datetime.strptime(d, '%Y-%m-%d') - datetime.timedelta(3)).strftime('%Y-%m-%d')
    d_4 = (datetime.datetime.strptime(d, '%Y-%m-%d') - datetime.timedelta(4)).strftime('%Y-%m-%d')
    d_5 = (datetime.datetime.strptime(d, '%Y-%m-%d') - datetime.timedelta(5)).strftime('%Y-%m-%d')
    d_6 = (datetime.datetime.strptime(d, '%Y-%m-%d') - datetime.timedelta(6)).strftime('%Y-%m-%d')

    print 'sending request to currency api. Data provider Bank of England powered by www.quandl.com'
    api = 'https://www.quandl.com/api/v1/datasets/BOE/XUDLBK69?auth_token=JGu4ByMVixuz6uywb8Ha'
    resp = requests.get(api).content
    print 'currency received'
    data = json.loads(resp)['data']
    # print data
    for i in data:
        if i[0] in [d, d_1, d_2, d_3, d_4, d_5, d_6]:
            currency = i[1]
            return float(currency)
    return float(data[0][1])


def get_google_data(start, end):
    # currency_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y-%m-%d')
    # currency = get_usd_rur(currency_date)
    # print currency
    currency = 1
    host = 'https://adwords.google.com/api/adwords/reportdownload/v201506'
    # access_token = ''
    access_token = get_new_access_token()
    header = {'Authorization': 'Bearer %s' % access_token,
              'Content-Type': 'application/x-www-form-urlencoded',
              'developerToken': '',
              'clientCustomerId': ''}

    __rdxml = '''
    <reportDefinition xmlns="https://adwords.google.com/api/adwords/cm/v201506">
        <selector>
                <fields>CampaignName</fields>
                <fields>CampaignStatus</fields>
                <fields>Impressions</fields>
                <fields>Clicks</fields>
                <fields>Cost</fields>
                <dateRange>
                  <min>%s</min>
                  <max>%s</max>
                </dateRange>
        </selector>
        <reportName>Custom Adgroup Performance Report</reportName>
        <reportType>ADGROUP_PERFORMANCE_REPORT</reportType>
        <dateRangeType>CUSTOM_DATE</dateRangeType>
        <downloadFormat>TSV</downloadFormat>
    </reportDefinition>''' % (start, end)

    campaign = slice(0, 1)
    state = slice(1, 2)
    impression_count = slice(2, 3)
    click_count = slice(3, 4)
    cost = slice(4, 5)

    r = requests.post(host, headers=header, data={'__rdxml': __rdxml})
    response = r.content
    # print response
    print 'google finished'

    class GoogleData():
        def __init__(self):
            self.impressions = 0
            self.clicks = 0
            self.cost = 0

    gdn = GoogleData()
    search = GoogleData()

    for line in response.split('\n'):
        parts = line.split('\t')
        # try:
        #     if parts[1] == 'enabled':
        #         print 'Campaign: {}\n\tStatus: {}\n\tImpressions: {}\n\tClicks: {}\n\tCost: {}'.format(
        #             parts[campaign][0],
        #             parts[state][0],
        #             parts[impressions][0],
        #             parts[clicks][0],
        #             float(parts[cost][0]) / 1000000.0)
        # except:
        #     pass
        campaign_name = parts[campaign][0].lower()
        if campaign_name.endswith(('_switch_search', '_switch_gdn')):
            impressions = float(parts[impression_count][0])
            clicks = float(parts[click_count][0])
            cost_rubles = (float(parts[cost][0]) / (1000000.0 * currency))
            if campaign_name.endswith('_switch_search'):
                search.impressions += impressions
                search.clicks += clicks
                search.cost += cost_rubles
            if campaign_name.endswith('_switch_gdn'):
                gdn.impressions += impressions
                gdn.clicks += clicks
                gdn.cost += cost_rubles

    return {'search_impressions': search.impressions,
            'search_clicks': search.clicks,
            'search_cost': search.cost,
            'gdn_impressions': gdn.impressions,
            'gdn_clicks': gdn.clicks,
            'gdn_cost': gdn.cost}


def get_direct_data(start, end):
    """
    For documentation visit https://tech.yandex.ru/direct/doc/dg-v4/examples/python-json-docpage/
    New API access requests are moderated.
    """
    # Adress for sending JSON requests
    url = 'https://api.direct.yandex.ru/v4/json/'
    # OAuth
    token = ''
    # Direct login
    login = ''
    param = {
        'login': login,
        'CampaignIDS': [136],
        'StartDate': start,
        'EndDate': end,
        'Currency': 'RUB'
    }
    # For documentation visit https://tech.yandex.ru/direct/doc/dg-v4/reference/GetSummaryStat-docpage/
    data = {
        'token': token,
        'method': 'GetSummaryStat',
        'locale': 'ru',
        'param': param
    }
    # Convert data to JSON and encode it to UTF-8
    jdata = json.dumps(data, ensure_ascii=False).encode('utf8')
    # Request api
    response = urllib2.urlopen(url, data=jdata)
    # Show the answer for request
    parsed = json.loads(response.read())
    # print json.dumps(parsed, indent=2, sort_keys=True, ensure_ascii=False)
    # Returns following structure:
    """
    {"data": [{
      "CampaignID": 136,
      "ClicksContext": 142, /* Clicks in RSYA(GDN analog by Yandex) */
      "ClicksSearch": 0, /* Clicks in Search */
      "GoalConversionContext": "44.98",
      "GoalConversionSearch": null,
      "GoalCostContext": "8.86",
      "GoalCostSearch": null,
      "SessionDepthContext": "1.25",
      "SessionDepthSearch": null,
      "ShowsContext": 123, /* Shows in RSYA */
      "ShowsSearch": 0, /* Shows in Search */
      "StatDate": "2014-08-20",
      "SumContext": 159.84, /* Spend in RSYA */
      "SumSearch": 0}]}
    """
    if parsed['data']:
        rsya_cost = parsed['data'][0]['SumContext']  # includes VAT
        rsya_clicks = parsed['data'][0]['ClicksContext']
        rsya_impressions = parsed['data'][0]['ShowsContext']
    else:
        rsya_cost = 0
        rsya_clicks = 0
        rsya_impressions = 0

    return {'rsya_impressions': rsya_impressions,
            'rsya_clicks': rsya_clicks,
            'rsya_cost': rsya_cost
            }

# print get_direct_data('2015-08-25', '2015-08-25')


def get_switch_creativeids():
    kullan = re.compile(r'^https?://(www\.)?xxx\.com\.tr/kullan')
    switch_creative_ids = []
    params = {'limit': '1000',
              'fields': 'object_story_spec',
              'access_token': ''}
    url = 'https://graph.facebook.com/v2.4/act_776054839099536/adcreatives'

    while True:
        r = requests.get(url, params=params)
        response = json.loads(r.content)
        # print json.dumps(response, sort_keys=True, indent=4)
        data = response['data']
        page = response['paging']
        for item in data:
            # print json.dumps(item, sort_keys=True, indent=4)
            if 'object_story_spec' in item and 'link_data' in item['object_story_spec'] and 'link' in \
                    item['object_story_spec']['link_data']:
                link = item['object_story_spec']['link_data']['link']
                id = item['id'].encode("utf-8")
                if re.search(kullan, link):
                    switch_creative_ids.append(id)
        if 'next' in page:
            url = page['next']
            params = {}
            # print 'new url', len(switch_ids)
        else:
            return switch_creative_ids


def get_switch_adgroup_ids(switch_ids):
    params = {'limit': '1000',
              'fields': 'creative',
              'access_token': ''}
    url = 'https://graph.facebook.com/v2.4/act_776054839099536/adgroups'
    switch_adgroup_ids = []
    while True:
        r = requests.get(url, params=params)
        response = json.loads(r.content)
        # print json.dumps(response, sort_keys=True, indent=4)
        data = response['data']
        page = response['paging']
        for item in data:
            adgroup_id = item['id']
            creative_id = item['creative']['id']
            if creative_id in switch_ids:
                switch_adgroup_ids.append(adgroup_id)
        if 'next' in page:
            url = page['next']
            params = {}
            # print 'new url', len(switch_ids)
        else:
            return switch_adgroup_ids


def get_facebook_data(start, end, switch_adgroup_ids):
    params = {'time_range': "{since:'%s',until:'%s'}" % (start, end),
              'limit': '1000',
              'fields': 'actions,spend,impressions,adgroup_id,placement',
              'level': 'adgroup',
              'access_token': ''}
    url = 'https://graph.facebook.com/v2.4/act_776054839099536/insights'
    spend = 0
    website_click = 0
    impressions = 0
    placements = {}
    while True:
        r = requests.get(url, params=params)
        response = json.loads(r.content)
        # print json.dumps(response, sort_keys=True, indent=4), '\n\n\n\n\n------'
        for adstat in response['data']:
            adgroup_id = adstat['adgroup_id'].encode("utf-8")
            # campaign_name = adstat['campaign_name'].encode("utf-8")
            adimpression = float(adstat['impressions'])
            adspend = float(adstat['spend'])
            placement = adstat['placement']
            if adgroup_id in switch_adgroup_ids and placement == 'desktop_feed':
                actions = adstat.get('actions')
                if actions:
                    wc = filter(lambda x: x['action_type'] == 'link_click', actions)
                    if wc:
                        website_click += float(wc[0]['value'])
                impressions += adimpression
                spend += adspend
            else:
                pass
        if 'next' in response['paging']:
            url = response['paging']['next']
            params = {}
            print 'next_page'
        else:
            break
    return spend, website_click, impressions


def get_metrica_conversions(start, end):
    url = 'https://beta.api-metrika.yandex.ru/stat/v1/data'
    data = {'dimensions': ['ym:s:UTMSource', 'ym:s:UTMMedium', 'ym:s:UTMCampaign'],
            'metrics': ['ym:s:goal0621users', 'ym:s:goal0621reaches'],
            'date1': start,
            'date2': end,
            'oauth_token': '',
            'pretty': '1',
            'ids': '731'}

    r = requests.get(url, params=data)
    out = r.content
    print 'metrika data received'
    # print json.dumps(json.loads(out), sort_keys=True, indent=2)

    search_conversions = 0.0
    gdn_conversions = 0.0
    rsya_conversions = 0.0
    fb_conversions = 0.0

    for item in json.loads(out)['data']:
        source = item['dimensions'][0]['name']
        medium = item['dimensions'][1]['name']
        campaign = item['dimensions'][2]['name']
        installs = item['metrics'][0]
        if source and medium and campaign:
            source = source.lower()
            medium = medium.lower()
        if medium in ['cpc', 'search', 'gdn'] and source in ['yandex', 'google', 'facebook']:
            if source == 'google':
                if medium == 'gdn':
                    gdn_conversions += installs
                if medium == 'search':
                    search_conversions += installs
            elif source == 'yandex':
                if medium == 'cpc':
                    rsya_conversions += installs
            elif source == 'facebook':
                fb_conversions += installs
    return search_conversions, gdn_conversions, rsya_conversions, fb_conversions


# print get_metrica_conversions('2015-08-25', '2015-08-25')


def get_clickhouse_data(sql_query, connection_timeout=1500, host='http://mtmega01i.yandex.ru:8123/'):
    params = {'query': sql_query,
              'user': 'aydogank',
              'password': 'u8Ab6S4M'
              }

    query_get = urllib.urlencode(params)
    url = host + '?' + query_get
    #    print url
    req = urllib2.Request(url)
    res = urllib2.urlopen(req, timeout=connection_timeout)
    result = res.read()
    return result


def combine_all_data(start, end):
    google_start_date = start.replace('-', '')
    google_end_date = end.replace('-', '')
    #    facebook_start_date = start_date
    #    facebook_end_date = end_date
    metrica_start_date = start_date
    metrica_end_date = end_date

    # take outputs
    metrika_output = get_metrica_conversions(metrica_start_date, metrica_end_date)
    google_output = get_google_data(google_start_date, google_end_date)
    direct_output = get_direct_data(start, end)

    #    switch_creative_ids = get_switch_creativeids()
    #    switch_adgroup_ids =  get_switch_adgroup_ids(switch_creative_ids)
    #    facebook_output = get_facebook_data(facebook_start_date, facebook_end_date, switch_adgroup_ids)
    #    print 'facebook output:', facebook_output

    # CONVERSIONS == NUMBER OF INSTALLS (AGREE IN INLINE)
    search_conversions = metrika_output[0]
    gdn_conversions = metrika_output[1]
    rsya_conversions = metrika_output[2]
    fb_conversions = metrika_output[3]
    total_conversions = search_conversions + gdn_conversions + rsya_conversions + fb_conversions

    # SPEND
    #    fb_spend = facebook_output[0]
    search_spend = round(google_output['search_cost'], 2)
    gdn_spend = round(google_output['gdn_cost'], 2)
    rsya_spend = round(direct_output['rsya_cost'], 2)
    total_spend = search_spend + gdn_spend + rsya_spend

    # IMPRESSIONS
    #    fb_impressions = facebook_output[2]
    search_impressions = google_output['search_impressions']
    gdn_impressions = google_output['gdn_impressions']
    rsya_impressions = direct_output['rsya_impressions']
    total_impressions = search_impressions + gdn_impressions + rsya_impressions

    # CLICKS
    #    fb_clicks = facebook_output[1]
    search_clicks = google_output['search_clicks']
    gdn_clicks = google_output['gdn_clicks']
    rsya_clicks = direct_output['rsya_clicks']
    total_clicks = search_clicks + gdn_clicks + rsya_clicks

    # CPA
    #    fb_cpa = fb_spend / fb_conversion
    try:
        search_cpa = round((search_spend / search_conversions * 1.0), 2)
    except ZeroDivisionError:
        search_cpa = 0.0
    try:
        gdn_cpa = round((gdn_spend / gdn_conversions * 1.0), 2)
    except ZeroDivisionError:
        gdn_cpa = 0.0
    try:
        rsya_cpa = round((rsya_spend / rsya_conversions * 1.0), 2)
    except ZeroDivisionError:
        rsya_cpa = 0.0
    # all_cpa = total_spend / total_conversions

    # CTR
    #    fb_ctr = fb_clicks / fb_impressions
    try:
        search_ctr = round(search_clicks / (search_impressions * 1.0), 4)
    except ZeroDivisionError:
        search_ctr = 0.0
    try:
        gdn_ctr = round(gdn_clicks / (gdn_impressions * 1.0), 4)
    except ZeroDivisionError:
        gdn_ctr = 0.0
    try:
        rsya_ctr = round(rsya_clicks / (rsya_impressions * 1.0), 4)
    except ZeroDivisionError:
        rsya_ctr = 0.0
    # try:
    #     total_ctr = round(total_clicks / (total_impressions * 1.0), 4)
    # except ZeroDivisionError:
    #     total_ctr = 0.0

    # LANDING PAGE CONVERSION RATE
    #    fb_lpcr = fb_conversion / fb_clicks
    try:
        s_lpcr = search_conversions / (search_clicks * 1.0)
    except ZeroDivisionError:
        s_lpcr = 0.0
    try:
        gdn_lpcr = gdn_conversions / (gdn_clicks * 1.0)
    except ZeroDivisionError:
        gdn_lpcr = 0.0
    try:
        rsya_lpcr = rsya_conversions / (rsya_clicks * 1.0)
    except ZeroDivisionError:
        rsya_lpcr = 0.0

    # CPC
    #    fb_cpc = fb_spend / fb_clicks
    try:
        search_cpc = round(search_spend / (search_clicks * 1.0), 2)
    except ZeroDivisionError:
        search_cpc = 0.0
    try:
        gdn_cpc = round(gdn_spend / (gdn_clicks * 1.0), 2)
    except ZeroDivisionError:
        gdn_cpc = 0.0
    try:
        rsya_cpc = round(rsya_spend / (rsya_clicks * 1.0), 2)
    except ZeroDivisionError:
        rsya_cpc = 0.0
    # try:
    #     total_cpc = round(total_spend / (total_clicks * 1.0), 2)
    # except ZeroDivisionError:
    #     total_cpc = 0.0

    # SEARCH HITS
    # clid_hits = get_clid_nonclid_hits(start)['clid_hits']
    # nonclid_hits = get_clid_nonclid_hits(start)['nonclid_hits']
    # clid_hits_share = float(clid_hits) / nonclid_hits

    graph_dict = {'fielddate': start,
                  'search_ctr': search_ctr, 'gdn_ctr': gdn_ctr, 'rsya_ctr': rsya_ctr,
                  'search_cpc': search_cpc, 'gdn_cpc': gdn_cpc, 'rsya_cpc': rsya_cpc,
                  'search_cost': search_spend, 'gdn_cost': gdn_spend, 'rsya_cost': rsya_spend,
                  'search_conversions': search_conversions, 'gdn_conversions': gdn_conversions,
                  'rsya_conversions': rsya_conversions, 'fb_conversions': fb_conversions,
                  'total_conversions': total_conversions,
                  'search_cpa': search_cpa, 'gdn_cpa': gdn_cpa, 'rsya_cpa': rsya_cpa,
                  's_lpcr': s_lpcr, 'gdn_lpcr': gdn_lpcr, 'rsya_lpcr': rsya_lpcr}

    return graph_dict


if __name__ == "__main__":
    old_data = True
    print 'old data', old_data
    if old_data:
        start_date = (datetime.date.today() - datetime.timedelta(1)).strftime('%Y-%m-%d')
        end_date = (datetime.date.today() - datetime.timedelta(1)).strftime('%Y-%m-%d')
        start_date = '2015-08-26'
        end_date = start_date
        while start_date != '2015-08-01':
            try:
                all_data = combine_all_data(start_date, end_date)
                print json.dumps(all_data, sort_keys=True, indent=4)
                start_date = (datetime.datetime.strptime(start_date, '%Y-%m-%d') - datetime.timedelta(1)).strftime(
                    '%Y-%m-%d')
                end_date = start_date
                # start_date = end_date = '2015-07-24'
                print '\n------\n'
                print start_date, 'started'
                exit()
            except:
                time.sleep(10)
                continue
    else:
        start_date = (datetime.date.today() - datetime.timedelta(1)).strftime('%Y-%m-%d')
        end_date = (datetime.date.today() - datetime.timedelta(1)).strftime('%Y-%m-%d')
        all_data = combine_all_data(start_date, end_date)
        print json.dumps(all_data, sort_keys=True, indent=4)
