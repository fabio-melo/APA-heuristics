#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" tests.py - testes de estresse e modo interativo """

from heuristic import *  #pylint: disable=unused-wildcard-import 
from operator import itemgetter, attrgetter
from data import Item, Box, load_from_file, save_to_file
from sys import argv
from IPython import embed


#-----------------------------------------------------------#
# Teste de Estresse de Heurísticas                          #
#-----------------------------------------------------------#

def stresstest(itemgen=None, file=None,taxrate=False):

    if itemgen == 'normal': my_items = generate_item_list(amount=100,max_size=1000,max_value=100)
    elif itemgen == 'pareto': my_items = generate_pareto_list(amount=100, medium_size=400, medium_value=50, max_size=1000,max_value=100)
    else: my_items = load_from_file(file)
    totalitemvalue,totalitemsize = 0,0
    for i in my_items: totalitemvalue += i.value; totalitemsize += i.size
    print(str(totalitemsize) + ' ' + str(totalitemvalue))

    testtaxrate = taxrate if taxrate else [0,10,20,30,40,50,60]
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
               # mysum = 0
               # for x in mybox: mysum += x.used_size # rint(x.used_size, end=' ')
                
                results[f,s,l] = calc_profit(mybox, t)
        for k, v in sorted(results.items(), key=itemgetter(1), reverse=True):
            print(str(k), str(v));break


#-----------------------------------------------------------#
# Métodos Geradores de Instancias                           #
#-----------------------------------------------------------#

def generate_item_list(amount=100, max_size=1000, max_value=100,savefile=False):
    packing_list = []
    for _ in range(amount):
        item_packed = Item(random.randint(1, max_size),random.randint(1, max_value))
        packing_list.append(item_packed)
    if savefile: save_to_file(packing_list, file=savefile)
    return packing_list


def generate_pareto_list(amount=100, medium_value=50, medium_size=300, max_size=1000, max_value=100,verbose=False,savefile=False):
    packing_list = []
    percent20, percent80 = int((amount/100)*20), int((amount/100)*80)
    for _ in range(percent80):
        item_packed = Item(random.randint(1, medium_size),random.randint(1, medium_value))
        packing_list.append(item_packed)
    for _ in range(percent20):
        item_packed = Item(random.randint(medium_size, max_size),random.randint(medium_value, max_value))
        packing_list.append(item_packed)
    if verbose: 
        for i in packing_list: print(str(i.value),str(i.size))

    if savefile: save_to_file(packing_list, file=savefile)
    return packing_list


def test(file="pareto.txt", algo='top_to_bottom', taxrate=10, verbose=True):
     #test(file="random2.txt", algo="repack", taxrate=20)
    b = multifit(file,taxrate=taxrate, verbose=verbose)
    nb = vnd(b,taxrate=taxrate,algo=algo,verbose=verbose)
    return nb

if __name__ == '__main__':
    if '--random-gen' in argv: generate_item_list(amount=200,max_size=1000,max_value=100,savefile='random.txt');print("Lista Aleatória Gerada")
    if '--pareto-gen' in argv: generate_pareto_list(amount=200, medium_size=400, medium_value=50, max_size=1000,max_value=100,savefile='pareto.txt')
    if '--stress' in argv: stresstest(file=argv[2])
    if '-i' in argv: embed()
    #stresstest('pareto')
    #stresstest('normal')