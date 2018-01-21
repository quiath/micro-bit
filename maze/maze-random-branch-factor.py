# -*- coding: utf-8 -*-

import microbit as m
from random import randrange as rr
    
WH = 20
SH = 5

def clamp(a, b, c):
    return max(min(c, b), a)
            
class Game:
    def __init__(self):
        self.world = bytearray(WH * WH)
        self.player = [ 1, 1 ]
        self.pos = [0, 0]

    def getworld(self, x, y):
        return self.world[x + y * WH]
    
    def setworld(self, x, y, s):
        self.world[x + y * WH] = s
        
    def world2screen(self, p):
        return [ p[0] - self.pos[0], p[1] - self.pos[1] ]
    
    def screen2world(self, p):
        return [ p[0] + self.pos[0], p[1] + self.pos[1] ]
    
    def getscreen(self, x, y):
        p = self.screen2world((x, y))
        if p == self.player:
            return 4
        else:
            return self.getworld(p[0], p[1])
        
    def trymove1axis(self, p, d, axis):
        q = [ p[0], p[1] ]
        q[axis] += d
        if q[axis] < 0 or q[axis] >= WH:
            return False, p
        if self.getworld(q[0], q[1]) != 0:
            return False, q
        return True, q

    def updatepos(self):
        self.pos[0] = clamp(0, self.player[0] - SH // 2, WH - SH)
        self.pos[1] = clamp(0, self.player[1] - SH // 2, WH - SH)
        
    def moveplayer(self, dxy, ax):
        for i in range(2):
            if dxy[ax] != 0:
                r, q = self.trymove1axis(self.player, dxy[ax], ax)
                if r:
                    self.player = q
                    self.updatepos()
                    return True
            ax = 1 - ax
        return False        

XX = "2101"
YY = "1210"

CACTGOAL = 3
CAVAIL = 2
CWALL = 1
CEMPTY = 0

def mazesearchactive(g, k):
    for x in range(1, WH - 1):
        for y in range(1, WH - 1):
            if g.getworld(x, y) & 0x03 == CACTGOAL:
                if k == 0:
                    return x, y, 
                k -= 1
    return None, None

def mazeupd(g, x, y, active, d):
    p = g.getworld(x, y)
    if p & 0x03 == CACTGOAL:
        g.setworld(x, y, CWALL)
        active -= 1
    elif p == CAVAIL:
        g.setworld(x, y, CACTGOAL + (d << 2))
        active += 1
    
    return active
    
def maze(g, prob_max, prob_t):
    active = 0
    for x in range(WH):
        for y in range(WH):
            if x == 0 or y == 0 or x == WH - 1 or y == WH - 1:
                g.setworld(x, y, CWALL)
            else:
                g.setworld(x, y, CAVAIL)
                
    g.setworld(1, 1, CACTGOAL)
    active += 1
    
    nx, ny = -1, -1
    
    while active > 0:
        
        if nx == -1:
            x, y = mazesearchactive(g, rr(active))
        else:
            x, y = nx, ny
            nx, ny = -1, -1
            
        lastd = g.getworld(x, y) >> 2
        
        g.setworld(x, y, CEMPTY)
        active -= 1
                
        for d in range(4):
            nactive = mazeupd(g, x + int(XX[d]) - 1, y + int(YY[d]) - 1, active, d)
            if lastd == d and nactive > active and rr(prob_max) < prob_t:
                nx, ny = x + int(XX[d]) - 1, y + int(YY[d]) - 1
            active = nactive
    
    g.setworld(x, y, CACTGOAL)
    return x, y

h = rr(10)
m.display.show(str(h))
g = Game()
gx, gy = maze(g, 10, h)

f = 0    

while True:
    
    if m.button_a.is_pressed():
        m.display.clear()
        m.display.set_pixel(g.player[0] * SH // WH, g.player[1] * SH // WH, 9)
        m.display.set_pixel(gx * SH // WH, gy * SH // WH, 8 * (f % 2))
    else:
        
        for y in range(SH):
            for x in range(SH):
                v = g.getscreen(x, y)
                if v == CACTGOAL and f % 2 == 1:
                    v = 0
                m.display.set_pixel(x, y, v * 2)

        if abs(g.player[0] - gx) + abs(g.player[1] - gy) <= 1:
            break

        dx = m.accelerometer.get_x()
        dy = m.accelerometer.get_y()
        ax = int(abs(dy) > abs(dx))
        dx = clamp(-1, dx // 200, 1)
        dy = clamp(-1, dy // 200, 1)
        if dx != 0 or dy != 0:
            g.moveplayer((dx, dy), ax)

    m.sleep(200)
    f += 1

while True:
    m.sleep(500)
    m.display.scroll("{}s".format(f // 5))

