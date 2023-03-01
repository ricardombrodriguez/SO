import random
import sys
import numpy

random.seed(98388)

def timing():
    global next_event_type
    global time_next_event
    global sim_time
    global time_last_event

    min_time_next_event = 1e10

    next_event_type = ''

    for e in time_next_event:
        if time_next_event[e] < min_time_next_event:
            min_time_next_event = time_next_event[e]
            next_event_type = e

    if next_event_type == '':
        print('Event list is empty at time', sim_time)
        sys.exit()

    time_last_event = sim_time
    sim_time = min_time_next_event

def update_metrics():
    global sim_time
    global time_last_event
    global inventory_level
    global backlog
    global area_backlog
    global area_inventory_products

    if inventory_level < 0:
        backlog = abs(inventory_level)
        area_backlog += 5 * (sim_time - time_last_event) * backlog
    elif inventory_level > 0:
        area_inventory_products += (sim_time - time_last_event) * inventory_level

def inventory_evaluation():
    global sim_time
    global time_next_event
    global inventory_level
    global ordering_cost
    global outstanding_order
    global s
    global S

    if (inventory_level < s):
        # Place order, since inventory level is below s limit

        outstanding_order = S - inventory_level

        # Cost of the order, with K being the setup cost and i being the incremental cost
        K = 32
        i = 3
        ordering_cost += K + i*outstanding_order

        time_next_event['order_arrival'] = sim_time + random.uniform(0.5,1)

    time_next_event['evaluation'] = sim_time + 1


def order_arrival():
    global time_next_event
    global inventory_level
    global backlog
    global outstanding_order

    inventory_level += outstanding_order
    outstanding_order = 0

    time_next_event['order_arrival'] = 1e10

def product_demand():
    global sim_time
    global backlog
    global time_next_event
    global inventory_level


    SIZE_DEMANDS = [1, 2, 2, 3, 3, 4]               # according to probabilities
    demanded_size = random.choice(SIZE_DEMANDS)

    inventory_level -= demanded_size

    # time until next demand
    time_next_event['product_demand'] = sim_time + numpy.random.exponential(scale=0.1)

    
def calculate_estimates():
    global ordering_cost
    global area_inventory_products
    global area_backlog
    global total_cost

    ordering_cost /= 120                # divide per 120 months (giving per month average)
    area_inventory_products /= 120      # divide per 120 months (giving per month average)
    area_backlog /= 120                 # divide per 120 months (giving per month average)
    total_cost = ordering_cost + area_inventory_products + area_backlog

    with open("results.txt", "a") as file:
        file.write('\n\nSimulation. s = {0:5d} and S = {1:5d}\n'.format(s, S))
        file.write('Ordering cost (per month): {0:5.2f}\n'.format(ordering_cost))
        file.write('Handling cost (per month): {0:5.2f}\n'.format(area_inventory_products))
        file.write('Shortage cost (per month): {0:5.2f}\n'.format(area_backlog))
        file.write('TOTAL COST (per month): {0:5.2f}\n'.format(total_cost))
        file.write("===============================================")
        

# main

# simulation inputs
s_S = [
    (20,40),
    (20,60),
    (20,80),
    (20,100),
    (40,60),
    (40,80),
    (40,100),
    (60,80),
    (60,100),
]

for s, S in s_S:

    # simulation clock
    sim_time = 0.0

    # state variables
    inventory_level = 60
    time_last_event = 0.0
    backlog = 0
    outstanding_order = 0

    # simulation limits
    simulation_time_limit = 120     # months

    # statistics
    total_cost = 0.0
    ordering_cost = 0.0
    area_inventory_products = 0.0
    area_backlog = 0.0

    # event list
    time_next_event = {}
    time_next_event['product_demand'] = sim_time + numpy.random.exponential(scale=0.1)
    time_next_event['evaluation'] = sim_time + 1
    time_next_event['order_arrival'] = 1e10

    next_event_type = ''


    while sim_time < 120:

        timing()

        update_metrics()

        if next_event_type == 'product_demand':
            product_demand()
        elif next_event_type == 'evaluation':
            inventory_evaluation()
        elif next_event_type == 'order_arrival':
            order_arrival()

    calculate_estimates()