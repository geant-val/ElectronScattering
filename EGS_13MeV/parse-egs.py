import os
import simplejson


def process_file(fn):
    x = []
    y = []
    with open(fn) as f:
        line = f.readline().strip()
        count = int(line)
        for _ in range(count):
            xval, yval = f.readline().strip().split()
            x.append(float(xval))
            y.append(float(yval))

    return x, y


def main():
    mat = ['Al', 'Au', 'Au', 'Be', 'C', 'Not defined', 'Ti']
    for i, fn in enumerate(['Al2.13MeV.ascii', 'Au1.13MeV.ascii', 'Au3.13MeV.ascii', 'Be1.13MeV.ascii',
                            'C1.13MeV.ascii', 'noFoil.13MeV.ascii', 'Ti4.13MeV.ascii']):
        ofn = fn.replace('ascii', 'json')
        x, y = process_file(fn)
        with open(ofn, "w") as f:
            with open("EGS.json") as g:
                json = simplejson.load(g)

            json["metadata"]["targetName"] = mat[i]
            json["chart"]["xValues"] = x
            json["chart"]["yValues"] = y
            json["chart"]["nPoints"] = len(x)

            simplejson.dump(json, f, indent='    ', sort_keys=True)
    return 0


if __name__ == '__main__':
    exit(main())
