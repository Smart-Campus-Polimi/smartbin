import GreenGrass

filename = "/Users/drosdesd/Dropbox/edo_repo/smart_campus/foto/newspaper/PAPER_20190225-173052.png"

gg = GreenGrass.GreenGrass()

while True:
    key = raw_input('?')
    gg.getLabels(filename)
