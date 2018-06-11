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

def calc_profit(boxes, tax=10, min_t=50):
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
        'avoidtaxes' - (Tenta colocar o máximo de itens em caixas cujo valor total de cada caixa não é taxado)
     """
    # Primeiro Passo: Ordena a lista da forma especificada 
    if sortedlist: items = sorted(items,key=attrgetter('size'), reverse=True)
    if sortedlist == 'cheapest': items = sorted(items,key=attrgetter('value'))
    if sortedlist == 'expensive': items = sorted(items,key=attrgetter('value'), reverse=True)

    boxes = [] # crio a lista de caixas onde irei guardar cada caixa

    if fit in ("first", "best", "worst"): #se uma dessas heuristicas for escolhida, entra nesse loop
        for item in items: #itera todos os itens da lista
            if fit == 'worst' and boxes: #organiza as caixas com as mais cheias primeiro
                boxes = sorted(boxes, key=attrgetter('used_size')) 
            if fit == 'best' and boxes: #organiza as caixas com as menos cheias primeiro
                boxes = sorted(boxes, reverse=True, key=attrgetter('used_size')) 
            #caso não entre nos ifs anteriores, é usado ordem de chegada (first-fit)

            for b in boxes:
                if b.can_add(item): b.add_item(item); break #tenta colocar o item na primeira caixa que couber, e para.
            else:
                new_box = Box(box_size) # caso não caiba em nenhuma, cria uma nova caixa
                new_box.add_item(item)  # e adiciona o item nela
                boxes.append(new_box) # e a adiciona na lista de caixas

    elif fit in ("avoidtaxes"): #heuristica de evitar taxas
        cheaper_items, expensive_items = [], [] #divido a entrada em duas listas, uma para os itens mais baratos, outra para os mais caros
        cheap_boxes, expensive_boxes = [],[] #crio duas caixas, uma para os itens baratos, outra para os caros
        for item in items:
            if item.value <= min_tax: #caso o item seja barato, vai para a caixa dos baratos
                cheaper_items.append(item)
            else: #caso contrário, vai para a outra caixa
                expensive_items.append(item)
        

        for item in cheaper_items: # trabalhando com a caixa dos baratos
            for b in cheap_boxes:
                if b.can_add_without_tax(item,min_tax) and b.used_size <= min_tax: 
                    b.add_item(item); break #se posso adicionar sem taxa, adiciono o item
            else:
                new_box = Box(box_size) #caso contrário, crio uma caixa e adiciono o item nela
                new_box.add_item(item)
                cheap_boxes.append(new_box)
        for item in expensive_items:
            for b in expensive_boxes: #para os itens mais caros, faz o mesmo procedimento dos outros algorítimos
                if b.can_add(item): b.add_item(item); break
            else:
                new_box = Box(box_size)
                new_box.add_item(item)
                expensive_boxes.append(new_box)
        boxes = cheap_boxes + expensive_boxes # junta as duas listas de caixa

    if verbose: #se verboso, imprime o resultado
        print(str(fit) + " fit: " + str(sortedlist) + ' ' + str(len(boxes)))
        for b in boxes: print(str(b.used_size) + '-' + str(b.total_value),end='|')
        print()

    return boxes #retorna a lista final das caixas


#------------------------------------------------------------------------------#
#   Busca de Heurística Ótima                                                  #
# -----------------------------------------------------------------------------#


def multifit(file=None,taxrate=10,verbose=False):
    """ Executa todas Heurísticas com a lista de objetos definidos, utilizando o
    valor da taxa definida, e retorna o melhor variante do algorítimo
    """
    my_items = load_from_file(file)

    if verbose: #imprime alguns detalhes, caso verboso
        totalitemvalue,totalitemsize = 0,0
        for i in my_items: totalitemvalue += i.value; totalitemsize += i.size
        print("Itens: Valor: " + str(totalitemvalue) + " Tamanho:" + str(totalitemsize) + " Taxa: " + str(taxrate))

    fit_option = ['first','best','worst','avoidtaxes'] #todas as opções de heuristicas do fit
    sort_option = [True, False, 'cheapest', 'expensive'] #todas as opções de ordenação do fit

    results = [] #lista dos resultados


    for f in fit_option: #para cada heuristica
        for s in sort_option: #para cada ordenação
            mybox = fit(my_items,fit=f,sortedlist=s,verbose=False) #executa a heuristica
            res = Result(list_of_boxes=mybox, fit_order=f,sort_order=s, \
                         profit=calc_profit(mybox,taxrate),box_amount=len(mybox)) #salva o resultado em um objeto Result
            results.append(res) # e coloca na lista de resultados

    results = sorted(results, key=attrgetter('profit'),reverse=True) #as melhores resultados são colocadas no topo da lista
    finalresult = results[0] #o melhor resultado é o primeiro
    if verbose: 
        for x in results:
            x.print_result_h() #se verboso, imprime o resultado
    return finalresult #retorna o melhor resultado


#------------------------------------------------------------------------------#
#   Vizinhança Variável                                                        #
# -----------------------------------------------------------------------------#


def nbhood(result_h, algo='auto', \
           taxrate=10, randomseed="i_will_survive_this", verbose=False, meta=False):
    """ Recebe uma Solução e executa a heurística mais aplicável para gerar sua vizinhança. """

    #Ordem das Caixas: escolhe as ordens que serão usadas na busca de vizinhança
    order = ['unordered','shuffle'] #'smallest','expensive','biggest','cheapest', 
    results = []
    results.append(result_h) #adiciona o resultado inicial na lista
    boxes_ord = copy.deepcopy(result_h.list_of_boxes) #faz uma cópia profunda (incl. todos as variaveis e referências da lista de caixas)
    
    if algo == 'auto': #caso nenhum algoritimo especifico seja selecionado
        if result_h.fit_order == 'avoidtaxes': algo = 'repack' # o repack é consideralvemente mais eficiente com mais caixas
        else: algo = 'top_to_bottom' # já o top_to_bottom é melhor com caixas cheias

    if algo == 'top_to_bottom':
        
        """ desempacota a *n caixa selecionada e a parte em duas de tamanho menor
         só trás melhorias tangiveis se a heuristica usada for first,best ou worst fit """
        
        for o in order:
            if o == 'unordered': pass
            #if o == 'biggest': boxes_ord = sorted(boxes_ord, key=lambda x: x.used_size, reverse=True)
            #if o == 'smallest': boxes_ord = sorted(boxes_ord, key=lambda x: x.used_size)
            #if o == 'expensive': boxes_ord = sorted(boxes_ord, key=lambda x: x.total_value, reverse=True)
            #if o == 'cheapest': boxes_ord = sorted(boxes_ord, key=lambda x: x.total_value)
            if o == 'shuffle': random.seed(randomseed); random.shuffle(boxes_ord)
            
            """ será calculada a vizinhança para TODAS as possibilidades de execução, ou seja, 
            o loop percorre todos os itens na caixa"""
            for box in range(len(boxes_ord)): 
                boxes = copy.deepcopy(boxes_ord) #faz uma copia da lista de caixas (para não alterar a original)
                sortbox = boxes[box].items #extrai a lista de itens da caixa
                # partir em duas
                mini1 = sortbox[:len(sortbox)//2]  #pega a primeira parte da lista de itens
                mini2 = sortbox[len(sortbox)//2:] #pega a segunda parte dela
                boxes.pop(box) #remove a caixa que foi partida da lista de caixas
                minibox1,minibox2 = Box(), Box() #inicializa as duas caixas
                for m in mini1: #adiciona os tens em suas respectivas caixas
                    minibox1.add_item(m)
                for m in mini2:
                    minibox2.add_item(m)
                # coloca os itens na caixa principal
                boxes.append(minibox1)
                boxes.append(minibox2)

                """ gera um novo resultado, e o coloca na lista, (função de avalição sendo calc_profit) """
                res = Result(list_of_boxes=copy.deepcopy(boxes), nb_algo=algo, \
                            nb_order=o, nb_pos=box, box_amount=len(boxes), profit=calc_profit(boxes,taxrate), \
                            fit_order=result_h.fit_order, sort_order=result_h.sort_order)                        
                results.append(res)

    if algo == "repack":
        """ tenta juntar várias caixas pequenas em uma caixa grande. 
        ps: essa heurista só faz efeito notável no algoritimo avoidtaxes """

        for o in order:
            if o == 'unordered': pass
            #if o == 'biggest': boxes_ord = sorted(boxes_ord, key=lambda x: x.used_size, reverse=True)
            #if o == 'smallest': boxes_ord = sorted(boxes_ord, key=lambda x: x.used_size)
            #if o == 'expensive': boxes_ord = sorted(boxes_ord, key=lambda x: x.total_value, reverse=True)
            #if o == 'cheapest': boxes_ord = sorted(boxes_ord, key=lambda x: x.total_value)
            if o == 'shuffle': random.seed(randomseed); random.shuffle(boxes_ord)
            
            """ assim como no "top_to_bottom" será calculada a vizinhança para TODAS as possibilidades de execução, ou seja, 
             o loop percorre todos os itens na caixa """
            for box in range(len(boxes_ord)):
                boxes = copy.deepcopy(boxes_ord) #faz uma cópia da lista de caixas original
                newbox = boxes[box] # captura o conteudo de uma caixa na variavel newbox
                boxes.pop(box) # e remove a caixa da lista

                add_phase = True # fase de adicionar caixas à caixa

                while add_phase: #enquanto ainda podemos adicionar itens
                    for i in range(len(boxes)): #procuramos por o primeira caixa que caiba dentro da caixa escolhida
                        if newbox.used_size + boxes[i].used_size <= newbox.total_size: #caso ela caiba, adiciona na caixa
                            newbox.items += boxes[i].items #atualiza os valores da caixa
                            newbox.used_size += boxes[i].used_size
                            newbox.total_value += boxes[i].total_value
                            boxes.pop(i);break #para o loop caso achado, e tira a caixa que foi mergida da lista.
                    else: add_phase = False #caso não ache mais caixas que caibam nela, termina a fase de adição
                if newbox.items: boxes.append(newbox) # se a nova caixa tiver algo dentro, adiciona na lista de caixas.
                # salvamos o resultado num objeto result e calculamos a função de avaliação.
                res = Result(list_of_boxes=copy.deepcopy(boxes), nb_algo=algo, \
                            nb_order=o, nb_pos=box, box_amount=len(boxes), profit=calc_profit(boxes,taxrate), \
                            fit_order=result_h.fit_order, sort_order=result_h.sort_order)                        
                results.append(res) #salvamos o resultado na lista de resultados

    """ organizamos os resultados na ordem do melhor valor da função de avaliação """
    results = sorted(results, key=attrgetter('profit'),reverse=True)
    if verbose:  # se verboso, imprimimos os cinco melhores resultados
        for i in range(5):
            results[i].print_result()
        print("- Melhor Vizinhança: ",end=''); results[0].print_result()        
    finalresult = results[0] # melhor resultado é o primeiro da lista

    if meta: return results #se queremos utilizar o resultado em uma metaheurisitca, retornamos toda a lista
    else: return finalresult #se só queremos o melhor valor, retornamos apenas ele


def vnd(solution, taxrate=10, algo='auto', randomseed="i_will_survive_this",\
        verbose = False):
    """ Descida de Vizinhança Variável:
    Executa a busca de vizinhança várias vezes até a achar um valor ótimo onde não é possível melhorar """

    old_profit = solution.profit # salva o valor antigo, para viés de comparação
    it = 0 # contador de execuções de vizinhança

    while True: #enquanto o um ótimo não for achado
        if verbose: print("> Visitando Vizinhança " + str(it+1))
        new_result = nbhood(solution, algo=algo, taxrate=taxrate, randomseed=randomseed,\
                            verbose=verbose) #roda o algoritimo da vizinhança
        if new_result.profit > solution.profit: #se o resultado achado for melhor que o valor anterior
            solution = new_result # atualiza o valor de solução
            it += 1 #atualiza o contador da vizinhança
        else: break #caso contrário, pare
    if verbose:
        print()
        print(">> Melhor Resultado Final:")
        solution.print_result()
        print("Melhoria: " + str(old_profit) + " ---> " + str(solution.profit) + " (+" + str(solution.profit - old_profit) + ")")
        print("Vizinhanças Visitadas para geração do resultado: " + str(it))
    return solution #retorna a melhor solução (objeto Result)


def smarter_vnd(solutions, taxrate=10, algo='auto', randomseed="i_wish_i_was_dead",\
        verbose = False):
    """ Metaheurística: VND com Backtracking """
    old_profit = solutions[0].profit #função de avaliação inicial
    optimal_solution = solutions[0] #solução otima inicial
    it,bk = 0,0 #contadores de vizinhanças visitadas e backtracking

    while solutions: #enquanto ouver soluções na lista
        if verbose: print("> Visitando Vizinhança " + str(it+1))
        new_solutions = nbhood(solutions[0], algo=algo, taxrate=taxrate, randomseed=randomseed,\
                            verbose=verbose, meta=True) #procura as vizinhanças locais, e salva a a lista num objeto

        if new_solutions[0].profit > optimal_solution.profit: # o se o valor da melhor nova solução for melhor que a solução otima anterior
            solutions = new_solutions #atualiza o valor da lista de soluções
            optimal_solution = solutions[0] # a nova solução otima é a primeira da lista
            it += 1 #atualiza o contador de vizinhanaça
            bk = 0 #reseta o contador de backtracking
        else:
            bk += 1 #incrementa o backgracking
            if bk == 20: break # limita o backtracking em 20 vizinhanças, por questões de tempo computacional
            print("Fazendo Backtracking: " + str(bk)) 
            solutions.pop(0) #remove a solução testada da lista.

            
    if verbose:
        print()
        print(">> Melhor Resultado Final:")
        optimal_solution.print_result()
        print("Melhoria: " + str(old_profit) + " ---> " + str(optimal_solution.profit) + " (+" + str(optimal_solution.profit - old_profit) + ")")
        print("Vizinhanças Visitadas para geração do resultado: " + str(it))

    return solutions



def smarter_vnd_worsening(solutions, taxrate=10, algo='auto', randomseed="i_will_survive_this",\
        verbose = False):
    """ Metaheurística: VND com Backtracking, com movimentos em soluções suboptimas """
    old_profit = solutions[0].profit #função de avaliação inicial
    optimal_solution = solutions[0] #solução otima inicial
    it,bk = 0,0 #contadores de vizinhanças visitadas e backtracking
    global_maximum = solutions[0]
    older_solution = solutions[0]

    while solutions: #enquanto ouver soluções na lista
        if verbose: print("> Visitando Vizinhança " + str(it+1))
        new_solutions = nbhood(solutions[0], algo=algo, taxrate=taxrate, randomseed=randomseed,\
                            verbose=verbose, meta=True) #procura as vizinhanças locais, e salva a a lista num objeto

        if new_solutions[0].profit > optimal_solution.profit: # o se o valor da melhor nova solução for melhor que a solução otima anterior
            solutions = new_solutions #atualiza o valor da lista de soluções
            older_solution = optimal_solution
            optimal_solution = solutions[0] # a nova solução otima é a primeira da lista
            if optimal_solution.profit > global_maximum.profit:
                global_maximum = optimal_solution
            it += 1 #atualiza o contador de vizinhanaça
            bk = 0 #reseta o contador de backtracking
        else:
            bk += 1 #incrementa o backgracking
            if bk == 10: 
                if global_maximum.profit > optimal_solution.profit:
                    optimal_solution = global_maximum
                    break # limita o backtracking em 10 vizinhanças, por questões de tempo computacional
            print("Fazendo Backtracking: " + str(bk))
            if optimal_solution.profit > global_maximum.profit:
                global_maximum = optimal_solution
            optimal_solution = older_solution 
            solutions.pop(0) #remove a solução testada da lista.

            
    if verbose:
        print()
        print(">> Melhor Resultado Final:")
        optimal_solution.print_result()
        print("Melhoria: " + str(old_profit) + " ---> " + str(optimal_solution.profit) + " (+" + str(optimal_solution.profit - old_profit) + ")")
        print("Vizinhanças Visitadas para geração do resultado: " + str(it))

    return solutions



