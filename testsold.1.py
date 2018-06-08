#------------------------------#
# Testes                #
#------------------------------#

from heuristic import fit
from operator import itemgetter, attrgetter
from data import Item, Box, generate_item_list, generate_pareto_list, load_from_file
from sys import argv

def calc_profit(box, tax, min_t=50):
    temp = []
    for b in box:
        temp.append(b.profit_per_box(tax_rate=tax,min_tax=min_t))
    return sum(temp)

def stresstest(itemgen=None, file=None):

    if itemgen == 'normal': my_items = generate_item_list(amount=100,max_size=1000,max_value=100)
    elif itemgen == 'pareto': my_items = generate_pareto_list(amount=100, medium_size=400, medium_value=50, max_size=1000,max_value=100)
    else: my_items = load_from_file(file)
    totalitemvalue = 0
    for i in my_items: totalitemvalue += i.value
    print(totalitemvalue)

    testtaxrate = [0,10,20,30,40,50,60]
    fit_option = ['first','best','worst','avoidtaxes']
    sort_option = [True, False, 'cheapest', 'expensive']

    for t in testtaxrate:
        results = {}
        print("TAX RATE: " + str(t), end=' ')
        for f in fit_option:
            for s in sort_option:
                mybox = fit(my_items,fit=f,sortedlist=s,verbose=False)
                l = len(mybox)
                # n = fit_option.index(f) + (sort_option.index(s)*10)
                n = mybox.used_value
                results[f,s,l,n] = calc_profit(mybox, t)
        for k, v in sorted(results.items(), key=itemgetter(1), reverse=True):
            print(str(k), str(v));break

if __name__ == '__main__':
    if '--random-gen' in argv: generate_item_list(amount=200,max_size=1000,max_value=100,savefile='random.txt');print("Lista Aleatória Gerada")
    if '--pareto-gen' in argv: generate_pareto_list(amount=200, medium_size=400, medium_value=50, max_size=1000,max_value=100,savefile='pareto.txt')
    if '--stress' in argv: stresstest(file=argv[2])
    
    #stresstest('pareto')
    #stresstest('normal')