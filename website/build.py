import os.path as path
import itertools
import asciimathml
from xml.etree.ElementTree import tostring
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


def get_datafilenames():
    ruledatafilerawtar = "rules_raw.tar.xz"
    ruledatafilenwtar = "rules_nw.tar.xz"

    return (ruledatafilerawtar,
            ruledatafilenwtar)


# Rule page part


def generate_rulepage(sitedatasrcpath, sitedstpath, extensiontype, polynomialname, T, rule):

    rulename = get_rulename(rule)

    rulestr = get_rulestr(rule)

    (rulenodesplot,
     ruleweightsplot,
     ruleweightslogplot,
     ruledatafiletxt,
     ruledatafilecsv) = get_filenames(rule)

    (ruledatafilerawtar,
     ruledatafilenwtar) = get_datafilenames()

    datapath = path.join(sitedatasrcpath, extensiontype, 'rules')

    print(ruledatafiletxt)
    try:
        (startpoly,
         extpolys,
         endpoly,
         allroots,
         allweights) = parse_rulefile(path.join(datapath, ruledatafiletxt))
    except IOError:
        print('WARNING: File not found: {}'.format(ruledatafiletxt))
        _, extpolys, endpoly, allroots, allweights = [], [], [], [[], []], [[], []]

    polynomials = extpolys + endpoly
    polynomials = [tostring(asciimathml.parse(p)).decode('ascii') for p in polynomials]

    site = T.render(polynomialname=polynomialname,
                    rulename=rulename,
                    polynomials=polynomials,
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


def generate_rulepages(sitesrcpath, sitedatasrcpath, sitedstpath, extensiontype, polynomialname):

    rulelistspath = path.join(sitedatasrcpath, extensiontype, 'rulelists')

    rulelists = collect_all_rules(rulelistspath)
    rulelists = merge_rulelists(rulelists)

    with open(path.join(sitesrcpath, 'rule.html.j2'), 'r') as f:
        T = Template(f.read())

    for rule in itertools.chain.from_iterable(rulelists.values()):
        generate_rulepage(sitedatasrcpath, sitedstpath, extensiontype, polynomialname, T, rule)


# Subindex part


def prepare_ruledata(allrules):
    data = {}

    for rmd, rules in allrules.items():
        data[rmd] = rule_names(rules)

    return data


def generate_subindex(sitesrcpath, sitedatasrcpath, sitedstpath, extensiontype, polynomialname):

    rulelistspath = path.join(sitedatasrcpath, extensiontype, 'rulelists')

    rulelists = collect_all_rules(rulelistspath)
    rulelists = merge_rulelists(rulelists)

    data = prepare_ruledata(rulelists)

    ruledatafilerawtar = "rules_raw.tar.xz"
    ruledatafilenwtar = "rules_nw.tar.xz"

    with open(path.join(sitesrcpath, 'subindex.html.j2'), 'r') as f:
        T = Template(f.read())

    subindex = T.render(polynomialname=polynomialname,
                        allrules=data,
                        ruledatafilerawtar=ruledatafilerawtar,
                        ruledatafilenwtar=ruledatafilenwtar)

    subindexpagedstpath = path.join(sitedstpath, extensiontype)

    with open(path.join(subindexpagedstpath, 'subindex.html'), 'w') as f:
        f.write(subindex)


# Main Index part


def generate_index(sitesrcpath, sitedstpath, extensiontypes, polynomialnames):

    pages = [path.relpath(path.join(sitedstpath,
                                    extensiontype,
                                    'subindex.html'), sitedstpath) for extensiontype in extensiontypes]

    with open(path.join(sitesrcpath, 'index.html.j2'), 'r') as f:
        T = Template(f.read())

    index = T.render(subindices=zip(polynomialnames, pages))

    with open(path.join(sitedstpath, 'index.html'), 'w') as f:
        f.write(index)


if __name__ == '__main__':

    import os
    import shutil

    sitedstpath = '/userdata/raoulb/KEL'

    sitesrcpath = '/u/raoulb/rulerepo/website'
    sitedatasrcpath = '/userdata/raoulb/KELDATA'

    extensiontypes = [
        'Kronrod_Extensions_Legendre',
        'Kronrod_Extensions_ChebyshevT',
        'Kronrod_Extensions_ChebyshevU',
        'Kronrod_Extensions_Laguerre',
        'Kronrod_Extensions_Hermite',
        'Kronrod_Extensions_HermitePro'
    ]

    polynomialnames = [
        'Legendre',
        'Chebyshev T (first kind)',
        'Chebyshev U (second kind)',
        'Laguerre',
        'Hermite (physicists\')',
        'Hermite (probabilists\')'
    ]

    assert path.exists(sitedstpath)

    for polynomialname, extensiontype in zip(polynomialnames, extensiontypes):
        # Create directory structure
        for subdir in ('rules', 'data', 'plots'):
            dd = path.join(sitedstpath, extensiontype, subdir)
            if not os.path.exists(dd):
                os.makedirs(dd)

        # Copy static files
        spath = path.join(sitedatasrcpath, extensiontype, 'plots')
        for file in os.listdir(spath):
            shutil.copy(path.join(spath, file),
                        path.join(sitedstpath, extensiontype, 'plots'))

        for datafile in get_datafilenames():
            shutil.copy(path.join(sitedatasrcpath, extensiontype, 'data', datafile),
                        path.join(sitedstpath, extensiontype, 'data'))

        # Generate pages
        generate_rulepages(sitesrcpath, sitedatasrcpath, sitedstpath, extensiontype, polynomialname)

        generate_subindex(sitesrcpath, sitedatasrcpath, sitedstpath, extensiontype, polynomialname)

    generate_index(sitesrcpath, sitedstpath, extensiontypes, polynomialnames)
