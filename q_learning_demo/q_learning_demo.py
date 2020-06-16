"""
DOCSTRING
"""
import threading
import time
import tkinter

class Learn:
    """
    DOCSTRING
    """
    def __init__(self):
        """
        DOCSTRING
        """
        self.world = World()
        self.world()
        self.discount = 0.3
        self.actions = self.world.actions
        states = []
        self.Q = {}
        for i in range(self.world.x):
            for j in range(self.world.y):
                states.append((i, j))
        for state in states:
            temp = {}
            for action in self.actions:
                temp[action] = 0.1
                self.world.set_cell_score(state, action, temp[action])
            self.Q[state] = temp
        for (i, j, c, w) in self.world.specials:
            for action in self.actions:
                self.Q[(i, j)][action] = w
                self.world.set_cell_score((i, j), action, w)

    def __call__(self):
        """
        DOCSTRING
        """
        t = threading.Thread(target=self.run)
        t.daemon = True
        t.start()
        self.world.start_game()

    def do_action(self, action):
        """
        DOCSTRING
        """
        s = self.world.player
        r = -self.world.score
        if action == self.actions[0]:
            self.world.try_move(0, -1)
        elif action == self.actions[1]:
            self.world.try_move(0, 1)
        elif action == self.actions[2]:
            self.world.try_move(-1, 0)
        elif action == self.actions[3]:
            self.world.try_move(1, 0)
        else:
            return
        s2 = self.world.player
        r += self.world.score
        return s, action, r, s2

    def inc_Q(self, s, a, alpha, inc):
        """
        DOCSTRING
        """
        self.Q[s][a] *= 1 - alpha
        self.Q[s][a] += alpha * inc
        self.world.set_cell_score(s, a, self.Q[s][a])
    
    def max_Q(self, s):
        """
        DOCSTRING
        """
        val = None
        act = None
        for a, q in self.Q[s].items():
            if val is None or (q > val):
                val = q
                act = a
        return act, val

    def run(self):
        """
        DOCSTRING
        """
        time.sleep(1)
        alpha = 1
        t = 1
        while True:
            s = self.world.player
            max_act, max_val = self.max_Q(s)
            (s, a, r, s2) = self.do_action(max_act)
            max_act, max_val = self.max_Q(s2)
            self.inc_Q(s, a, alpha, r + self.discount * max_val)
            t += 1.0
            if self.world.has_restarted():
                self.world.restart_game()
                time.sleep(0.01)
                t = 1.0
            alpha = pow(t, -0.1)
            time.sleep(0.1)

class World:
    """
    DOCSTRING
    """
    def __init__(self):
        """
        DOCSTRING
        """
        self.master = tkinter.Tk()
        self.triangle_size = 0.1
        self.cell_score_min = -0.2
        self.cell_score_max = 0.2
        self.Width = 100
        (self.x, self.y) = (5, 5)
        self.actions = ["up", "down", "left", "right"]
        self.board = tkinter.Canvas(self.master, width=self.x*self.Width, height=self.y*self.Width)
        self.player = (0, self.y-1)
        self.score = 1
        self.restart = False
        self.walk_reward = -0.04
        self.walls = [(1, 1), (1, 2), (2, 1), (2, 2)]
        self.specials = [(4, 1, "red", -1), (4, 0, "green", 1)]
        self.cell_scores = {}

    def __call__(self):
        """
        DOCSTRING
        """
        self.render_grid()
        self.master.bind("<Up>", self.call_up)
        self.master.bind("<Down>", self.call_down)
        self.master.bind("<Right>", self.call_right)
        self.master.bind("<Left>", self.call_left)
        self.me = self.board.create_rectangle(self.player[0]*self.Width+self.Width*2/10,
                                              self.player[1]*self.Width+self.Width*2/10,
                                              self.player[0]*self.Width+self.Width*8/10,
                                              self.player[1]*self.Width+self.Width*8/10,
                                              fill="orange", width=1, tag="me")
        self.board.grid(row=0, column=0)

    def call_down(self, event):
        """
        DOCSTRING
        """
        self.try_move(0, 1)

    def call_left(self, event):
        """
        DOCSTRING
        """
        self.try_move(-1, 0)

    def call_right(self, event):
        """
        DOCSTRING
        """
        self.try_move(1, 0)

    def call_up(self, event):
        """
        DOCSTRING
        """
        self.try_move(0, -1)

    def create_triangle(self, i, j, action):
        """
        DOCSTRING
        """
        if action == self.actions[0]:
            return self.board.create_polygon((i+0.5-self.triangle_size)*self.Width,
                                             (j+self.triangle_size)*self.Width,
                                             (i+0.5+self.triangle_size)*self.Width,
                                             (j+self.triangle_size)*self.Width,
                                             (i+0.5)*self.Width, j*self.Width,
                                             fill="white",
                                             width=1)
        elif action == self.actions[1]:
            return self.board.create_polygon((i+0.5-self.triangle_size)*self.Width,
                                             (j+1-self.triangle_size)*self.Width,
                                             (i+0.5+self.triangle_size)*self.Width,
                                             (j+1-self.triangle_size)*self.Width,
                                             (i+0.5)*self.Width, (j+1)*self.Width,
                                             fill="white",
                                             width=1)
        elif action == self.actions[2]:
            return self.board.create_polygon((i+self.triangle_size)*self.Width,
                                             (j+0.5-self.triangle_size)*self.Width,
                                             (i+self.triangle_size)*self.Width,
                                             (j+0.5+self.triangle_size)*self.Width,
                                             i*self.Width, (j+0.5)*self.Width,
                                             fill="white",
                                             width=1)
        elif action == self.actions[3]:
            return self.board.create_polygon((i+1-self.triangle_size)*self.Width,
                                             (j+0.5-self.triangle_size)*self.Width,
                                             (i+1-self.triangle_size)*self.Width,
                                             (j+0.5+self.triangle_size)*self.Width,
                                             (i+1)*self.Width, (j+0.5)*self.Width,
                                             fill="white",
                                             width=1)

    def has_restarted(self):
        """
        DOCSTRING
        """
        return self.restart
    
    def render_grid(self):
        """
        DOCSTRING
        """
        for i in range(self.x):
            for j in range(self.y):
                self.board.create_rectangle(i*self.Width,
                                            j*self.Width,
                                            (i+1)*self.Width,
                                            (j+1)*self.Width,
                                            fill="white",
                                            width=1)
                temp = {}
                for action in self.actions:
                    temp[action] = self.create_triangle(i, j, action)
                self.cell_scores[(i,j)] = temp
        for (i, j, c, w) in self.specials:
            self.board.create_rectangle(i*self.Width,
                                        j*self.Width,
                                        (i+1)*self.Width,
                                        (j+1)*self.Width,
                                        fill=c,
                                        width=1)
        for (i, j) in self.walls:
            self.board.create_rectangle(i*self.Width,
                                   j*self.Width,
                                   (i+1)*self.Width,
                                   (j+1)*self.Width,
                                   fill="black",
                                   width=1)
    
    def restart_game(self):
        """
        DOCSTRING
        """
        self.player = (0, self.y-1)
        self.score = 1
        self.restart = False
        self.board.coords(self.me,
                          self.player[0]*self.Width+self.Width*2/10,
                          self.player[1]*self.Width+self.Width*2/10,
                          self.player[0]*self.Width+self.Width*8/10,
                          self.player[1]*self.Width+self.Width*8/10)

    def set_cell_score(self, state, action, val):
        """
        DOCSTRING
        """
        triangle = self.cell_scores[state][action]
        green_dec = int(min(
            255, max(0, (val - self.cell_score_min) * 255.0 / (self.cell_score_max - self.cell_score_min))))
        green = hex(green_dec)[2:]
        red = hex(255-green_dec)[2:]
        if len(red) == 1:
            red += "0"
        if len(green) == 1:
            green += "0"
        color = "#" + red + green + "00"
        self.board.itemconfigure(triangle, fill=color)

    def start_game(self):
        """
        DOCSTRING
        """
        self.master.mainloop()
    
    def try_move(self, dx, dy):
        """
        DOCSTRING
        """
        if self.restart == True:
            restart_game()
        new_x = self.player[0] + dx
        new_y = self.player[1] + dy
        self.score += self.walk_reward
        if (new_x >= 0) and (new_x < self.x) and (new_y >= 0):
            if (new_y < self.y) and not ((new_x, new_y) in self.walls):
                self.board.coords(self.me,
                                  new_x*self.Width+self.Width*2/10,
                                  new_y*self.Width+self.Width*2/10,
                                  new_x*self.Width+self.Width*8/10,
                                  new_y*self.Width+self.Width*8/10)
                self.player = (new_x, new_y)
        for (i, j, c, w) in self.specials:
            if new_x == i and new_y == j:
                self.score -= self.walk_reward
                self.score += w
                if self.score > 0:
                    print('Success! score: ', self.score)
                else:
                    print('Fail! score: ', self.score)
                self.restart = True
                return

if __name__ == '__main__':
    learn = Learn()
    learn()
