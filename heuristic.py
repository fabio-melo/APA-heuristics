import sys, random
from operator import itemgetter, attrgetter
from data import Item, Box

def fit(items, fit='first', sortedlist=False, box_size=1000, verbose=True, min_tax=50):
    
    # ordem da lista 
    if sortedlist: items = sorted(items,key=attrgetter('size'), reverse=True)
    if sortedlist == 'cheapest': items = sorted(items,key=attrgetter('value'))
    if sortedlist == 'expensive': items = sorted(items,key=attrgetter('value'), reverse=True)

    #totalitemvalue,totalitemsize = 0,0
    #for i in items: totalitemvalue += i.value; totalitemsize += i.size
  #  print(str(totalitemvalue) + ' ' + str(totalitemsize))
    boxes = []

    if fit in ("first", "best", "worst"):
        for item in items:
            if fit == 'best' and boxes: boxes = sorted(boxes, key=attrgetter('used_size'))
            if fit == 'worst' and boxes: boxes = sorted(boxes, reverse=True, key=attrgetter('used_size'))        
            
            for b in boxes:
                if b and b.can_add(item): b.add_item(item); break
            else:
                new_box = Box(box_size)
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
                if b and b.can_add_without_tax(item,min_tax) and b.used_size <= min_tax: b.add_item(item); break
            else:
                new_box = Box(box_size)
                cheap_boxes.append(new_box)
        for item in expensive_items:
            for b in expensive_boxes:
                if b and b.can_add(item): b.add_item(item); break
            else:
                new_box = Box(box_size)
                expensive_boxes.append(new_box)
        boxes = cheap_boxes + expensive_boxes

    if verbose: 
        print(str(fit) + " fit: " + str(sortedlist) + ' ' + str(len(boxes)))
        for b in boxes: print(str(b.used_size) + '-' + str(b.total_value),end='|')
        print()

    return boxes

