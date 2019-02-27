import json
import os
import random
import bottle
import math

from api import ping_response, start_response, move_response, end_response

class Node:
    def __init__ (self, coordinates, f_cost = None, visited = None, parent = None, isSnake = None, wall = None):
        self.f_cost = None
        self.coordinates = coordinates ##{[x][y]}
        self.visited = False
        self.parent = None
        self.isSnake = None
        self.wall = None
        self.h_cost = None
        
        
def distance(food, head):
    return math.sqrt((food['x'] - head['x'])**2 + (food['y'] - head['y'])**2)

def f_distance(node, target):
    return math.sqrt((node.coordinates['x'] - target['x'])**2 + (node.coordinates['y'] - target['y'])**2)

@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''

@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()

@bottle.post('/start')
def start():
    data = bottle.request.json

    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    print(json.dumps(data))

    color = "#00FF00"

    return start_response(color)

def f_cost(data, node, target):
    h_cost = node.parent.h_cost
    h_cost += 1
    node.h_cost = h_cost
    ourHead = data['you']['body'][0]
    f_cost = h_cost + f_distance(node, target)
    return f_cost

def createNeighbors(data, node, target):
    neighbors = []
    ## Create right neighbor
    if(node.coordinates['x'] + 1 != data['board']['width']):
        new_coords = node.coordinates
        new_coords['x'] += 1
        tmp_node = Node(new_coords)
        tmp_node.parent = node
        tmp_cost = f_cost(data, tmp_node, target)
        tmp_node.f_cost = tmp_cost
        neighbors.append(tmp_node)
        
    ## Create left neighbor
    if(node.coordinates['x'] - 1 != 0):
        new_coords = node.coordinates
        new_coords['x'] -= 1
        tmp_node = Node(new_coords)
        tmp_node.parent = node
        tmp_cost = f_cost(data, tmp_node, target)
        tmp_node.f_cost = tmp_cost
        neighbors.append(tmp_node)

    ## Create top neighbor
    if(node.coordinates['y'] - 1 != 0):
        new_coords = node.coordinates
        new_coords['y'] -= 1
        tmp_node = Node(new_coords)
        tmp_node.parent = node
        tmp_cost = f_cost(data, tmp_node, target)
        tmp_node.f_cost = tmp_cost
        neighbors.append(tmp_node)

    ## Create bottom neighbor
    if(node.coordinates['y'] + 1 != data['board']['height']):
        new_coords = node.coordinates
        new_coords['y'] += 1
        tmp_node = Node(new_coords)
        tmp_node.parent = node
        tmp_cost = f_cost(data, tmp_node, target)
        tmp_node.f_cost = tmp_cost
        neighbors.append(tmp_node)
    
    return neighbors

def isValid(data, node):
    valid = True
                        
    snakes = data['board']['snakes']
    for i in range(len(snakes)):
        for j in range(len(snakes[i]['body'])):
            if(node.coordinates == snakes[i]['body'][j]):
                valid = False
                return valid

    ## TO DO: Check nodes around enemy snake heads
    
    ourBody = data['you']['body']
    for k in range(len(ourBody)):
        if(node.coordinates == ourBody[k]):
            valid = False
            return valid

    return valid

def A_Star(data):
    ourHead = data['you']['body'][0]
    
    open_list = []
    closed_list = []

    
    node = Node(ourHead)
    node.f_cost = 0
    node.h_cost = 0
    node.visited = True
    open_list.append(node)

    target_food = data['board']['food'][0]
    min_distance = distance(data['board']['food'][0], ourHead)
    
    for i in range(len(data['board']['food'])):
        if(distance(data['board']['food'][i], ourHead) < min_distance):
            min_distance = distance(data['board']['food'][i], ourHead)
            target_food = data['board']['food'][i]
    ##print("right before while loop")
    for i in range(50):

        
        ## lowest_fcost is a node
        lowest_fcost = open_list[0]
        for i in range(len(open_list)):
            if open_list[i].f_cost < lowest_fcost.f_cost:
                print(lowest_fcost.f_cost)
                lowest_fcost = open_list[i]

        lowest_fcost.visited = True
        closed_list.append(lowest_fcost)
        open_list.remove(lowest_fcost)

        curr_coords = lowest_fcost.coordinates
        if curr_coords['x'] == target_food['x'] and curr_coords['y'] == target_food['y']:
            print("we got the lowest cost yayayaya")
            print(lowest_fcost)
            return lowest_fcost

        neighbors = createNeighbors(data, lowest_fcost, target_food)

        for j in range(len(neighbors)):
            if isValid(data, neighbors[j]) or neighbors[j] not in closed_list:
                already_exists = False
                for i in range(len(open_list)):
                    if open_list[i].coordinates == neighbors[j].coordinates:
                        already_exists = True
                        if open_list[i].f_cost > neighbors[j].f_cost:
                            open_list.remove(open_list[i])
                            open_list.append(neighbors[j])
                if already_exists == False:
                    open_list.append(neighbors[j])


def direction(node, ourHead):
    direction = ''
    tempnode = node
    while(tempnode.parent != ourHead):
        tempnode = tempnode.parent

    ## Check Right    
    temp_r = ourHead
    temp_r[0] += 1
    if tempnode.coordinates == temp_r:
        direction = 'right'

    ## Check Left
    temp_l = ourHead
    temp_l[0] -= 1
    if tempnode.coordinates == temp_l:
        direction = 'left'

    ## Check Up
    temp_u = ourHead
    temp_u[1] -= 1
    if tempnode.coordinates == temp_u:
        direction = 'up'

    ## Check Down
    temp_d = ourHead
    temp_d[1] += 1
    if tempnode.coordinates == temp_d:
        direction = 'down'

    return direction
    

@bottle.post('/move')
def move():
    ##print("1************************************\n\n\n\n")

    data = bottle.request.json

    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    ##print(json.dumps(data))




    directions = ['up', 'down', 'left', 'right']
    #direction = random.choice(directions)
    boardheight = data['board']['height']
    boardwidth = data['board']['width']

    ourHead = data['you']['body'][0]
    
    rightTopCorner = ourHead['y']==0 and ourHead['x']==boardwidth-1
    origin = ourHead['y']==0 and ourHead['x']==0
    leftBottomCorner = ourHead['x']==0 and ourHead['y']==boardheight-1
    rightBottomCorner = ourHead['x']==boardwidth-1 and ourHead['y']==boardheight-1
    rightWall = ourHead['x']==boardwidth-1
    bottomWall = ourHead['y']==boardheight-1
    leftWall = ourHead['x']==0
    topWall = ourHead['y']==0

    node = A_Star(data)
    print("After astar ************************************\n\n\n\n")
 
    direction_bigd = direction(node, ourHead)
    print("************************************\n\n\n\n")
    print(direction_bigd)
    return move_response(direction_bigd)


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    
    # x=data['turn']
    

# print(x)
    
    ##print(json.dumps(data))

    return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )

def move():
    data = bottle.request.json

    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    ##print(json.dumps(data))

    directions = ['up', 'down', 'left', 'right']
    direction = random.choice(directions)

    return move_response(direction)



