from copy import deepcopy
import os
import random
from collections import namedtuple


# Features
# 1. tail should grow
# 2. food generation
# 3. wall hit detection 
# 4. self hit detection 
# 5. move through walls
# 6. wall healing 

class Grid:
    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns*2
        self.grid = [([" "]*(self.columns)) for row in range(rows)]

    def get_column_size(self):
        return self.columns

    def get_row_size(self):
        return self.rows

    def init(self):
        self.draw_borders()

    def __getitem__(self, index):
        return self.grid[index]

    def draw_borders(self):
        for row in range(self.rows):
            for column in range(self.columns):
                is_first_row = row == 0
                is_last_row = row == self.rows-1
                is_first_column = column == 0
                is_last_column = column == self.columns-1

                if is_first_column:
                    self.grid[row][column] = "|"
                elif is_last_column:
                    self.grid[row][column] = "|"
                elif is_first_row:
                    self.grid[row][column] = "`"
                elif is_last_row:
                    self.grid[row][column] = "_"

    def print_grid(self):
        os.system('clear')
        for row in self.grid:
            for column in row:
                print(column, end="", flush=False)
            print(flush=False)
        print(flush=True)


class Snake:
    def __init__(self, grid, can_snake_go_through_wall):
        self.score = 0
        self.food = None
        self.grid = grid
        self.can_snake_go_through_wall = can_snake_go_through_wall
        self.snake = []
        self.snake_direction = None
        self.curr_direction = None

        self.init_snake_direciton()
        self.init_snake_head()
        self.generate_food(self.snake)
        self.draw_snake()

    def draw_snake(self):
        self.grid.print_grid()

    def init_snake_direciton(self):
        SnakeDirection = namedtuple(
            "SnakeDirection", ["left", "right", "up", "down"])
        snake_direction = SnakeDirection("LEFT", "RIGHT", "UP", "DOWN")
        self.snake_direction = snake_direction
        self.curr_direction = snake_direction.left

    def init_snake_head(self):
        self.snake = []
        snake_head_x = self.grid.get_column_size()//2
        snake_head_y = self.grid.get_row_size()//2
        self.snake.append((snake_head_y, snake_head_x))
        self.grid[snake_head_y][snake_head_x] = "<"

    def can_snake_move(self, target_direction):
        possible_moves = {
            self.snake_direction.up: ["RIGHT", "LEFT", "UP"],
            self.snake_direction.down: ["RIGHT", "LEFT", "DOWN"],
            self.snake_direction.left: ["UP", "DOWN", "LEFT"],
            self.snake_direction.right: ["UP", "DOWN", "RIGHT"],
        }
        can_snake_move_in_target_direction = target_direction in possible_moves[
            self.curr_direction]

        return can_snake_move_in_target_direction

    def grow_snake_tail(self, is_food_consumed, prev_last_tail_pos, snake):
        if is_food_consumed:
            snake.append(prev_last_tail_pos)
        else:
            row = prev_last_tail_pos[0]
            column = prev_last_tail_pos[1]

            is_first_row = row == 0
            is_last_row = row == self.grid.get_row_size()-1
            is_first_column = column == 0
            is_last_column = column == self.grid.get_column_size()-1

            char = " "

            if is_first_column:
                char = "|"
            elif is_last_column:
                char = "|"
            elif is_first_row:
                char = "`"
            elif is_last_row:
                char = "_"
            else:
                char = " "

            self.grid[row][column] = char

    def move_snake_body(self, new, snake):
        tmp = None
        for index in range(len(snake)):
            tmp = snake[index]
            snake[index] = new
            new = tmp

        return tmp

    def consume_food(self, new, snake):
        snake_y = new[0]
        snake_x = new[1]
        food_y = self.food[0]
        food_x = self.food[1]

        is_food_consumed = snake_x == food_x and snake_y == food_y
        if is_food_consumed:
            self.score += 1
            self.grid[food_y][food_x] = " "
            self.generate_food(snake)
            return True

        return False

    def generate_food(self, snake):
        is_food_position_not_generated = True
        food_x = None
        food_y = None

        while is_food_position_not_generated:
            food_x = random.randint(1, self.grid.get_column_size()-2)
            food_y = random.randint(1, self.grid.get_row_size()-2)

            for body in snake:
                if food_x != body[1] and food_y != body[0]:
                    is_food_position_not_generated = False

        self.food = (food_y, food_x)
        self.grid[food_y][food_x] = "@"
        return

    def has_snake_hit_wall(self, snake):
        body = snake[0]
        body_y = body[0]
        body_x = body[1]

        is_first_row = body_y == 0
        is_last_row = body_y == self.grid.get_row_size()-1
        is_first_column = body_x == 0
        is_last_column = body_x == self.grid.get_column_size()-1

        if is_first_row or is_last_row or is_first_column or is_last_column:
            return True
        else:
            return False

    def is_snake_collied(self, snake):
        for i in range(len(snake)-1):
            for j in range(i+1, len(snake)):
                if snake[i][0] == snake[j][0] and \
                        snake[i][1] == snake[j][1]:
                    return True
        return False

    def update_snake_on_grid(self, snake):
        snake_head = {
            "LEFT": "<",
            "RIGHT": ">",
            "UP": "^",
            "DOWN": "v"
        }

        snake_head_char = snake_head[self.curr_direction]

        for index, body in enumerate(snake):
            row = body[0]
            column = body[1]
            if index == 0:
                self.grid[row][column] = snake_head_char
            else:
                self.grid[row][column] = "o"

    def move_snake(self, direction):
        can_move = self.can_snake_move(direction)
        if can_move:
            new_head_position = self.get_next_head_position(direction)
            tmp_snake = deepcopy(self.snake)
            is_food_consumed = self.consume_food(new_head_position, tmp_snake)
            prev_last_tail_position = self.move_snake_body(
                new_head_position, tmp_snake)
            self.grow_snake_tail(
                is_food_consumed, prev_last_tail_position, tmp_snake)
            has_snake_hit_the_wall = False
            if self.can_snake_go_through_wall == False:
                has_snake_hit_the_wall = self.has_snake_hit_wall(tmp_snake)
            has_snake_collied = self.is_snake_collied(tmp_snake)
            if has_snake_collied or has_snake_hit_the_wall:
                print("DANGER!!!")
            else:
                self.curr_direction = direction
                self.update_snake_on_grid(tmp_snake)
                self.snake = tmp_snake
                self.draw_snake()

    def get_next_head_position(self, direction):
        if direction == self.snake_direction.up:
            return self.move_snake_up()
        elif direction == self.snake_direction.down:
            return self.move_snake_down()
        elif direction == self.snake_direction.right:
            return self.move_snake_right()
        elif direction == self.snake_direction.left:
            return self.move_snake_left()
        else:
            raise Exception(f"Invalid direction: {direction}")

    def move_snake_up(self):
        curr_snake_head_y = self.snake[0][0]
        curr_snake_head_x = self.snake[0][1]
        new_snake_head_y = curr_snake_head_y - 1
        if self.can_snake_go_through_wall and new_snake_head_y < 0:
            new_snake_head_y = self.grid.get_row_size()-1
        new_snake_position = (new_snake_head_y, curr_snake_head_x)
        return new_snake_position

    def move_snake_down(self):
        curr_snake_head_y = self.snake[0][0]
        curr_snake_head_x = self.snake[0][1]
        new_snake_head_y = curr_snake_head_y + 1
        if self.can_snake_go_through_wall and new_snake_head_y > self.grid.get_row_size()-1:
            new_snake_head_y = 0
        new_snake_position = (new_snake_head_y, curr_snake_head_x)
        return new_snake_position

    def move_snake_right(self):
        curr_snake_head_y = self.snake[0][0]
        curr_snake_head_x = self.snake[0][1]
        new_snake_head_x = curr_snake_head_x + 1
        if self.can_snake_go_through_wall and new_snake_head_x > self.grid.get_column_size()-1:
            new_snake_head_x = 0
        new_snake_position = (curr_snake_head_y, new_snake_head_x)
        return new_snake_position

    def move_snake_left(self):
        curr_snake_head_y = self.snake[0][0]
        curr_snake_head_x = self.snake[0][1]
        new_snake_head_x = curr_snake_head_x - 1
        if self.can_snake_go_through_wall and new_snake_head_x < 0:
            new_snake_head_x = self.grid.get_column_size()-1
        new_snake_position = (curr_snake_head_y, new_snake_head_x)
        return new_snake_position


class Game:
    def __init__(self, snake):
        self.snake = snake

    def get_user_input(self):
        direction = input()
        if not direction:
            return
        direction = direction[0]
        key_map = {
            "w": "UP",
            "s": "DOWN",
            "a": "LEFT",
            "d": "RIGHT",
            "p": "EXIT"
        }
        if direction in ["w", "a", "s", "d", "p"]:
            return key_map[direction]
        else:
            return None

    def run_game(self):
        while True:
            command = self.get_user_input()
            if not command:
                continue
            elif command == "EXIT":
                break
            elif command:
                self.snake.move_snake(command)


if __name__ == "__main__":
    grid = Grid(40, 40)
    grid.init()
    snake = Snake(grid, False)
    game = Game(snake)
    game.run_game()
