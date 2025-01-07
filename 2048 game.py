import tkinter as tk
import random
import os
import datetime

class Game2048:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("2048 Game")
        self.board_size = 4
        self.tile_colors = {
            0: "#cdc1b4", 2: "#eee4da", 4: "#ede0c8", 8: "#f2b179",
            16: "#f59563", 32: "#f67c5f", 64: "#f65e3b", 128: "#edcf72",
            256: "#edcc61", 512: "#edc850", 1024: "#edc53f", 2048: "#edc22e",
        }
        self.score = 0
        self.previous_grid = None
        self.previous_score = 0
        self.grid = [[0] * self.board_size for _ in range(self.board_size)]
        self.setup_ui()
        self.spawn_tile()
        self.spawn_tile()
        self.window.mainloop()

    def get_difficulty(self):
        difficulty_window = tk.Toplevel(self.window)
        difficulty_window.title("Select Difficulty")

        difficulty_label = tk.Label(difficulty_window, text="Select Difficulty Level:", font=("Verdana", 14))
        difficulty_label.pack(pady=10)

        difficulty_var = tk.IntVar(value=2)

        def set_difficulty(level):
            difficulty_var.set(level)
            difficulty_window.destroy()

        tk.Button(difficulty_window, text="Easy (2 Tiles)", command=lambda: set_difficulty(2)).pack(pady=5)
        tk.Button(difficulty_window, text="Medium (4 Tiles)", command=lambda: set_difficulty(4)).pack(pady=5)
        tk.Button(difficulty_window, text="Hard (6 Tiles)", command=lambda: set_difficulty(6)).pack(pady=5)

        self.window.wait_window(difficulty_window)
        return difficulty_var.get()

    def setup_ui(self):
        self.frame = tk.Frame(self.window, bg="#bbada0", bd=4)
        self.frame.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        self.cells = []
        for i in range(self.board_size):
            row = []
            for j in range(self.board_size):
                cell = tk.Label(self.frame, text="", bg=self.tile_colors[0], fg="#776e65",
                                font=("Verdana", 24), width=4, height=2)
                cell.grid(row=i, column=j, padx=5, pady=5)
                row.append(cell)
            self.cells.append(row)

        self.score_label = tk.Label(self.window, text=f"Score: {self.score}",
                                    font=("Verdana", 18), bg="#bbada0", fg="white")
        self.score_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.undo_button = tk.Button(self.window, text="Undo", command=self.undo,
                                      font=("Verdana", 14), bg="#8f7a66", fg="white")
        self.undo_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.leaderboard_button = tk.Button(self.window, text="Leaderboard", command=self.show_leaderboard,
                                             font=("Verdana", 14), bg="#8f7a66", fg="white")
        self.leaderboard_button.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        self.window.bind("<Up>", lambda event: self.move("Up"))
        self.window.bind("<Down>", lambda event: self.move("Down"))
        self.window.bind("<Left>", lambda event: self.move("Left"))
        self.window.bind("<Right>", lambda event: self.move("Right"))

    def save_state(self):
        self.previous_grid = [row[:] for row in self.grid]
        self.previous_score = self.score

    def undo(self):
        if self.previous_grid:
            self.grid = [row[:] for row in self.previous_grid]
            self.score = self.previous_score
            self.update_ui()

    def spawn_tile(self):
        empty_cells = [(i, j) for i in range(self.board_size) for j in range(self.board_size) if self.grid[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.grid[i][j] = random.choice([2, 4])
            self.animate_tile_spawn(i, j)
        self.update_ui()

    def animate_tile_spawn(self, i, j):
        cell = self.cells[i][j]
        for size in range(10, 25):
            cell.config(font=("Verdana", size))
            self.window.update_idletasks()
            self.window.after(5)

    def update_ui(self):
        for i in range(self.board_size):
            for j in range(self.board_size):
                value = self.grid[i][j]
                self.cells[i][j].config(text="" if value == 0 else str(value),
                                         bg=self.tile_colors.get(value, "#f65e3b"))
        self.score_label.config(text=f"Score: {self.score}")

    def compress(self):
        new_grid = [[0] * self.board_size for _ in range(self.board_size)]
        for i in range(self.board_size):
            pos = 0
            for j in range(self.board_size):
                if self.grid[i][j] != 0:
                    new_grid[i][pos] = self.grid[i][j]
                    pos += 1
        self.grid = new_grid

    def merge(self):
        for i in range(self.board_size):
            for j in range(self.board_size - 1):
                if self.grid[i][j] == self.grid[i][j + 1] and self.grid[i][j] != 0:
                    self.grid[i][j] *= 2
                    self.grid[i][j + 1] = 0
                    self.score += self.grid[i][j]

    def reverse(self):
        for i in range(self.board_size):
            self.grid[i] = self.grid[i][::-1]

    def transpose(self):
        self.grid = [list(row) for row in zip(*self.grid)]

    def move(self, direction):
        self.save_state()
        if direction == "Up":
            self.transpose()
            self.compress()
            self.merge()
            self.compress()
            self.transpose()
        elif direction == "Down":
            self.transpose()
            self.reverse()
            self.compress()
            self.merge()
            self.compress()
            self.reverse()
            self.transpose()
        elif direction == "Left":
            self.compress()
            self.merge()
            self.compress()
        elif direction == "Right":
            self.reverse()
            self.compress()
            self.merge()
            self.compress()
            self.reverse()
        self.spawn_tile()

        if not self.can_move():
            self.game_over()

    def can_move(self):
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.grid[i][j] == 0:
                    return True
                if j < self.board_size - 1 and self.grid[i][j] == self.grid[i][j + 1]:
                    return True
                if i < self.board_size - 1 and self.grid[i][j] == self.grid[i + 1][j]:
                    return True
        return False

    def game_over(self):
        game_over_label = tk.Label(self.window, text="Game Over!", font=("Verdana", 24),
                                   bg="#bbada0", fg="white")
        game_over_label.grid()
        self.window.unbind("<Up>")
        self.window.unbind("<Down>")
        self.window.unbind("<Left>")
        self.window.unbind("<Right>")
        self.save_leaderboard()

    def save_leaderboard(self):
        try:
            with open("leaderboard.txt", "a") as file:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file.write(f"Score: {self.score} - {timestamp}\n")
        except Exception as e:
            print(f"Error saving leaderboard: {e}")

    def show_leaderboard(self):
        try:
            if not os.path.exists("leaderboard.txt"):
                with open("leaderboard.txt", "w") as file:
                    file.write("No scores yet.\n")

            with open("leaderboard.txt", "r") as file:
                scores = file.readlines()
                leaderboard_window = tk.Toplevel(self.window)
                leaderboard_window.title("Leaderboard")
                leaderboard_label = tk.Label(leaderboard_window, text="Leaderboard", font=("Verdana", 18), bg="#bbada0", fg="white")
                leaderboard_label.pack(pady=10)

                scores_text = tk.Text(leaderboard_window, font=("Verdana", 14), bg="#f9f6f2", fg="#776e65", width=40, height=15)
                scores_text.insert(tk.END, "".join(scores))
                scores_text.config(state=tk.DISABLED)
                scores_text.pack(padx=10, pady=10)

                close_button = tk.Button(leaderboard_window, text="Close", command=leaderboard_window.destroy,
                                         font=("Verdana", 14), bg="#8f7a66", fg="white")
                close_button.pack(pady=10)
        except FileNotFoundError:
            print("No leaderboard data found.")

if __name__ == "__main__":
    Game2048()
