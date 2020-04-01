kotu_kelimeler = ['amk', 'sikeyim','aq']
sa="hay sikeyim böyle işin ben aq"
sa = sa.split(" ")
for i in range(len(sa)):
    if sa[i] in kotu_kelimeler:
        print(sa[i])