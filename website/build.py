import os.path as path
from jinja2 import Template

from rulefile import parse_rulefile


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


def generate_subindex(ruledatasrcpath, polynomialname, extensiontype):

    RI = read_rules_inventory(ruledatasrcpath)
    RI = sorted(list(map(lambda l: list(map(int, l)), RI)))

    rulenames = list(map(get_rulename, RI))

    pages = [path.join(sitedstpath,
                       extensiontype,
                       'rules',
                       'rule_{}.html'.format("_".join(map(str, rule)))) for rule in RI]

    with open(path.join(sitesrcpath, 'subindex.html.j2'), 'r') as f:
        T = Template(f.read())

    subindex = T.render(polynomialname=polynomialname,
                        rules=zip(rulenames, pages))

    subindexpagedstpath = path.join(sitedstpath, extensiontype)

    with open(path.join(subindexpagedstpath, 'subindex.html'), 'w') as f:
        f.write(subindex)


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

    for polynomialname, extensiontype in zip(polynomialnames, extensiontypes):
        dd = path.join(sitedstpath, extensiontype, 'rules')
        if not os.path.exists(dd):
            os.makedirs(dd)

        q = path.join(ruledatasrcpath, extensiontype)

        generate_rulepages(q, polynomialname, extensiontype)

        generate_subindex(q, polynomialname, extensiontype)

    generate_index(polynomialnames, extensiontypes)
