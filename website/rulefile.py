import re


def parse_rulefile(filepath):

    rblock = False
    wblock = False
    allroots = []
    allweights = []
    roots = []
    weights = []

    startpoly = []
    extpolys = []
    endpoly = []

    startpolyblock = False
    extpolyblock = False
    endpolyblock = False

    with open(filepath, "r") as F:
        for line in F.readlines():
            if line.startswith("Starting with polynomial:"):
                startpolyblock = True

            elif line.startswith("Extension levels are:"):
                startpolyblock = False
                extpolyblock = True

            elif line.startswith("Ending with final polynomial:"):
                extpolyblock = False
                endpolyblock = True

            elif line.startswith("---"):
                extpolyblock = False
                endpolyblock = False

            elif line.startswith("The nodes are"):
                rblock = True
                wblock = False
                roots = []
                allroots.append(roots)
                continue
            elif line.startswith("The weights are"):
                wblock = True
                rblock = False
                weights = []
                allweights.append(weights)
                continue
            elif (rblock or wblock) and not line.startswith("| "):
                rblock = False
                wblock = False
                continue

            elif startpolyblock:
                startpoly.append(line.split(' : ')[1])

            elif extpolyblock:
                extpolys.append(line.split(' : ')[1])

            elif endpolyblock:
                endpoly.append(line.split(' : ')[1])

            elif rblock:
                M = re.match('.*\((.*)\).*\((.*)\)', line)
                roots.append((M.group(1), M.group(2)))
            elif wblock:
                M = re.match('.*\((.*)\).*\((.*)\)', line)
                weights.append((M.group(1), M.group(2)))

    if not allroots or not allweights:
        raise ValueError("No suitable data found!")

    return (startpoly, extpolys, endpoly, allroots, allweights)
