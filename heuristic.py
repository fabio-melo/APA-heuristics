#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" heuristics.py - heurísticas e etc """

import sys, random, copy
from operator import itemgetter, attrgetter
from data import Item, Box, load_from_file, Result

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

    results = []


    for f in fit_option:
        for s in sort_option:
            mybox = fit(my_items,fit=f,sortedlist=s,verbose=False)
            res = Result(list_of_boxes=mybox, fit_order=f,sort_order=s,profit=calc_profit(mybox,taxrate),box_amount=len(mybox))
            results.append(res)

    results = sorted(results, key=attrgetter('profit'),reverse=True)
    finalresult = results[0]
    if verbose: finalresult.print_result_h()
    return finalresult


#------------------------------------------------------------------------------#
#   Vizinhança Variável                                                        #
# -----------------------------------------------------------------------------#


def nbhood(result_h, algo='top_to_bottom', \
           taxrate=10, randomseed="i_wish_i_was_dead", verbose=False, meta=False):
    """ Recebe uma Solução (Lista de Caixas) e aplica a heurística definida. """
    #Ordem das Caixas
    order = ['unordered','shuffle'] #'smallest','expensive','biggest','cheapest',
    results = []
    results.append(result_h)
    boxes_ord = copy.deepcopy(result_h.list_of_boxes)
    

    if algo == 'top_to_bottom':
        
        # desempacotar primeira caixa a transforma em duas de tamanho menor
        # só trás melhorias tangiveis se a heuristica usada for first,best ou worst fit
        
        for o in order:
            if o == 'unordered': pass
            #if o == 'biggest': boxes_ord = sorted(boxes_ord, key=lambda x: x.used_size, reverse=True)
            #if o == 'smallest': boxes_ord = sorted(boxes_ord, key=lambda x: x.used_size)
            #if o == 'expensive': boxes_ord = sorted(boxes_ord, key=lambda x: x.total_value, reverse=True)
            #if o == 'cheapest': boxes_ord = sorted(boxes_ord, key=lambda x: x.total_value)
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
                res = Result(list_of_boxes=copy.deepcopy(boxes), nb_algo=algo, \
                            nb_order=o, nb_pos=box, box_amount=len(boxes), profit=calc_profit(boxes,taxrate), \
                            fit_order=result_h.fit_order, sort_order=result_h.sort_order)                        
                results.append(res)

    if algo == "repack":
        # tenta juntar caixas, essa heurista só faz efeito no algoritimo avoidtaxes

        for o in order:
            if o == 'unordered': pass
            #if o == 'biggest': boxes_ord = sorted(boxes_ord, key=lambda x: x.used_size, reverse=True)
            #if o == 'smallest': boxes_ord = sorted(boxes_ord, key=lambda x: x.used_size)
            #if o == 'expensive': boxes_ord = sorted(boxes_ord, key=lambda x: x.total_value, reverse=True)
            #if o == 'cheapest': boxes_ord = sorted(boxes_ord, key=lambda x: x.total_value)
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
                res = Result(list_of_boxes=copy.deepcopy(boxes), nb_algo=algo, \
                            nb_order=o, nb_pos=box, box_amount=len(boxes), profit=calc_profit(boxes,taxrate), \
                            fit_order=result_h.fit_order, sort_order=result_h.sort_order)                        
                results.append(res)


    results = sorted(results, key=attrgetter('profit'),reverse=True)
    if verbose: 
        for i in range(5):
            results[i].print_result()
        print("Melhor Resultado da Vizinhança"); results[0].print_result()        
    finalresult = results[0]

    if meta: return results
    else: return finalresult


def vnd(solution, taxrate=10, algo='top_to_bottom', randomseed="i_wish_i_was_dead",\
        verbose = False):
    old_profit = solution.profit    
    it = 0

    while True:
        if verbose: print("> Visitando Vizinhança " + str(it+1))
        new_result = nbhood(solution, algo=algo, taxrate=taxrate, randomseed=randomseed,\
                            verbose=verbose)
        if new_result.profit > solution.profit:
            solution = new_result
            it += 1
        else: break
    if verbose:
        print()
        print(">> Melhor Resultado Final:")
        solution.print_result()
        print("Melhoria: " + str(old_profit) + " ---> " + str(solution.profit) + " (+" + str(solution.profit - old_profit) + ")")
        print("Vizinhanças Visitadas para geração do resultado: " + str(it))

    return solution



def smarter_vnd(solutions, taxrate=10, algo='top_to_bottom', randomseed="i_wish_i_was_dead",\
        verbose = False):
    
    old_profit = solutions[0].profit
    optimal_solution = solutions[0]
    it,bk = 0,0

    while solutions:
        if verbose: print("> Visitando Vizinhança " + str(it+1))
        new_solutions = nbhood(solutions[0], algo=algo, taxrate=taxrate, randomseed=randomseed,\
                            verbose=verbose, meta=True)

        if new_solutions[0].profit > optimal_solution.profit:
            solutions = new_solutions
            optimal_solution = solutions[0]
            it += 1
            bk = 0
        else:
            bk += 1
            if bk == 10: break
            print("Fazendo Backtracking: " + str(bk)) 
            solutions.pop(0)

            
    if verbose:
        print()
        print(">> Melhor Resultado Final:")
        optimal_solution.print_result()
        print("Melhoria: " + str(old_profit) + " ---> " + str(optimal_solution.profit) + " (+" + str(optimal_solution.profit - old_profit) + ")")
        print("Vizinhanças Visitadas para geração do resultado: " + str(it))

    return solutions



