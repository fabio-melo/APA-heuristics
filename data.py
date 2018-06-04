import sys, random, json

class Item:
    def __init__(self, size, value):
        self.size = size
        self.value = value

class Box:
    def __init__(self, size=1000):
        self.total_size = size
        self.used_size = 0
        self.total_value = 0
        self.items = []
    
    def add_item(self, item):
        self.items.append(item)
        self.used_size += item.size
        self.total_value += item.value

    def can_add(self, item):
        return True if self.used_size + item.size <= self.total_size else False

    def can_add_without_tax(self, item, min_tax):
        return True if self.used_size + item.size <= self.total_size and self.total_value + item.value <= min_tax else False

    def profit_per_box(self, base_box_cost=1, box_rate=0.001, tax_rate=10, min_tax=50):
        box_cost = int(base_box_cost + (box_rate * self.used_size))
        if self.total_value <= min_tax:
            profit = self.total_value - box_cost
          #  print("sem taxa: " + str(box_cost) + '--' + str(profit))
        else:   
            taxation = (self.total_value / 100) * tax_rate
            profit = self.total_value - int(taxation) - box_cost
           # print("taxado: "+ str(taxation) + "-" + str(box_cost) + "--" + str(self.total_value) + "= " + str(profit))
        return profit

#----------------------------#
# Funções Auxiliares         #
#----------------------------#

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

def save_to_file(pack, file='instance.txt'):
    packlist = []
    for p in pack:
        item = [p.size, p.value]
        packlist.append(item)
    with open(file, 'w') as f: json.dump(packlist, f)

def load_from_file(file):
    with open(file, 'r') as f:
        packlist = []
        unpack = json.load(f)
        for u in unpack:
            new_item = Item(size=u[0],value=u[1])
            packlist.append(new_item)
        return packlist