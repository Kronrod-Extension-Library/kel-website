import os.path as path
import re
import itertools
from jinja2 import Template

from rulefile import parse_rulefile
from rulelistfile import get_rulelist


# Rule page part


def read_rules_inventory(datapath, datafile='all_rules.dat'):
    with open(path.join(datapath, datafile)) as f:
        rules = f.readlines()
    return map(lambda s: s.strip().split(' '), rules)


def get_rulename(rule):
    return "Q[{}]".format(", ".join(map(str, rule)))


def get_rulestr(rule):
    return "_".join(map(str, rule))


def get_filenames(rule, ruletype):
    rulestr = get_rulestr(rule)
    ruledatafile = "rule_{}_{}.dat".format(ruletype, rulestr)
    rulenodesplot = "rule_{}_{}_nodes_weights_cp_{}.png".format(ruletype, rulestr, rulestr)
    ruleweightsplot = "rule_{}_{}_nodes_weights_{}.png".format(ruletype, rulestr, rulestr)
    ruleweightslogplot = "rule_{}_{}_nodes_weights_log_{}.png".format(ruletype, rulestr, rulestr)

    return (ruledatafile,
            rulenodesplot,
            ruleweightsplot,
            ruleweightslogplot)


def generate_rulepage(T, rule, polynomialname, extensiontype):

    rulename = get_rulename(rule)

    rulestr = get_rulestr(rule)

    (ruledatafile,
     rulenodesplot,
     ruleweightsplot,
     ruleweightslogplot) = get_filenames(rule, ext2abbr[extensiontype])

    datapath = path.join(ruledatasrcpath, extensiontype, 'rules')

    (startpoly,
     extpolys,
     endpoly,
     allroots,
     allweights) = parse_rulefile(path.join(datapath, ruledatafile))

    if len(rule) == 1:
        # No extension, just base rule
        polys = startpoly
    else:
        polys = startpoly + extpolys[1:] + endpoly

    site = T.render(polynomialname=polynomialname,
                    rulename=rulename,
                    polys=polys,
                    rulenodesplot=path.join(datapath, rulenodesplot),
                    ruleweightsplot=path.join(datapath, ruleweightsplot),
                    ruleweightslogplot=path.join(datapath, ruleweightslogplot),
                    nodeballs=allroots[0],
                    weightballs=allweights[0])

    rulepagedstpath = path.join(sitedstpath, extensiontype, 'rules')

    with open(path.join(rulepagedstpath, 'rule_{}.html'.format(rulestr)), 'w') as f:
        f.write(site)


def generate_rulepages(ruledatasrcpath, polynomialname, extensiontype):

    RI = read_rules_inventory(ruledatasrcpath)

    with open(path.join(sitesrcpath, 'rule.html.j2'), 'r') as f:
        T = Template(f.read())

    for rule in list(RI):
        print(rule)
        generate_rulepage(T, rule, polynomialname, extensiontype)


# Subindex part


def collect_all_rules(rulelistspath):

    allrules = {}

    for file in os.listdir(rulelistspath):
        print(file)
        if file.startswith('rules_'):
            m = re.match('rules_n(.*)_maxp(.*)_maxrec(.*).txt', file)
            datum = tuple(map(int, (m.group(1), m.group(2), m.group(3))))
            allrules[datum] = get_rulelist(path.join(rulelistspath, file))

    return allrules


def merge_rulelists(allrules):

    mergedrules = {}

    key = lambda x: x[0]
    for g, si in itertools.groupby(sorted(allrules.keys(), key=key), key):
        pmax = 0
        rmax = 0
        rules = []

        for i in si:
            n, p, r = i
            pmax = max(pmax, p)
            rmax = max(rmax, r)
            rules += allrules[i]

        mergedrules[(g, pmax, rmax)] = sorted(list(set(rules)))

    return mergedrules


def rule_names(rules):
    names = []

    for rule in rules:
        rulename = get_rulename(rule)
        pagename = 'rule_{}.html'.format("_".join(map(str, rule)))
        names.append((rulename, pagename))

    return names


def prepare_ruledata(allrules):
    data = {}

    for rmd, rules in allrules.items():
        data[rmd] = rule_names(rules)

    return data


def generate_subindex_new(ruledatasrcpath, polynomialname, extensiontype):

    rulelistspath = path.join(ruledatasrcpath, extensiontype, 'rulelists')

    rulelists = collect_all_rules(rulelistspath)
    rulelists = merge_rulelists(rulelists)

    data = prepare_ruledata(rulelists)

    with open(path.join(sitesrcpath, 'subindex.html.j2'), 'r') as f:
        T = Template(f.read())

    subindex = T.render(polynomialname=polynomialname,
                        sitepath=sitedstpath,
                        extensiontype=extensiontype,
                        allrules=data)

    subindexpagedstpath = path.join(sitedstpath, extensiontype)

    with open(path.join(subindexpagedstpath, 'subindex.html'), 'w') as f:
        f.write(subindex)


# Main Index part


def generate_index(polynomialnames, extensiontypes):

    pages = [path.join(sitedstpath,
                       extensiontype,
                       'subindex.html') for extensiontype in extensiontypes]


    with open(path.join(sitesrcpath, 'index.html.j2'), 'r') as f:
        T = Template(f.read())

    index = T.render(subindices=zip(polynomialnames, pages))

    indexpagedstpath = path.join(sitedstpath)

    with open(path.join(indexpagedstpath, 'index.html'), 'w') as f:
        f.write(index)


if __name__ == '__main__':

    import os

    siteurl = '/u/raoulb'

    sitesrcpath = '/u/raoulb/rulerepo/website'
    sitedstpath = path.join(siteurl, 'ruleweb')

    ruledatasrcpath = '/userdata/raoulb/KronrodExtensions/'

    extensiontypes = [
        'Kronrod_Extensions_Legendre',
        'Kronrod_Extensions_ChebyshevT',
        'Kronrod_Extensions_ChebyshevU',
        'Kronrod_Extensions_Laguerre',
        'Kronrod_Extensions_Hermite']

    polynomialnames = [
        'Legendre',
        'Chebyshev T (first kind)',
        'Chebyshev U (second kind)',
        'Laguerre',
        'Hermite (probabilists\')']

    ext2abbr = {'Kronrod_Extensions_Legendre': 'leg',
                'Kronrod_Extensions_ChebyshevT': '',
                'Kronrod_Extensions_ChebyshevU': '',
                'Kronrod_Extensions_Laguerre': 'lag',
                'Kronrod_Extensions_Hermite': 'herm'}

    extensiontypes = [
        'Kronrod_Extensions_Test'
    ]

    polynomialnames = [
        'Test'
    ]

    ext2abbr = {'Kronrod_Extensions_Test': 'test'}

    for polynomialname, extensiontype in zip(polynomialnames, extensiontypes):
        dd = path.join(sitedstpath, extensiontype, 'rules')
        if not os.path.exists(dd):
            os.makedirs(dd)

        q = path.join(ruledatasrcpath, extensiontype)

        #generate_rulepages(q, polynomialname, extensiontype)

        generate_subindex_new(ruledatasrcpath, polynomialname, extensiontype)

    generate_index(polynomialnames, extensiontypes)
