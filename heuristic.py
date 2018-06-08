#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" heuristics.py - heurísticas e etc """

import sys, random, copy
from operator import itemgetter, attrgetter
from data import Item, Box, load_from_file

#------------------------------------------------------------------------------#
#   Funções Auxiliares                                                         #
# -----------------------------------------------------------------------------#


def print_boxes(boxes):
    """ Imprime os Valores das caixas de uma lista de caixas """
    for b in boxes: print("(" + str(b.used_size) + "," + str(b.total_value) + ")",end=" ")
    print()

def calc_profit(boxes, tax=20, min_t=50):
    """ Função de Avalição: Calcula o lucro de uma lista de caixas """
    temp = []
    for b in boxes:
        temp.append(b.profit_per_box(tax_rate=tax,min_tax=min_t))
    return sum(temp)


#------------------------------------------------------------------------------#
#   Heurística de Construção                                                   #
# -----------------------------------------------------------------------------#


def fit(items, fit='first', sortedlist=False, box_size=1000, verbose=False, min_tax=50):
    """ Heuristicas para Construção de Soluções \n
    Ordenação de Caixa:
        False = ordem de chegada
        True = ordenado do maior para o menor
        'cheapest' - do item mais barato, para o mais caro
        'expensive' - do item mais caro para o mais barato
    Heurísticas Disponíveis:
        'first' - First Fit (coloca o item na primeira caixa disponível que o couber)
        'best' - Best Fit (coloca o item na caixa que tiver menos espaço disponivel e couber) 
        'worst' - Worst Fit (coloca o item na caixa que tiver mais espaço disponível e couber)
        'avoidtaxes' - Tenta colocar o máximo de itens em caixas cujo valor total não é tarifado)
     """
    # ordem da lista 
    if sortedlist: items = sorted(items,key=attrgetter('size'), reverse=True)
    if sortedlist == 'cheapest': items = sorted(items,key=attrgetter('value'))
    if sortedlist == 'expensive': items = sorted(items,key=attrgetter('value'), reverse=True)


    boxes = []

    if fit in ("first", "best", "worst"):
        for item in items:
            if fit == 'best' and boxes: 
                boxes = sorted(boxes, key=attrgetter('used_size'))
            if fit == 'worst' and boxes: 
                boxes = sorted(boxes, reverse=True, key=attrgetter('used_size'))        
            
            for b in boxes:
                if b.can_add(item): b.add_item(item); break
            else:
                new_box = Box(box_size)
                new_box.add_item(item)
                boxes.append(new_box)

    elif fit in ("avoidtaxes"):
        cheaper_items, expensive_items = [], []
        cheap_boxes, expensive_boxes = [],[]
        for item in items:
            if item.value <= min_tax:
                cheaper_items.append(item)
            else: 
                expensive_items.append(item)
        

        for item in cheaper_items:
            for b in cheap_boxes:
                if b.can_add_without_tax(item,min_tax) and b.used_size <= min_tax: 
                    b.add_item(item); break
            else:
                new_box = Box(box_size)
                new_box.add_item(item)
                cheap_boxes.append(new_box)
        for item in expensive_items:
            for b in expensive_boxes:
                if b.can_add(item): b.add_item(item); break
            else:
                new_box = Box(box_size)
                new_box.add_item(item)
                expensive_boxes.append(new_box)
        boxes = cheap_boxes + expensive_boxes

    if verbose: 
        print(str(fit) + " fit: " + str(sortedlist) + ' ' + str(len(boxes)))
        for b in boxes: print(str(b.used_size) + '-' + str(b.total_value),end='|')
        print()

    return boxes


#------------------------------------------------------------------------------#
#   Busca de Heurística Ótima                                                  #
# -----------------------------------------------------------------------------#


def multifit(file=None,taxrate=10,verbose=False):
    """ Executa todas Heurísticas com a lista de objetos definidos, utilizando o
    valor da taxa definida, e retorna o melhor variante do algorítimo
    
    Lista de Caixas em armazenada em n[1][1] """
    my_items = load_from_file(file)

    if verbose:
        totalitemvalue,totalitemsize = 0,0
        for i in my_items: totalitemvalue += i.value; totalitemsize += i.size
        print(str(totalitemvalue) + ' ' + str(totalitemsize))
        print("TAX RATE: " + str(taxrate), end=' ')

    fit_option = ['first','best','worst','avoidtaxes']
    sort_option = [True, False, 'cheapest', 'expensive']

    results,finalresult = {},{}


    for f in fit_option:
        for s in sort_option:
            mybox = fit(my_items,fit=f,sortedlist=s,verbose=False)
            l = len(mybox)
            results[f,s,l] = calc_profit(mybox, taxrate), mybox

    
    finalresult = max(results.items(), key=itemgetter(1))

    if verbose: print(str(finalresult[0]) + str(finalresult[1][0]))
    return finalresult


#------------------------------------------------------------------------------#
#   Vizinhança Variável                                                        #
# -----------------------------------------------------------------------------#


def nbhood(list_of_boxes, kind='r', algo='top_to_bottom', \
           taxrate=10, randomseed="i_wish_i_was_dead", verbose=False):
    """ Recebe uma Solução (Lista de Caixas) e aplica a heurística definida. """
    #Ordem das Caixas
    order = ['unordered','biggest','smallest','expensive','cheapest','shuffle']
    
    nb_results = {}
    nb_results['original','original','original'] = calc_profit(list_of_boxes, taxrate)


    if algo == 'top_to_bottom':
        
        # desempacotar primeira caixa a transforma em duas de tamanho menor
        # só trás melhorias tangiveis se a heuristica usada for first,best ou worst fit
        
        boxes_ord = copy.deepcopy(list_of_boxes)
        for o in order:
            if o == 'unordered': pass
            if o == 'biggest': boxes_ord = sorted(boxes_ord, key=lambda x: x.used_size, reverse=True)
            if o == 'smallest': boxes_ord = sorted(boxes_ord, key=lambda x: x.used_size)
            if o == 'expensive': boxes_ord = sorted(boxes_ord, key=lambda x: x.total_value, reverse=True)
            if o == 'cheapest': boxes_ord = sorted(boxes_ord, key=lambda x: x.total_value)
            if o == 'shuffle': random.seed(randomseed); random.shuffle(boxes_ord)
            


            for box in range(len(boxes_ord)):
                boxes = copy.deepcopy(boxes_ord)
                sortbox = boxes[box].items
                #sortbox = sorted(sortbox, key=lambda x: x.size) 
                # partir em duas
                mini1 = sortbox[:len(sortbox)//2]  #pegar o primeira parte
                mini2 = sortbox[len(sortbox)//2:] #pegar a segunda parte
                boxes.pop(box)
                minibox1,minibox2 = Box(), Box()
                for m in mini1:
                    minibox1.add_item(m)
                for m in mini2:
                    minibox2.add_item(m)
                
                boxes.append(minibox1)
                boxes.append(minibox2)

                nb_results[algo,o,box] = calc_profit(boxes, taxrate), copy.deepcopy(boxes)

    if algo == "repack":
        # tenta juntar caixas, essa heurista só faz efeito no algoritimo avoidtaxes


        boxes_ord = copy.deepcopy(list_of_boxes)
        for o in order:
            if o == 'unordered': pass
            if o == 'biggest': boxes_ord = sorted(boxes_ord, key=lambda x: x.used_size, reverse=True)
            if o == 'smallest': boxes_ord = sorted(boxes_ord, key=lambda x: x.used_size)
            if o == 'expensive': boxes_ord = sorted(boxes_ord, key=lambda x: x.total_value, reverse=True)
            if o == 'cheapest': boxes_ord = sorted(boxes_ord, key=lambda x: x.total_value)
            if o == 'shuffle': random.seed(randomseed); random.shuffle(boxes_ord)
            
            for box in range(len(boxes_ord)):
                boxes = copy.deepcopy(boxes_ord)
                newbox = boxes[box]
                boxes.pop(box)

                add_phase = True

                while add_phase:
                    for i in range(len(boxes)):
                        if newbox.used_size + boxes[i].used_size <= newbox.total_size:
                            newbox.items += boxes[i].items
                            newbox.used_size += boxes[i].used_size
                            newbox.total_value += boxes[i].total_value
                            boxes.pop(i);break
                    else: add_phase = False
                if newbox.items: boxes.append(newbox)
                nb_results[algo,o,box] = calc_profit(boxes, taxrate), copy.deepcopy(boxes)
    finalresult = max(nb_results.items(), key=itemgetter(1))[0]
    if verbose: print(finalresult)
    return finalresult


def vnd(list_of_boxes, taxrate=20, algo='top_to_bottom'):
    
    best_solution = calc_profit(list_of_boxes, taxrate) #calcular o valor da solução inicial
    
    it = 0

    while True:
        new_best = nbhood(l, algo=algo) 
        if new_best[0][0] == best_solution: break
        it += 1
    
    return



