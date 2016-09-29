import os.path as path
import itertools
from jinja2 import Template

from rulefile import parse_rulefile
from rulelistfile import collect_all_rules, merge_rulelists


def get_rulename(rule):
    return "Q[{}]".format(", ".join(map(str, rule)))


def get_rulestr(rule):
    return "_".join(map(str, rule))


def rule_names(rules):
    names = []

    for rule in rules:
        rulename = get_rulename(rule)
        pagename = 'rule_{}.html'.format("_".join(map(str, rule)))
        names.append((rulename, pagename))

    return names


def get_datafilenames():
    ruledatafilerawtar = "rules_raw.tar.xz"
    ruledatafilenwtar = "rules_nw.tar.xz"

    return (ruledatafilerawtar,
            ruledatafilenwtar)


# Rule page part


def get_filenames(rule):
    rulestr = get_rulestr(rule)
    rulenodesplot = "rule_{}_nodes_weights_cp_{}.svg".format(rulestr, rulestr)
    ruleweightsplot = "rule_{}_nodes_weights_{}.svg".format(rulestr, rulestr)
    ruleweightslogplot = "rule_{}_nodes_weights_log_{}.svg".format(rulestr, rulestr)
    ruledatafiletxt = "rule_{}.txt".format(rulestr)
    ruledatafilecsv = "rule_{}_qr_0.csv".format(rulestr)

    return (rulenodesplot,
            ruleweightsplot,
            ruleweightslogplot,
            ruledatafiletxt,
            ruledatafilecsv)


def generate_rulepage(T, rule, polynomialname, extensiontype):

    rulename = get_rulename(rule)

    rulestr = get_rulestr(rule)

    (rulenodesplot,
     ruleweightsplot,
     ruleweightslogplot,
     ruledatafiletxt,
     ruledatafilecsv) = get_filenames(rule)

    (ruledatafilerawtar,
     ruledatafilenwtar) = get_datafilenames()

    datapath = path.join(ruledatasrcpath, extensiontype, 'rules')

    print(ruledatafiletxt)
    try:
        (startpoly,
         extpolys,
         endpoly,
         allroots,
         allweights) = parse_rulefile(path.join(datapath, ruledatafiletxt))
    except IOError:
        print('WARNING: File not found: {}'.format(ruledatafiletxt))
        (startpoly, extpolys, endpoly, allroots, allweights) = ([], [], [], [[], []], [[], []])

    if len(rule) == 1:
        # No extension, just base rule
        polys = startpoly
    else:
        polys = startpoly + extpolys[1:] + endpoly

    site = T.render(polynomialname=polynomialname,
                    sitepath=sitedstpath,
                    extensiontype=extensiontype,
                    rulename=rulename,
                    polys=polys,
                    rulenodesplot=rulenodesplot,
                    ruleweightsplot=ruleweightsplot,
                    ruleweightslogplot=ruleweightslogplot,
                    nodeballs=allroots[0],
                    weightballs=allweights[0],
                    ruledatafilerawtar=ruledatafilerawtar,
                    ruledatafilenwtar=ruledatafilenwtar)

    rulepagedstpath = path.join(sitedstpath, extensiontype, 'rules')

    with open(path.join(rulepagedstpath, 'rule_{}.html'.format(rulestr)), 'w') as f:
        f.write(site)


def generate_rulepages(ruledatasrcpath, polynomialname, extensiontype):

    rulelistspath = path.join(ruledatasrcpath, extensiontype, 'rulelists')

    rulelists = collect_all_rules(rulelistspath)
    rulelists = merge_rulelists(rulelists)

    with open(path.join(sitesrcpath, 'rule.html.j2'), 'r') as f:
        T = Template(f.read())

    for rule in itertools.chain.from_iterable(rulelists.values()):
        generate_rulepage(T, rule, polynomialname, extensiontype)


# Subindex part


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

    ruledatafilerawtar = "rules_raw.tar.xz"
    ruledatafilenwtar = "rules_nw.tar.xz"

    with open(path.join(sitesrcpath, 'subindex.html.j2'), 'r') as f:
        T = Template(f.read())

    subindex = T.render(polynomialname=polynomialname,
                        sitepath=sitedstpath,
                        extensiontype=extensiontype,
                        allrules=data,
                        ruledatafilerawtar=ruledatafilerawtar,
                        ruledatafilenwtar=ruledatafilenwtar)

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

    siteurl = '/scratch/userdata/raoulb/KronrodExtensions/'

    sitesrcpath = '/u/raoulb/rulerepo/website'
    sitedstpath = siteurl

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

    extensiontypes = [
        'Kronrod_Extensions_Test'
    ]

    polynomialnames = [
        'Test'
    ]

    for polynomialname, extensiontype in zip(polynomialnames, extensiontypes):
        # TODO: Create full dir structure and copy data
        dd = path.join(sitedstpath, extensiontype, 'rules')
        if not os.path.exists(dd):
            os.makedirs(dd)

        generate_rulepages(ruledatasrcpath, polynomialname, extensiontype)

        generate_subindex_new(ruledatasrcpath, polynomialname, extensiontype)

    generate_index(polynomialnames, extensiontypes)
