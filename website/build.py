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


def get_filenames(rule):
    rulestr = get_rulestr(rule)
    ruledatafile = "rule_herm_{}.dat".format(rulestr)
    rulenodesplot = "rule_herm_{}_nodes_weights_cp_{}.png".format(rulestr, rulestr)
    ruleweightsplot = "rule_herm_{}_nodes_weights_{}.png".format(rulestr, rulestr)
    ruleweightslogplot = "rule_herm_{}_nodes_weights_log_{}.png".format(rulestr, rulestr)

    return (ruledatafile,
            rulenodesplot,
            ruleweightsplot,
            ruleweightslogplot)


def generate_rulepage(T, rule, polynomialname):

    rulename = get_rulename(rule)

    rulestr = get_rulestr(rule)

    (ruledatafile,
     rulenodesplot,
     ruleweightsplot,
     ruleweightslogplot) = get_filenames(rule)

    datapath = path.join(ruledatasrcpath, 'rules')

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

    rulepagedstpath = path.join(sitedstpath, polytype, 'rules')

    with open(path.join(rulepagedstpath, 'rule_{}.html'.format(rulestr)), 'w') as f:
        f.write(site)


def generate_pages(polytype, polynomialname):

    RI = read_rules_inventory(ruledatasrcpath)

    with open(path.join(sitesrcpath, 'rule.html.j2'), 'r') as f:
        T = Template(f.read())

    for rule in list(RI):
        print(rule)
        generate_rulepage(T, rule, polynomialname)


def generate_subindex(polytype, polynomialname):

    RI = read_rules_inventory(ruledatasrcpath)
    RI = sorted(list(map(lambda l: list(map(int, l)), RI)))

    rulenames = list(map(get_rulename, RI))

    pages = [path.join(sitedstpath,
                       polytype,
                       'rules',
                       'rule_{}.html'.format("_".join(map(str, rule)))) for rule in RI]

    with open(path.join(sitesrcpath, 'subindex.html.j2'), 'r') as f:
        T = Template(f.read())

    subindex = T.render(polynomialname=polynomialname,
                        rules=zip(rulenames, pages))

    subindexpagedstpath = path.join(sitedstpath, polytype)

    with open(path.join(subindexpagedstpath, 'subindex.html'), 'w') as f:
        f.write(subindex)


if __name__ == '__main__':

    import os

    siteurl = '/u/raoulb'

    sitesrcpath = '/u/raoulb/rulerepo/website'
    sitedstpath = path.join(siteurl, 'ruleweb')

    ruledatasrcpath = '/userdata/raoulb/KronrodExtensions/Kronrod_Extensions_Hermite'

    #polynomialname = "Hermite (physicists')"
    polynomialname = "Hermite (probabilists')"

    polytype = 'hermite_pro'

    dd = path.join(sitedstpath, polytype, 'rules')
    if not os.path.exists(dd):
        os.makedirs(dd)

    generate_pages(polytype, polynomialname)

    generate_subindex(polytype, polynomialname)
