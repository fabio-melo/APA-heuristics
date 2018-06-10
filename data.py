#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" data.py - classes e funções de carregamento/exportação """

import sys, random, json


#------------------------------------------------------------------------------#
# Classes                                                                      #
#------------------------------------------------------------------------------#


class Item:
    """ Item (Classe): cada item a ser guardado """

    def __init__(self, size, value):
        self.size = size
        self.value = value

class Box:
    """ Box (Classe): cada caixa onde serão armazenados os items """
    def __init__(self, size=1000):
        self.total_size = size
        self.used_size = 0
        self.total_value = 0
        self.items = []
    
    def add_item(self, item):
        """ Adiciona um item na caixa, e atualiza seus valores """
        self.items.append(item)
        self.used_size += item.size
        self.total_value += item.value

    def can_add(self, item):
        """ Verifica se pode adicionar item na caixa, retorna True se verdade"""
        return True if self.used_size + item.size <= self.total_size else False

    def can_add_without_tax(self, item, min_tax):
        """ Verifica se pode adicionar item na caixa sem ultrapassar o valor
            definido como mínimo taxável. retorna True se verdade """
        return True if self.used_size + item.size <= self.total_size \
                    and self.total_value + item.value <= min_tax else False

    def profit_per_box(self, base_box_cost=5, box_rate=0.005, tax_rate=10, \
                       min_tax=50):
        """ Itera entre cada item de uma caixa e calcula seu lucro
        Parametros:
            base_box_cost: custo minimo de cada caixa
            box_rate: um valor que varia de acordo com o peso da caixa
            tax_rate: valor da taxa de imposto
            min_tax: tamanho máximo de caixa para que não seja taxada """
        box_cost = int(base_box_cost + (box_rate * self.used_size))
        if self.total_value <= min_tax:
            profit = self.total_value - box_cost
          #  print("sem taxa: " + str(box_cost) + '--' + str(profit))
        else:   
            taxation = (self.total_value / 100) * tax_rate
            profit = self.total_value - int(taxation) - box_cost
           # print("taxado: "+ str(taxation) + "-" + str(box_cost) + "--" +
           # str(self.total_value) + "= " + str(profit))
        return profit


class Result:
    """ Result (Classe): armazena os resultados das heuristicas gulosas e
    das buscas de vizinhança """

    def __init__(self,list_of_boxes='',fit_order='',sort_order='',nb_algo='',\
                 nb_order='',nb_pos='',box_amount='', profit=''):
        self.list_of_boxes =list_of_boxes
        self.fit_order = fit_order
        self.sort_order = sort_order
        self.nb_algo = nb_algo
        self.nb_order = nb_order
        self.nb_pos = nb_pos
        self.box_amount = box_amount
        self.profit = profit


    def print_result_h(self):
        """ Imprime os Resultados das Heuristicas de Construção """
        print(str(self.profit) + " " + str(self.box_amount) + ' :' \
        + str(self.fit_order) + ',' + str(self.sort_order)+ ' ')

    def print_result(self):
        """ Impreme os Resultados dos Movimentos de Vizinhança """
        print(str(self.profit) + " " + str(self.box_amount) + ' :' + \
        str(self.nb_algo) + ',' + str(self.nb_order) + ',' + str(self.nb_pos) \
        + '/' + str(self.fit_order) + ',' + str(self.sort_order)+ ' ')

        
        

#------------------------------------------------------------------------------#
# Arquivos                                                                     #
#------------------------------------------------------------------------------#


def save_to_file(pack, file='instance.txt'):
    """ Salva uma lista de caixas como arquivo """
    packlist = []
    for p in pack:
        item = [p.size, p.value]
        packlist.append(item)
    with open(file, 'w') as f: json.dump(packlist, f)

def load_from_file(file):
    """ Carrega lista de caixas de um arquivo """
    with open(file, 'r') as f:
        packlist = []
        unpack = json.load(f)
        for u in unpack:
            new_item = Item(size=u[0],value=u[1])
            packlist.append(new_item)
        return packlist