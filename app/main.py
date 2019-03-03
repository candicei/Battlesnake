import json
import os
import random
import bottle
import numpy as np

from api import ping_response, start_response, move_response, end_response


# A Star Implementation from: https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

    
#A* Algorithm    
def astar(maze, start, end):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""

    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    i = 0 #initializing 
    # Loop until you find the end
    while len(open_list) > 0:

        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1] # Return reversed path

        i = i+1
        # backup path
        b_path = [] 
        num_items_in_bpath = 0
        
        # Generate children
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares

            
            if(i>200 and num_items_in_bpath>0):
                node_position = b_path[0][0] + new_position[0], b_path[0][1]+new_position[1]
            else:   
                # Get node position
                node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (len(maze) - 1) or node_position[0] < 0 or node_position[1] > (len(maze[len(maze)-1]) -1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if maze[node_position[0]][node_position[1]] != 0:
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:

            # Child is on the closed list
            for closed_child in closed_list:
                if child == closed_child:
                    continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            # Child is already in the open list
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    continue

            # Add the child to the open list
            open_list.append(child)
    
    
    
#Returns the maze filled with zeros
def returnMaze(data):
    boardx = data['board']['height']
    boardy = data['board']['width']
    maze = np.zeros((boardx,boardy),dtype=int)
    return maze

#Gives the (int) x and y position of our OWN snake in two lists (x, y)
def getSelfPos(data):
    snake = data['you']['body']
    x = [snakePos['x'] for snakePos in snake]
    y = [snakePos['y'] for snakePos in snake]
    return x,y

# return the current head postion of OWN snake in (int) as a tuple
def getSelfHeadPos(data):
    xself,yself = getSelfPos(data)
    x = xself[0]
    y = yself[0]
    return (x,y)

#Gives the entire position of snakes 
def enemyAllPos(data):
    numEnemies = enemyCount(data)
    xx = [] #initializing
    yy = [] #initializing
    selfx,selfy = getSelfPos(data) 
    #looping to find an appended list of x and y coordinates of all enemy snakes
    for s in range(numEnemies+1): #need to include +1 because location of 'self' also has to be considered
        x,y = enemy1Pos(data,s)
        if not(x == selfx or y == selfy):
            xx += x
            yy += y
    return xx,yy

#Gives the x,y as a list of int values of the a snake given 'numSnake' which starts at 0  
def enemy1Pos(data,numSnake):
    snake = data['board']['snakes'][numSnake]['body']
    x = [snakePos['x'] for snakePos in snake]
    y = [snakePos['y'] for snakePos in snake]
    return x,y

#Gives the position of surrounding position of enemies heads and their potential 'next step'
def enemySurroundHeadPos(data):
    numEnemies = enemyCount(data)
    xx = [] #initializing
    yy = [] #initializing
    direction_x = [0, 0, -1, 1] # referring to up, down, left, right
    direction_y = [-1, 1, 0, 0] # referring to up, down, left, right
    
    
    #looping to find the 4 locations surrounding the head
    for s in range(numEnemies):
        x,y = enemy1Pos(data,s)
    
        headx = x[0]
        heady = y[0]
        print('head of enemy')
        print((headx,heady))
        print('head of  own')
        print(getSelfHeadPos(data))
        if not((headx,heady) == getSelfHeadPos(data)):
            print('got that the heads are different')
            #looping through the directions
            for rr in range(4):
                dir = [(headx)+direction_x[rr],(heady+direction_y[rr])] #find the 4 locations an enemie's head can move into in the next step
                if (int(dir[0]) in range(0,(data['board']['height']-1)) and int(dir[1]) in range(0,(data['board']['width']-1))): #making sure the coords are within the board range
                    xx+= [dir[0]]
                    yy+= [dir[1]]
            print('surrounding head:')
            print(xx,yy)
    
    return xx,yy


#Gives the number of enemies still alive
def enemyCount(data):
    numEnemies = sum(1 for enemies in data['board']['snakes']) -1 # minus one because the board counts itself in "snakes"
    return numEnemies

#Finding location of fruits
def fruitLoc(data):
    snake = data['board']['food']
    x = [snakePos['x'] for snakePos in snake]
    y = [snakePos['y'] for snakePos in snake]
    return x,y

#Finding nearest fruit to head. Returns position as a tuple (int) x,y
def closestFruit(data,maze):
    fx,fy = fruitLoc(data) #getting x,y of all fruits
    hx,hy = getSelfHeadPos(data) #getting position of head
    viableFruitx = [] #initializing viable fruit locations (x)
    viableFruity = [] #initializing viable fruit locations (y)
    flag = 0
    for j in range(0,len(fx)): # determining where fruits might be covered by potential snake moves
        if (maze[fx[j],fy[j]] == 0):
            print('')
            viableFruitx += [fx[j]]
            viableFruity += [fy[j]] 
    # if all fruits are covered up, gg and just go for one anyways, merp. 
    if viableFruitx == []:
        viableFruitx = fx
        viableFruity = fy
        flag = 1
    
    distx = np.array(viableFruitx) - hx
    disty = np.array(viableFruity) - hy
    distx *= distx #calculating the square
    disty *= disty #calculating the square
    dist = distx+disty #calculating distance (without taking sqrt)
    indexMin = np.argmin(dist) #checked: only returns one index which is good
    if flag == 1:
        if indexMin == 0:
            indexMin = 1
        else:
            indexMin = 0
    return (viableFruitx[indexMin],viableFruity[indexMin])

#provides the string direction: 'up','down','left','right' from the path
def returnDirection(path):
    arrayDirection = np.subtract(path[1],path[0])
    if (arrayDirection == ([0,-1])).all():
        direction = 'up'
    elif (arrayDirection == ([0,1])).all():
        direction = 'down'
    elif (arrayDirection == ([-1,0])).all():
        direction = 'left'
    elif (arrayDirection == ([1,0])).all():
        direction = 'right'
    else:
        direction = 'right'
        print('random direction chosen!')
    return direction 


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
    print(" ")
    print("---------------------")
    print("New Game")
    print(data)
    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
#    print(json.dumps(data))

    # Obtaining board height and width!
    boardx = data['board']['height'] 
    boardy = data['board']['width']
    print(boardx)
    print(boardy)

    color = "#00FF00"

    return start_response(color)


@bottle.post('/move')
def move():
    data = bottle.request.json
    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
#    print('--')
    numEnemies = enemyCount(data)
    #print(numEnemies)
#    print(data['turn'])
    

    #obtaining 'maze' for astar
    maze = returnMaze(data) #obtaining maze (size)
    
    enemyXLoc, enemyYLoc = enemyAllPos(data) #obtaing locations of enemies on maze
    ownXLoc, ownYLoc = getSelfPos(data) #obtaining own snake location on maze
    enemyHeadMoveX, enemyHeadMoveY = enemySurroundHeadPos(data) #obtaining locations of the potential location of future enemy heads 
#    print('enemy head 4 locss')
    
    maze[enemyXLoc, enemyYLoc] = 1 #marking locations of other snakes on maze
    maze[ownXLoc, ownYLoc] = 1 #marking self location on maze
    maze[enemyHeadMoveX, enemyHeadMoveY] = 1 #marking locations of potential enemy sneakhead movements on maze
    
    
    #blocking off maze edges
    boardx = data['board']['height'] 
    boardy = data['board']['width']
    for x in range(0,boardx):
        maze[x,0] = 1
        maze[x,boardy-1] = 1
    for y in range(0,boardy):
        maze[0,y] = 1
        maze[boardx-1,y] = 1
    

    #obtaining 'start' for astar 
    start = getSelfHeadPos(data) #using current head location as 'start'
    print('start')
    print(start)
    
    #obtaining 'end' for astar 
    end = closestFruit(data,maze)
    print('end')
    print(end)
    
    #calculating astar for the shortest path
    path = astar(maze, start, end)
    print('path:')
    print(path)
    
    #determining direction
    direction = (returnDirection(path))
#    print('direction:')
#    print(direction)
#    print(data)
    print('data of snake:')
    print(data)
    return {"move": direction}


@bottle.post('/end')
def end():
    data = bottle.request.json
    print(data)

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
#    print(json.dumps(data))

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