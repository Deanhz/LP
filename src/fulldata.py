
def collectData():
    for id in range(100):
        fin = str(id)
        fout = '{:03d}'.format(int(fin))
        Fout = open(fout, "w")
        for line in open(fin):
            Fout.write(line)
        print("finished:" + fout)


if __name__ == '__main__':
    collectData()
