from tkinter import *
from random import *
from time import sleep
from PIL import Image, ImageTk
from datetime import datetime


class CaveGenerator:
    
    def __init__(self,width,height,cell_size,noise_dens,iters):
        self.minvalue=0#please make positive
        self.maxvalue=99#^^
        self.noise_density=noise_dens
        self.iterations=iters

        self.cellsize=cell_size
        self.rows=int(height/cellsize)
        self.cols=int(width/cellsize)

        #generate empty tilemap
        self.tilemap=[]
        for i in range(self.rows):
            col=[]
            for j in range(self.cols):
                col.append(None)
            self.tilemap.append(col)
        
    #noise function
    ################################################################
    #assign each square a value
    def noise(self):
        for i in range(self.rows):
            for j in range(self.cols):
                self.tilemap[i][j]=randint(self.minvalue,self.maxvalue)

    #cellular automata
    ################################################################
    def cell_auto(self):
        for its in range(self.iterations):
            newtilemap=[]
            for i in range(self.rows):
                row=[]
                for j in range(self.cols):
                    value=self.maxvalue
                    wallneighbors=0
                    for n in range(i-1,i+2):
                        for m in range(j-1,j+2):
                            if self.is_in_map(m,n):
                                if n!=i or m!=j:
                                    if self.is_wall(m,n):
                                        wallneighbors+=1
                            else:
                                wallneighbors+=1
                    if wallneighbors > 4:
                        value=randint(self.minvalue,self.noise_density)
                    row.append(value)
                newtilemap.append(row)

            for i in range(self.rows):
                for j in range(self.cols):
                    self.tilemap[i][j]=newtilemap[i][j]


    #helper mathods
    ########################################################################
    #return bool of whether or not (x,y) is a valid space
    def is_in_map(self,x,y):
        return x>=0 and x<self.cols and y>=0 and y<self.rows

    def is_wall(self,x,y):
        return self.tilemap[y][x] in range(0,self.noise_density+1)


    #wrapper methods
    ########################################################################
    def generate(self):#keep
        self.noise()
        self.cell_auto()
        return self.tilemap


#generate money map
####################################################################
def find_hex_color(rgb):
    color='#'
    for i in rgb:
        ayo=hex(i)[2:]
        color+=f'{ayo:>2}'
    return color.replace(' ','0')

def generate_color(value, gradient):
    diff=cave_generator.maxvalue - cave_generator.minvalue
    r=value * int(gradient[0] / diff)
    g=value * int(gradient[1] / diff)
    b=value * int(gradient[2] / diff)
    return find_hex_color((r,g,b))

#map stuff
################################################################
#initialization stuff
w=800
h=500
cellsize=10
noise_density=57
iterations=6

wall_color=(255,255,0)#red
ground_color=(167, 129, 68)#brownish
grid_color=find_hex_color((167, 129, 68))#brownish
gui_bg_color=find_hex_color((147,109,48))#darker brownish
money_color=find_hex_color((255,255,0))
transparent=find_hex_color((255,255,254))#reserved this to be seen as transparent

player_pos=None
money=0#the player's amount of cash money dolla beeohs
lives=3#player's lives duh
hurttime=datetime.now()
immunity=2#seconds the player should have immunity after being hit

difficulty=10#closer to zero is more enemies
tiles_broken=0
enemy_move=datetime.now()
enemy_move_speed=1.5#closer to zero is faster
enemies=[]
enemy_objects=[]

root = Tk()#master runtime guy
root.title('Cave Game')
root.configure(background=gui_bg_color)
root.wm_attributes('-transparentcolor',transparent)

cave_generator=CaveGenerator(w,h,cellsize,noise_density,iterations)
tilemap=cave_generator.generate()
changed=True


#boring gui stuff
############################################################################
money_label=Label(root,text=f'${money:>4}',fg=money_color,bg=gui_bg_color,font=('courier 40 bold'))

canvas=Canvas(root, width=w, height=h, bg=find_hex_color(ground_color),highlightthickness=0)

photo=PhotoImage(file='pheart.png')
photoimage=photo.subsample(10,10)

heartlabels=[]
for i in range(lives):
    heartlabels.append(Label(root,image=photoimage,background=gui_bg_color))
    heartlabels[-1].grid(row=0,column=1+i)

money_label.grid(row=0,column=0)
canvas.grid(row=1,column=0,columnspan=int(0.5*(w/cellsize)))

player=canvas.create_rectangle(0,0,cellsize,cellsize,fill='blue')

#place stuff in the map
###################################################################################
def place_stuff():
    global player_pos
    global tilemap

    #'realistically' cluster valuable walls vs. cheap ones
    most=range(int(6/7*noise_density), noise_density)
    middle=int(5/7*noise_density)
    least=int(2/7*noise_density)
    
    for i in range(len(tilemap)):
        for j in range(len(tilemap[i])):
            if cave_generator.is_wall(j,i):
                if tilemap[i][j] in most:
                    tilemap[i][j]=noise_density
                else:
                    most_neighbor=False
                    for m in range(i-1,i+2):
                        for n in range(j-1,j+2):
                            if cave_generator.is_in_map(n,m) and tilemap[m][n] in most:
                                most_neighbor=True
                                break
                        if most_neighbor:
                            break
                    if most_neighbor:
                        tilemap[i][j]=middle
                    else:
                        tilemap[i][j]=least
    
    #place player
    #to reference the player's location: use tilemap[-1][0] for x, tilemap[-1][1]
    #the indices of the first (50) lists and the indices of their values represent tilemap locations, while the values themselves represent wallvalue
    #however the values of the last list represent the tilemap location of the player. weird i know
    for i in range(len(tilemap)):
        over=False
        for j in range(len(tilemap[i])):
            if not cave_generator.is_wall(j,i):#place him somewhere that isn't a wall
                player_pos=[j,i]
                over=True
                break
        if over:
            break

    #place entry and exit
    #entry
    tilemap[player_pos[1]][player_pos[0]]=-1

    #exit
    for i in range(len(tilemap)-1,-1,-1):
        over=False
        for j in range(len(tilemap[i])-1,-1,-1):
            if not cave_generator.is_wall(j,i):
                tilemap[i][j]=-2
                over=True
                break
        if over:
            break

def place_enemies():
    global tiles_broken
    global difficulty
    global enemies
    global enemy_objects

    for k in range(int(tiles_broken / difficulty)+1-len(enemies)):
        over=False
        found=False
        while not found:
            i=randint(0,len(tilemap)-1)
            j=randint(0,len(tilemap[0])-1)
            if not cave_generator.is_wall(j,i):#place him somewhere that isn't a wall
                 enemies.append(['shadow',[j,i]])
                 enemy_objects.append(canvas.create_rectangle(0,0,cellsize,cellsize,fill='red'))
                 found=True
                 over=True
        if over:
            break
#draw the tilemap
####################################################################
def draw_tilemap():
    global changed
    global enemies
    global enemy_objects
    global canvas
    
    if changed:
        #clear the canvas
        canvas.delete('all')
        
        #gridlines: aren't doing anything as they are same color as ground
        for i in range(0,w,cellsize):
            canvas.create_line(i,0,i,h,fill=grid_color)
        for i in range(0,h,cellsize):
            canvas.create_line(0,i,w,i,fill=grid_color)

        #tiles
        for i in range(len(tilemap)):
            for j in range(len(tilemap[i])):
                x1=j*cellsize
                y1=i*cellsize
                x2=x1+cellsize
                y2=y1+cellsize
                color=None
                tile=False
                
                if tilemap[i][j] == -1:
                    color='pink'
                    tile=True
                elif tilemap[i][j] == -2:
                    color='pink'
                    tile=True
                elif tilemap[i][j] <= noise_density:
                    color=generate_color(tilemap[i][j],wall_color)
                    tile=True
                    
                if tile:
                    canvas.create_rectangle(x1,y1,x2,y2,fill=color)#,outline=color get rid of black outline
        changed=False

    for k in range(len(enemies)):
        canvas.delete(enemy_objects[k])
        x1=enemies[k][1][0]*cellsize
        y1=enemies[k][1][1]*cellsize
        x2=x1+cellsize
        y2=y1+cellsize
        enemy_objects[k]=canvas.create_rectangle(x1,y1,x2,y2,fill='red')
        
    #player tile
    global player
    global player_pos
    canvas.delete(player)
    x1=player_pos[0]*cellsize
    y1=player_pos[1]*cellsize
    x2=x1+cellsize
    y2=y1+cellsize
    player=canvas.create_rectangle(x1,y1,x2,y2,fill='blue')

#game build stuff
#######################################################################
def next_level():
    global tilemap
    global changed
    global tiles_broken
    global enemies
    
    tiles_broken=0
    enemies=[]
    
    tilemap=cave_generator.generate()
    changed=True
    place_stuff()
    place_enemies()

    sleep(1)
    

#player actions
########################################################################
actions=[]
bad_actions=['Shift_L','Shift_R','Caps_Lock']

                    
def keyup(e):
    if  e.keysym in actions and e.keysym not in bad_actions:
        actions.pop(actions.index(e.keysym.lower()))

def keydown(e):
    if not e.keysym in actions and e.keysym not in bad_actions:
        actions.append(e.keysym.lower())

def next_move(start,end):
    xdiff=end[0]-start[0]
    ydiff=end[1]-start[1]

    x=0
    y=0
    
    if xdiff > 0:
        x=1
    elif xdiff < 0:
        x=-1
    else:
        x=0
    if ydiff > 0:
        y=1
    elif ydiff < 0:
        y=-1
    else:
        y=0
    return [x,y]
        
def handle_actions():
    global player_pos
    global hurttime
    global immunity
    global enemies
    global enemy_move
    global enemy_move_speed

    #check player position for special stuff to do
    if tilemap[player_pos[1]][player_pos[0]] == -2:#if current space is the exit
        next_level()

    for i in range(len(enemies)):
        if player_pos == enemies[i][1] and (datetime.now()-hurttime).total_seconds() > immunity:
            lose_health(1)
            hurttime=datetime.now()

    #move enemies
    moved=False
    for k in range(len(enemies)):
        if (datetime.now()-enemy_move).total_seconds() > enemy_move_speed:
            if not cave_generator.is_wall(enemies[k][1][0]+next_move(enemies[k][1],player_pos)[0],enemies[k][1][1]):
                enemies[k][1][0]+=next_move(enemies[k][1],player_pos)[0]
            if not cave_generator.is_wall(enemies[k][1][0],enemies[k][1][1]+next_move(enemies[k][1],player_pos)[1]):
                enemies[k][1][1]+=next_move(enemies[k][1],player_pos)[1]
            moved=True
    if moved:
        enemy_move=datetime.now()
        moved=False

    #move and mine
    switch={'w':[0,-1],'s':[0,1],'a':[-1,0],'d':[1,0],'space':None}
    movenewx=player_pos[0]
    movenewy=player_pos[1]
    minenewx=player_pos[0]
    minenewy=player_pos[1]
    for char in actions:#gets the total prospect direction of movement
        if char in 'wasd':
            if cave_generator.is_in_map(movenewx+switch[char][0],movenewy+switch[char][1]) and not cave_generator.is_wall(movenewx+switch[char][0],movenewy+switch[char][1]):
                movenewx+=switch[char][0]
                movenewy+=switch[char][1]
            minenewx+=switch[char][0]
            minenewy+=switch[char][1]
    if 'space' in actions and cave_generator.is_in_map(minenewx,minenewy):
        mine_tile(minenewx,minenewy)
    move_player(movenewx,movenewy)
    
    
def move_player(newx,newy):
    global player_pos
    if cave_generator.is_in_map(newx,newy) and not cave_generator.is_wall(newx,newy):
        player_pos=[newx,newy]
            

def mine_tile(col,row):
    global changed
    global money
    global tiles_broken
    if cave_generator.is_wall(col,row):
        money+=tilemap[row][col]
        money_label['text']=f'${money:>4}'
        tilemap[row][col]=cave_generator.maxvalue
        changed=True
        tiles_broken+=1
        place_enemies()

def lose_health(amount):
    global lives
    if lives > 0:
        heartlabels[0].grid_forget()
        heartlabels.pop(0)
        lives-=amount
    else:
        print('you died play again?')
    
                
#do all the actions
########################################################################
place_stuff()
place_enemies()
draw_tilemap()
root.update()

root.bind('<KeyPress>', keydown)
root.bind('<KeyRelease>', keyup)
    
while True:
    #check player movement
    print(actions)
    handle_actions()
    draw_tilemap()
    root.update()
    sleep(0.075)










