import random
import customtkinter as ctk
from tkinter import messagebox, ttk
import json
import os

rarities = {}

config_dir = "configurations"
if not os.path.exists(config_dir):
    os.makedirs(config_dir)

def save_config():
    config_name = entry_config_name.get().strip()
    if not config_name:
        messagebox.showerror("Error", "Please enter a valid configuration name.")
        return

    try:
        config_path = os.path.join(config_dir, f"{config_name}.json")
        with open(config_path, 'w') as f:
            json.dump(rarities, f)
        update_config_list()
        messagebox.showinfo("Success", f"Configuration '{config_name}' saved successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save configuration: {e}")

def load_config():
    config_name = config_dropdown.get()
    if not config_name:
        messagebox.showerror("Error", "Please select a configuration to load.")
        return

    try:
        config_path = os.path.join(config_dir, f"{config_name}.json")
        with open(config_path, 'r') as f:
            global rarities
            rarities = json.load(f)
        update_rarity_display()
        messagebox.showinfo("Success", f"Configuration '{config_name}' loaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load configuration: {e}")

def update_config_list():
    config_files = [f.split('.')[0] for f in os.listdir(config_dir) if f.endswith('.json')]
    config_dropdown["values"] = config_files
    if config_files:
        config_dropdown.set(config_files[0])

def add_rarity():
    name = entry_rarity_name.get().strip().lower()
    try:
        probability = float(entry_probability.get().strip())

        if probability >= 1:
            probability = probability / 100.0
        elif probability < 1:
            probability = probability / 100.0

        if not name or not (0 < probability <= 1):
            raise ValueError("Please enter a valid rarity name and probability between 0 and 1.")

        if name in rarities:
            messagebox.showerror("Error", f"Rarity '{name}' already exists.")
            return

        rarities[name] = probability
        update_rarity_display()

        target_rarity_menu["values"] = list(rarities.keys())

        entry_rarity_name.delete(0, ctk.END)
        entry_probability.delete(0, ctk.END)

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid probability (between 0 and 1).")

def update_rarity_display():
    textbox_rarities.delete(1.0, ctk.END)
    for rarity, probability in rarities.items():
        textbox_rarities.insert(ctk.END, f"{rarity.capitalize()}: {probability * 100:.2f}%\n")

def remove_rarity():
    selected = textbox_rarities.get("sel.first", "sel.last")
    if selected:
        rarity_name = selected.split(":")[0].strip().lower()
        if rarity_name in rarities:
            del rarities[rarity_name]
            update_rarity_display()
            target_rarity_menu["values"] = list(rarities.keys())
            messagebox.showinfo("Success", f"Rarity '{rarity_name}' removed successfully!")
        else:
            messagebox.showerror("Error", f"Rarity '{rarity_name}' not found.")
    else:
        messagebox.showerror("Error", "Please select a rarity to remove.")

def update_rarity_display():
    textbox_rarities.delete(1.0, ctk.END)
    for rarity, probability in rarities.items():
        textbox_rarities.insert(ctk.END, f"{rarity.capitalize()}: {probability * 100:.2f}%\n")


def simulate():
    try:
        target_rarity = target_rarity_menu.get()
        cost_per_roll = int(entry_cost_per_roll.get())
        num_simulations = int(entry_num_simulations.get())
        gold_per_hour = int(entry_gold_per_hour.get())
        starting_coins = int(entry_starting_coins.get())

        if not target_rarity:
            raise ValueError("Please select a target rarity for the simulation.")
        if cost_per_roll <= 0 or num_simulations <= 0 or gold_per_hour <= 0 or starting_coins <= 0:
            raise ValueError("Cost per roll, number of simulations, gold per hour, and starting coins must be positive.")
        if sum(rarities.values()) > 1:
            raise ValueError("The total probability of rarities cannot exceed 1 (100%).")

        total_rolls_all = 0
        total_cost_all = 0
        cumulative_roll_counts = {rarity: 0 for rarity in rarities}

        for _ in range(num_simulations):
            roll_counts = {rarity: 0 for rarity in rarities}
            total_rolls = 0
            got_target = False

            while not got_target:
                roll = random.random()
                total_rolls += 1
                cumulative_probability = 0
                for rarity, probability in rarities.items():
                    cumulative_probability += probability
                    if roll < cumulative_probability:
                        roll_counts[rarity] += 1
                        if rarity == target_rarity:
                            got_target = True
                        break

            total_rolls_all += total_rolls
            total_cost_all += total_rolls * cost_per_roll
            for rarity, count in roll_counts.items():
                cumulative_roll_counts[rarity] += count

        average_rolls = round(total_rolls_all / num_simulations)
        average_cost = round(total_cost_all / num_simulations)
        average_roll_counts = {rarity: round(cumulative_roll_counts[rarity] / num_simulations) for rarity in rarities}

        remaining_cost = max(0, average_cost - starting_coins)

        if remaining_cost > 0:
            time_required_hours = remaining_cost / gold_per_hour
            days = int(time_required_hours // 24)
            hours = int(time_required_hours % 24)
            minutes = int((time_required_hours % 1) * 60)
        else:
            days, hours, minutes = 0, 0, 0

        result_text = (f"Average rolls to get a '{target_rarity}' item: {average_rolls}\n"
                       f"Average total cost: {average_cost:,} coins\n"
                       f"Time required: {days} days, {hours} hours, {minutes} minutes\n\n"
                       "Average roll breakdown:\n" +
                       "\n".join(
                           f"{rarity.capitalize()}: {avg_count}" for rarity, avg_count in average_roll_counts.items()))
        result_label.configure(text=result_text)

    except ValueError as e:
        messagebox.showerror("Invalid Input", str(e))

root = ctk.CTk()
root.title("Custom Rarity Roll Simulator")
root.geometry("800x600")

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

frame_input = ctk.CTkFrame(root)
frame_input.pack(padx=20, pady=20, fill="both", expand=True)

frame_input.grid_rowconfigure(0, weight=1)
frame_input.grid_columnconfigure(0, weight=1)
frame_input.grid_columnconfigure(1, weight=1)

label_gold_per_hour = ctk.CTkLabel(frame_input, text="Gold per hour:")
label_gold_per_hour.grid(row=0, column=0, padx=0, pady=0, sticky="e")

entry_gold_per_hour = ctk.CTkEntry(frame_input, width=150)
entry_gold_per_hour.grid(row=0, column=1, padx=0, pady=0)

label_num_simulations = ctk.CTkLabel(frame_input, text="Number of simulations:")
label_num_simulations.grid(row=1, column=0, padx=0, pady=0, sticky="e")

entry_num_simulations = ctk.CTkEntry(frame_input, width=150)
entry_num_simulations.grid(row=1, column=1, padx=0, pady=0)

label_cost_per_roll = ctk.CTkLabel(frame_input, text="Cost per roll:")
label_cost_per_roll.grid(row=2, column=0, padx=0, pady=0, sticky="e")

entry_cost_per_roll = ctk.CTkEntry(frame_input, width=150)
entry_cost_per_roll.grid(row=2, column=1, padx=0, pady=0)

label_target_rarity = ctk.CTkLabel(frame_input, text="Target rarity:")
label_target_rarity.grid(row=3, column=0, padx=0, pady=0, sticky="e")

target_rarity_menu = ttk.Combobox(frame_input, values=list(rarities.keys()), state="readonly", width=15)
target_rarity_menu.grid(row=3, column=1, padx=0, pady=0)

label_rarity_name = ctk.CTkLabel(frame_input, text="Rarity Name:")
label_rarity_name.grid(row=4, column=0, padx=0, pady=0, sticky="e")

entry_rarity_name = ctk.CTkEntry(frame_input, width=150)
entry_rarity_name.grid(row=4, column=1, padx=0, pady=0)

label_probability = ctk.CTkLabel(frame_input, text="Probability:")
label_probability.grid(row=5, column=0, padx=0, pady=0, sticky="e")

entry_probability = ctk.CTkEntry(frame_input, width=150)
entry_probability.grid(row=5, column=1, padx=0, pady=0)

label_starting_coins = ctk.CTkLabel(frame_input, text="Starting Coins:")
label_starting_coins.grid(row=6, column=0, padx=0, pady=0, sticky="e")

entry_starting_coins = ctk.CTkEntry(frame_input, width=150)
entry_starting_coins.grid(row=6, column=1, padx=0, pady=0)

label_config_name = ctk.CTkLabel(frame_input, text="Configuration Name:")
label_config_name.grid(row=7, column=0, padx=0, pady=0, sticky="e")

entry_config_name = ctk.CTkEntry(frame_input, width=150)
entry_config_name.grid(row=7, column=1, padx=0, pady=0)

config_dropdown = ttk.Combobox(frame_input, state="readonly", width=15)
config_dropdown.grid(row=8, column=1, padx=0, pady=0)

button_add_rarity = ctk.CTkButton(frame_input, text="Add Rarity", command=add_rarity)
button_add_rarity.grid(row=9, column=0, padx=0, pady=5)

button_remove_rarity = ctk.CTkButton(frame_input, text="Remove Selected Rarity", command=remove_rarity)
button_remove_rarity.grid(row=9, column=1, padx=0, pady=5)

button_save_config = ctk.CTkButton(frame_input, text="Save Configuration", command=save_config)
button_save_config.grid(row=10, column=0, padx=0, pady=5)

button_load_config = ctk.CTkButton(frame_input, text="Load Configuration", command=load_config)
button_load_config.grid(row=10, column=1, padx=0, pady=5)

textbox_rarities = ctk.CTkTextbox(frame_input, width=300, height=200)
textbox_rarities.grid(row=11, column=0, columnspan=2, padx=5, pady=5)

button_simulate = ctk.CTkButton(frame_input, text="Simulate", command=simulate)
button_simulate.grid(row=12, column=0, columnspan=2, padx=0, pady=5)

frame_results = ctk.CTkFrame(root)
frame_results.pack(padx=20, pady=20, fill="both", expand=True)

result_label = ctk.CTkLabel(frame_results, text="", justify="left")
result_label.pack(padx=10, pady=10)

update_config_list()

root.mainloop()
