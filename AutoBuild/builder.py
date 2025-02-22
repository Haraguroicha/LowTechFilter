import re
from datetime import datetime, timedelta, timezone

import requests

filterlist = {
    'abp': ['experimental.txt', 'filter.txt', 'PureView/news.txt', 'PureView/news_mobile.txt'],
    'hosts': ['hosts.txt', 'nofarm_hosts.txt']
}
url = 'https://filter.futa.gg/'
tz = timezone(timedelta(hours=+8))
today = datetime.now(tz).date()


class HEAD:
    abp: str = '[Adblock Plus]\n' \
               '! Title: LowTechFilter {name}\n' \
               '! Version: {version}\n' \
               '! Expires: 1 hour\n' \
               '! Homepage: https://t.me/AdBlock_TW\n' \
               '! ----------------------------------------------------------------------\n'
    hosts: str = '! FutaHosts\n' \
                 '! LowTechFilter {name}\n' \
                 '! URL: <https://github.com/FutaGuard/LowTechFilter>\n' \
                 '! Version: {version}\n' \
                 '! --------------------------------------------------\n'


for category in filterlist:
    for filename in filterlist[category]:
        pattern = r'(?<=Version: )(\d+\.\d+\.)(\d+)'

        r = requests.get(url + filename)
        first = None
        version = None
        if r.status_code != 200:
            pass
        else:
            first = '\n'.join(r.text.splitlines()[:5])

        try:
            version = re.findall(pattern, first, re.MULTILINE)[0]
        except:
            # https://www.ptt.cc/bbs/Battlegirlhs/M.1506615677.A.1A4.html
            version = ('2017.0929.', '1')

        dt = datetime.strptime(version[0], '%Y.%m%d.').date()
        newversion = today.strftime('%Y.%m%d.')
        if dt != today:
            newversion += '1'
        else:
            newversion += str(int(version[1]) + 1)

        with open(f'{filename}', 'r') as files:
            data = files.read()
            with open(f'{filename}', 'w') as output:
                heads: str = HEAD().__getattribute__(category)
                newhead = heads.format(
                    name=filename.split('.')[0].replace('_', ' ').replace('/', ' ').title(),
                    version=newversion
                )
                output.write(newhead + data)

            ### SP ###
            # hide farm site from google
            if filename == 'nofarm_hosts.txt':
                domain_list = ''
                for domains in data.splitlines():
                    if not domains.startswith('!'):
                        domain = domains[2:-1]
                        domain_list += 'google.*##div.g:has(div[data-hveid] a[href*="{domain}"])\n'.format(
                            domain=domain
                        )
                heads: str = HEAD().__getattribute__('abp')
                newhead = heads.format(
                    name='hide farm content from google',
                    version=newversion
                )
                with open('hide_farm_from_search.txt', 'w') as f:
                    f.write(newhead + domain_list)

            # hosts to domains
            if filename == 'hosts.txt':
                data = data.splitlines()
                newdata = '\n'.join(data[5:])
                desc = '\n'.join(x.replace('!', '#') for x in data[:5]) + '\n'

                with open('domains.txt', 'w') as output:
                    pattern = r'(?<=^\|\|)\S+\.\S{2,}(?=\^)'
                    desc += '\n'.join(re.findall(pattern, newdata, re.MULTILINE))
                    output.write(desc)
