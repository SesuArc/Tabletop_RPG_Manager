import sqlite3
from tkinter import *
from tkinter import messagebox

conn = sqlite3.connect('rpg_characters.db')
c = conn.cursor()

# Character Table
c.execute('''CREATE TABLE IF NOT EXISTS characters (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT NOT NULL,
             description TEXT NOT NULL,
             level INTEGER DEFAULT 1)''')

# Armor Table
c.execute('''CREATE TABLE IF NOT EXISTS armors (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT NOT NULL,
             description TEXT NOT NULL,
             bonus INTEGER DEFAULT 0)''')

# Character_Armor Joint Table
c.execute('''CREATE TABLE IF NOT EXISTS character_armor (
             character_id INTEGER,
             armor_id INTEGER,
             FOREIGN KEY(character_id) REFERENCES characters(id),
             FOREIGN KEY(armor_id) REFERENCES armors(id))''')

# Monster Table
c.execute('''CREATE TABLE IF NOT EXISTS monsters (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT NOT NULL,
             description TEXT NOT NULL,
             battle_power INTEGER DEFAULT 1)''')

conn.commit()

root = Tk()
root.title("Tabletop RPG Manager")
root.geometry("1200x1000")

# Canvas and Scrollbar
canvas = Canvas(root)
canvas.pack(side=LEFT, fill=BOTH, expand=True)

scrollbar = Scrollbar(root, orient=VERTICAL, command=canvas.yview)
scrollbar.pack(side=RIGHT, fill=Y)

canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

main_frame = Frame(canvas)
canvas.create_window((0, 0), window=main_frame, anchor="nw")

# Initiate Lists
selected_characters = []
selected_armors = []
selected_battle_characters = []
selected_battle_monsters = []

#Character Functions
def addCharacter():
    name = entryName.get()
    description = entryDescription.get("1.0", END)
    level = int(levelSpinbox.get())

    if name and description.strip():
        c.execute("INSERT INTO characters (name, description, level) VALUES (?, ?, ?)",
                  (name, description.strip(), level))
        conn.commit()
        messagebox.showinfo("Success", "Character added!")

        # Clear input fields
        entryName.delete(0, END)
        entryDescription.delete("1.0", END)
        levelSpinbox.delete(0, "end")
        levelSpinbox.insert(0, "1")

        refreshCharacterList()
    else:
        messagebox.showwarning("Input Error", "Please provide both name and description.")

def deleteCharacter():
    try:
        selectedCharacter = listboxCharacters.get(listboxCharacters.curselection())
        c.execute("DELETE FROM characters WHERE name=?", (selectedCharacter,))
        conn.commit()
        messagebox.showinfo("Success", "Character deleted!")
        refreshCharacterList()
    except:
        messagebox.showwarning("Delete Error", "Please select a character to delete.")

def loadCharacter(event):
    try:
        selectedCharacter = listboxCharacters.get(listboxCharacters.curselection())
        c.execute("SELECT name, description, level FROM characters WHERE name=?", (selectedCharacter,))
        character = c.fetchone()

        if character:
            entryName.delete(0, END)
            entryName.insert(END, character[0])

            entryDescription.delete("1.0", END)
            entryDescription.insert(END, character[1])

            levelSpinbox.delete(0, "end")
            levelSpinbox.insert(0, character[2])

            # Fetch character equipment
            c.execute('''SELECT armors.name, armors.bonus FROM armors
                                     JOIN character_armor ON armors.id = character_armor.armor_id
                                     JOIN characters ON characters.id = character_armor.character_id
                                     WHERE characters.name=?''', (selectedCharacter,))
            equipped_armors = c.fetchall()

            if equipped_armors:
                armor_names = [armor[0] for armor in equipped_armors]
                total_bonus = sum(armor[1] for armor in equipped_armors)
                battlePower = int(character[2]) + total_bonus
                labelEquippedArmor.config(text=f"Equipment: {', '.join(armor_names)}")
                labelBattlePower.config(text=f"Battle Power: {battlePower}")
                updateEquipList(equipped_armors)
            else:
                labelEquippedArmor.config(text="Equipment: None")
                labelBattlePower.config(text="Battle Power: {}".format(character[2]))
                updateEquipList([])

    except:
        pass

def refreshCharacterList():
    listboxCharacters.delete(0, END)
    c.execute("SELECT name FROM characters")
    characters = c.fetchall()
    for character in characters:
        listboxCharacters.insert(END, character[0])

def updateCharacterLevel(level):
    try:
        if level.strip() == "":
            return
        selectedCharacter = listboxCharacters.get(listboxCharacters.curselection())
        c.execute("UPDATE characters SET level=? WHERE name=?", (int(level), selectedCharacter))
        conn.commit()
    except ValueError:
        messagebox.showwarning("Update Error", "Please enter a valid integer for character level.")
    except Exception as e:
        messagebox.showwarning("Update Error", f"Error updating character level: {e}")

def updateCharacterBattlePower():
    try:
        selected_index = listboxCharacters.curselection()
        if not selected_index:
            return

        selectedCharacter = listboxCharacters.get(selected_index[0])

        c.execute("SELECT level FROM characters WHERE name=?", (selectedCharacter,))
        character_level = c.fetchone()[0]

        c.execute('''SELECT SUM(armors.bonus) FROM armors
                     JOIN character_armor ON armors.id = character_armor.armor_id
                     JOIN characters ON characters.id = character_armor.character_id
                     WHERE characters.name=?''', (selectedCharacter,))
        total_bonus = c.fetchone()[0] or 0

        battle_power = character_level + total_bonus
        labelBattlePower.config(text=f"Battle Power: {battle_power}")
    except Exception as e:
        messagebox.showwarning("Error", f"Failed to update battle power: {e}")

def searchCharacter(event):
    query = entrySearchCharacter.get().lower()
    listboxCharacters.delete(0, END)
    c.execute("SELECT name FROM characters WHERE LOWER(name) LIKE ?", (f'%{query}%',))
    characters = c.fetchall()
    for character in characters:
        listboxCharacters.insert(END, character[0])

# Armor Functions
def addArmor():
    name = entryArmorName.get()
    description = entryArmorDescription.get("1.0", END)
    bonus = int(bonusSpinbox.get())

    if name and description.strip():
        c.execute("INSERT INTO armors (name, description, bonus) VALUES (?, ?, ?)",
                  (name, description.strip(), bonus))
        conn.commit()
        messagebox.showinfo("Success", "Equipment added!")

        # Clear input fields
        entryArmorName.delete(0, END)
        entryArmorDescription.delete("1.0", END)
        bonusSpinbox.delete(0, "end")
        bonusSpinbox.insert(0, "0")

        refreshArmorList()
    else:
        messagebox.showwarning("Input Error", "Please provide both name and description.")


def deleteArmor():
    try:
        selectedArmor = listboxArmors.get(listboxArmors.curselection())
        c.execute("DELETE FROM armors WHERE name=?", (selectedArmor,))
        conn.commit()
        messagebox.showinfo("Success", "equipment deleted!")
        refreshArmorList()
    except:
        messagebox.showwarning("Delete Error", "Please select an item to delete.")

def loadArmor(event):
    try:
        selectedArmor = listboxArmors.get(listboxArmors.curselection())
        c.execute("SELECT name, description, bonus FROM armors WHERE name=?", (selectedArmor,))
        armor = c.fetchone()

        if armor:
            entryArmorName.delete(0, END)
            entryArmorName.insert(END, armor[0])

            entryArmorDescription.delete("1.0", END)
            entryArmorDescription.insert(END, armor[1])

            bonusSpinbox.delete(0, "end")
            bonusSpinbox.insert(0, armor[2])
    except:
        pass


def refreshArmorList():
    listboxArmors.delete(0, END)
    c.execute("SELECT name FROM armors")
    armors = c.fetchall()
    for armor in armors:
        listboxArmors.insert(END, armor[0])

def updateArmorBonus(bonus):
    try:
        if bonus.strip() == "":
            return

        selected_index = listboxArmors.curselection()
        if not selected_index:
            return

        selectedArmor = listboxArmors.get(selected_index[0])

        c.execute("UPDATE armors SET bonus=? WHERE name=?", (int(bonus), selectedArmor))
        conn.commit()
    except ValueError:
        messagebox.showwarning("Update Error", "Please enter a valid integer for armor bonus.")
    except Exception as e:
        messagebox.showwarning("Update Error", f"Error updating armor bonus: {e}")

def searchArmor(event):
    query = entrySearchArmor.get().lower()
    listboxArmors.delete(0, END)
    c.execute("SELECT name FROM armors WHERE LOWER(name) LIKE ?", (f'%{query}%',))
    armors = c.fetchall()
    for armor in armors:
        listboxArmors.insert(END, armor[0])

# Equip Functions
def addCharacterToEquip():
    try:
        selectedCharacter = listboxCharacters.get(listboxCharacters.curselection())
        if selectedCharacter not in selected_characters:
            selected_characters.append(selectedCharacter)
            messagebox.showinfo("Success", f"{selectedCharacter} added to equip list!")
        refreshEquipList()
    except:
        messagebox.showwarning("Selection Error", "Please select a character to add.")

def addArmorToEquip():
    try:
        selectedArmor = listboxArmors.get(listboxArmors.curselection())
        if selectedArmor not in selected_armors:
            selected_armors.append(selectedArmor)
            messagebox.showinfo("Success", f"{selectedArmor} added to equip list!")
        refreshEquipList()
    except:
        messagebox.showwarning("Selection Error", "Please select equipment to add.")

# Equip armor
def equipAll():
    if not selected_characters or not selected_armors:
        messagebox.showwarning("Equip Error", "Please add both characters and equipment to equip.")
        return

    for character in selected_characters:
        for armor in selected_armors:

            c.execute("SELECT id FROM characters WHERE name=?", (character,))
            character_id = c.fetchone()[0]

            c.execute("SELECT id FROM armors WHERE name=?", (armor,))
            armor_id = c.fetchone()[0]

            c.execute("INSERT INTO character_armor (character_id, armor_id) VALUES (?, ?)", (character_id, armor_id))
            conn.commit()

    messagebox.showinfo("Success", "All selected characters have equipped all selected equipment!")
    refreshCharacterList()
    selected_characters.clear()
    selected_armors.clear()
    refreshEquipList()

def unequipAll():
    if not selected_characters or not selected_armors:
        messagebox.showwarning("Unequip Error", "Please add both characters and equipment to unequip.")
        return

    for character in selected_characters:
        for armor in selected_armors:

            c.execute("SELECT id FROM characters WHERE name=?", (character,))
            character_id = c.fetchone()[0]

            c.execute("SELECT id FROM armors WHERE name=?", (armor,))
            armor_id = c.fetchone()[0]

            c.execute("DELETE FROM character_armor WHERE character_id=? AND armor_id=?", (character_id, armor_id))
            conn.commit()

    messagebox.showinfo("Success", "All selected characters have unequipped all selected equipment!")
    refreshCharacterList()
    selected_characters.clear()
    selected_armors.clear()
    refreshEquipList()

def refreshEquipList():
    listboxEquip.delete(0, END)
    if selected_characters:
        listboxEquip.insert(END, "Characters to Equip:")
        for character in selected_characters:
            listboxEquip.insert(END, f" - {character}")
    if selected_armors:
        listboxEquip.insert(END, "Equipment to Equip:")
        for armor in selected_armors:
            listboxEquip.insert(END, f" - {armor}")

def updateEquipList(equipped_armors):
    listboxEquip.delete(0, END)
    for armor in equipped_armors:
        listboxEquip.insert(END, armor[0])

def clearEquipList():
    selected_characters.clear()
    selected_armors.clear()
    refreshEquipList()
    messagebox.showinfo("Success", "Equip list cleared!")

# Monster Functions
def addMonster():
    name = entryMonsterName.get()
    description = entryMonsterDescription.get("1.0", END)
    battle_power = int(battlePowerSpinbox.get())

    if name and description.strip():
        c.execute("INSERT INTO monsters (name, description, battle_power) VALUES (?, ?, ?)",
                  (name, description.strip(), battle_power))
        conn.commit()
        messagebox.showinfo("Success", "Monster added!")

        entryMonsterName.delete(0, END)
        entryMonsterDescription.delete("1.0", END)
        battlePowerSpinbox.delete(0, "end")
        battlePowerSpinbox.insert(0, "1")

        refreshMonsterList()
    else:
        messagebox.showwarning("Input Error", "Please provide both name and description.")

def deleteMonster():
    try:
        selectedMonster = listboxMonsters.get(listboxMonsters.curselection())
        c.execute("DELETE FROM monsters WHERE name=?", (selectedMonster,))
        conn.commit()
        messagebox.showinfo("Success", "Monster deleted!")
        refreshMonsterList()
    except:
        messagebox.showwarning("Delete Error", "Please select a monster to delete.")

def loadMonster(event):
    try:
        selectedMonster = listboxMonsters.get(listboxMonsters.curselection())
        c.execute("SELECT name, description, battle_power FROM monsters WHERE name=?", (selectedMonster,))
        monster = c.fetchone()

        if monster:
            entryMonsterName.delete(0, END)
            entryMonsterName.insert(END, monster[0])

            entryMonsterDescription.delete("1.0", END)
            entryMonsterDescription.insert(END, monster[1])

            battlePowerSpinbox.delete(0, "end")
            battlePowerSpinbox.insert(0, monster[2])

    except Exception as e:
        print(f"Error loading monster: {e}")

def refreshMonsterList():
    listboxMonsters.delete(0, END)
    c.execute("SELECT name FROM monsters")
    monsters = c.fetchall()
    for monster in monsters:
        listboxMonsters.insert(END, monster[0])

def updateMonsterPower(power):
    try:
        if power.strip() == "":
            return
        selectedMonster = listboxMonsters.get(listboxMonsters.curselection())
        c.execute("UPDATE monsters SET battle_power=? WHERE name=?", (int(power), selectedMonster))
        conn.commit()
    except ValueError:
        messagebox.showwarning("Update Error", "Please enter a valid integer for monster power.")
    except Exception as e:
        messagebox.showwarning("Update Error", f"Error updating monster power: {e}")


def searchMonster(event):
    query = entrySearchMonster.get().lower()
    listboxMonsters.delete(0, END)
    c.execute("SELECT name FROM monsters WHERE LOWER(name) LIKE ?", (f'%{query}%',))
    monsters = c.fetchall()
    for monster in monsters:
        listboxMonsters.insert(END, monster[0])

# Battle Menu
def addCharacterToBattle():
    try:
        selectedCharacter = listboxCharacters.get(listboxCharacters.curselection())
        if selectedCharacter not in selected_battle_characters:
            selected_battle_characters.append(selectedCharacter)
            messagebox.showinfo("Success", f"{selectedCharacter} added to battle!")
        refreshBattleList()
    except:
        messagebox.showwarning("Selection Error", "Please select a character to add.")

def addMonsterToBattle():
    try:
        selectedMonster = listboxMonsters.get(listboxMonsters.curselection())
        if selectedMonster not in selected_battle_monsters:
            selected_battle_monsters.append(selectedMonster)
            messagebox.showinfo("Success", f"{selectedMonster} added to battle!")
        refreshBattleList()
    except:
        messagebox.showwarning("Selection Error", "Please select a monster to add.")

def refreshBattleList():
    listboxBattle.delete(0, END)
    if selected_battle_characters:
        listboxBattle.insert(END, "Characters in Battle:")
        for character in selected_battle_characters:
            listboxBattle.insert(END, f" - {character}")
    if selected_battle_monsters:
        listboxBattle.insert(END, "Monsters in Battle:")
        for monster in selected_battle_monsters:
            listboxBattle.insert(END, f" - {monster}")

def calculateBattle():
    char_total = sum(fetchBattlePower(name, "characters") for name in selected_battle_characters)
    monster_total = sum(fetchBattlePower(name, "monsters") for name in selected_battle_monsters)

    char_modifier = int(charModifierSpinbox.get())
    monster_modifier = int(monModifierSpinbox.get())

    final_char_power = char_total + char_modifier
    final_monster_power = monster_total + monster_modifier

    if final_char_power > final_monster_power:
        result = "Characters Win!"
    elif final_monster_power > final_char_power:
        result = "Monsters Win!"
    else:
        result = "It's a Draw!"

    messagebox.showinfo("Battle Result", f"{result}\n"
                                         f"Characters: {final_char_power}\n"
                                         f"Monsters: {final_monster_power}")

def fetchBattlePower(name, table):
    if table == "characters":
        c.execute("SELECT level FROM characters WHERE name=?", (name,))
        character_level = c.fetchone()[0]

        c.execute('''SELECT SUM(armors.bonus) FROM armors
                     JOIN character_armor ON armors.id = character_armor.armor_id
                     JOIN characters ON characters.id = character_armor.character_id
                     WHERE characters.name=?''', (name,))
        total_bonus = c.fetchone()[0] or 0

        return character_level + total_bonus

    elif table == "monsters":
        c.execute("SELECT battle_power FROM monsters WHERE name=?", (name,))
        return c.fetchone()[0]

def clearBattleList():
    selected_battle_characters.clear()
    selected_battle_monsters.clear()
    refreshBattleList()
    messagebox.showinfo("Success", "Battle list cleared!")

# GUI
# Character Frame
frameCharacters = LabelFrame(main_frame, text="Characters", padx=10, pady=10)
frameCharacters.pack(side=LEFT, fill=BOTH, expand=True)

labelName = Label(frameCharacters, text="Character Name:")
labelName.pack(pady=5)
entryName = Entry(frameCharacters)
entryName.pack(pady=5, fill=X)

# character description
labelDescription = Label(frameCharacters, text="Character Description:")
labelDescription.pack(pady=5)
entryDescription = Text(frameCharacters, height=5, width=30)
entryDescription.pack(pady=5, fill=X)

# Character Level and battle power update
level_var = StringVar(value="0")
labelLevel = Label(frameCharacters, text="Character Level:")
labelLevel.pack(pady=5)
levelSpinbox = Spinbox(
    frameCharacters, from_=-100, to=10000, textvariable=level_var
)
levelSpinbox.pack(pady=5, fill=X)
level_var.trace("w", lambda *args: [updateCharacterLevel(level_var.get()), updateCharacterBattlePower()])

# Add and Delete Character buttons
btnAddCharacter = Button(frameCharacters, text="Add Character", command=addCharacter)
btnAddCharacter.pack(pady=10)

btnDeleteCharacter = Button(frameCharacters, text="Delete Character", command=deleteCharacter)
btnDeleteCharacter.pack(pady=5)

labelListCharacters = Label(frameCharacters, text="Character List")
labelListCharacters.pack(pady=5)

# Character List Frame
frameCharacterList = Frame(frameCharacters)
frameCharacterList.pack(pady=5, fill=BOTH, expand=True)

# Character Scrollbar
scrollbarCharacters = Scrollbar(frameCharacterList)
scrollbarCharacters.pack(side=RIGHT, fill=Y)

listboxCharacters = Listbox(frameCharacterList, yscrollcommand=scrollbarCharacters.set)
listboxCharacters.pack(pady=5, fill=BOTH, expand=True)
listboxCharacters.bind('<<ListboxSelect>>', loadCharacter)

scrollbarCharacters.config(command=listboxCharacters.yview)

# Add character to Equip menu
btnAddCharacterToEquip = Button(frameCharacters, text="Add to Equip", command=addCharacterToEquip)
btnAddCharacterToEquip.pack(pady=5)

# Equipped Items
labelEquippedArmor = Label(frameCharacters, text="Equipped items: None")
labelEquippedArmor.pack(pady=5)

# Battle Power
labelBattlePower = Label(frameCharacters, text="Battle Power: 0")
labelBattlePower.pack(pady=5)

# Equipment Frame
frameArmors = LabelFrame(main_frame, text="Equipment", padx=10, pady=10)
frameArmors.pack(side=LEFT, fill=BOTH, expand=True)

labelArmorName = Label(frameArmors, text="Equipment Name:")
labelArmorName.pack(pady=5)
entryArmorName = Entry(frameArmors)
entryArmorName.pack(pady=5, fill=X)

# Equipment Description
labelArmorDescription = Label(frameArmors, text="Equipment Description:")
labelArmorDescription.pack(pady=5)
entryArmorDescription = Text(frameArmors, height=5, width=30)
entryArmorDescription.pack(pady=5, fill=X)

# Equipment Bonus and real time battle power update
armor_bonus_var = StringVar(value="0")
labelArmorBonus = Label(frameArmors, text="Equipment Bonus:")
labelArmorBonus.pack(pady=5)
bonusSpinbox = Spinbox(
    frameArmors, from_=-10000, to=10000, textvariable=armor_bonus_var
)
bonusSpinbox.pack(pady=5, fill=X)

armor_bonus_var.trace("w", lambda *args: [updateArmorBonus(armor_bonus_var.get()), updateCharacterBattlePower()])

# Add and Delete Armor buttons
btnAddArmor = Button(frameArmors, text="Add Equipment", command=addArmor)
btnAddArmor.pack(pady=10)

btnDeleteArmor = Button(frameArmors, text="Delete Equipment", command=deleteArmor)
btnDeleteArmor.pack(pady=5)

labelListArmors = Label(frameArmors, text="Equipment List")
labelListArmors.pack(pady=5)

# Equipment List Frame
frameArmorList = Frame(frameArmors)
frameArmorList.pack(pady=5, fill=BOTH, expand=True)

# SEquipment Scrollbar
scrollbarArmors = Scrollbar(frameArmorList)
scrollbarArmors.pack(side=RIGHT, fill=Y)

listboxArmors = Listbox(frameArmorList, yscrollcommand=scrollbarArmors.set)
listboxArmors.pack(pady=5, fill=BOTH, expand=True)

scrollbarArmors.config(command=listboxArmors.yview)

listboxArmors.bind('<<ListboxSelect>>', loadArmor)

# Add Equipment to Equip Menu
btnAddArmorToEquip = Button(frameArmors, text="Add to Equip", command=addArmorToEquip)
btnAddArmorToEquip.pack(pady=5)

# Equip List Frame
frameEquipList = LabelFrame(main_frame, text="Equip List", padx=10, pady=10)
frameEquipList.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)

frameEquipButtons = Frame(frameEquipList)
frameEquipButtons.grid(row=0, column=0, columnspan=2, pady=(0, 5))

# Equip All Button
btnEquipAll = Button(frameEquipButtons, text="Equip All", command=equipAll)
btnEquipAll.grid(row=0, column=0, padx=5)

# Unequip All Button
btnUnequipAll = Button(frameEquipButtons, text="Unequip All", command=unequipAll)
btnUnequipAll.grid(row=0, column=1, padx=5)

listboxEquip = Listbox(frameEquipList)
listboxEquip.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

scrollbarEquip = Scrollbar(frameEquipList, orient=VERTICAL, command=listboxEquip.yview)
scrollbarEquip.grid(row=1, column=1, sticky="ns", pady=5)

listboxEquip.config(yscrollcommand=scrollbarEquip.set)

frameEquipList.grid_rowconfigure(1, weight=1)
frameEquipList.grid_columnconfigure(0, weight=1)

# Clear Equip List Button
btnClearEquip = Button(frameEquipList, text="Clear Equip List", command=clearEquipList)
btnClearEquip.grid(row=2, column=0, columnspan=2, pady=(5, 0))

# Monster Frame
frameMonsters = LabelFrame(main_frame, text="Monsters", padx=10, pady=10)
frameMonsters.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)

# Monster Name Input
labelMonsterName = Label(frameMonsters, text="Monster Name:")
labelMonsterName.pack(pady=5)
entryMonsterName = Entry(frameMonsters)
entryMonsterName.pack(pady=5, fill=X)

# Monster Description Input
labelMonsterDescription = Label(frameMonsters, text="Monster Description:")
labelMonsterDescription.pack(pady=5)
entryMonsterDescription = Text(frameMonsters, height=5, width=30)
entryMonsterDescription.pack(pady=5, fill=X)

# Monster Battle Power Input
monster_power_var = StringVar(value=0)
labelMonsterPower = Label(frameMonsters, text="Monster Battle Power:")
labelMonsterPower.pack(pady=5)
battlePowerSpinbox = Spinbox(frameMonsters, from_=0, to=10000, textvariable=monster_power_var)
battlePowerSpinbox.pack(pady=5, fill=X)
monster_power_var.trace("w", lambda *args: updateMonsterPower(monster_power_var.get()))

# Add and Delete Monster Buttons
btnAddMonster = Button(frameMonsters, text="Add Monster", command=addMonster)
btnAddMonster.pack(pady=10)

btnDeleteMonster = Button(frameMonsters, text="Delete Monster", command=deleteMonster)
btnDeleteMonster.pack(pady=5)

# Monster List Label
labelListMonsters = Label(frameMonsters, text="Monster List")
labelListMonsters.pack(pady=5)

# Monster List Frame with Scrollbar
frameMonsterList = Frame(frameMonsters)
frameMonsterList.pack(pady=5, fill=BOTH, expand=True)

scrollbarMonsters = Scrollbar(frameMonsterList)
scrollbarMonsters.pack(side=RIGHT, fill=Y)

listboxMonsters = Listbox(frameMonsterList, yscrollcommand=scrollbarMonsters.set)
listboxMonsters.pack(pady=5, fill=BOTH, expand=True)
listboxMonsters.bind('<<ListboxSelect>>', loadMonster)

scrollbarMonsters.config(command=listboxMonsters.yview)

# Search Bars
# Characters
labelSearchCharacter = Label(frameCharacters, text="Search Character:")
labelSearchCharacter.pack(pady=5)

entrySearchCharacter = Entry(frameCharacters)
entrySearchCharacter.pack(pady=5, fill=X)
entrySearchCharacter.bind("<KeyRelease>", searchCharacter)

labelListCharacters = Label(frameCharacters, text="Character List")
labelListCharacters.pack(pady=5)

# Battle Frame
frameBattle = LabelFrame(main_frame, text="Battle Menu", padx=10, pady=10)
frameBattle.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)

# Battle List
scrollbarBattle = Scrollbar(frameBattle)
scrollbarBattle.pack(side=RIGHT, fill=Y)

listboxBattle = Listbox(frameBattle, yscrollcommand=scrollbarBattle.set)
listboxBattle.pack(pady=5, fill=BOTH, expand=True)

scrollbarBattle.config(command=listboxBattle.yview)

# Add to Battle
btnAddCharToBattle = Button(frameBattle, text="Add Character to Battle", command=addCharacterToBattle)
btnAddCharToBattle.pack(pady=5)

btnAddMonToBattle = Button(frameBattle, text="Add Monster to Battle", command=addMonsterToBattle)
btnAddMonToBattle.pack(pady=5)

# clear battle menu
btnClearBattle = Button(frameBattle, text="Clear Battle List", command=clearBattleList)
btnClearBattle.pack(pady=5)

# Battle Modifiers
labelCharModifier = Label(frameBattle, text="Character Modifier:")
labelCharModifier.pack(pady=5)
charModifierSpinbox = Spinbox(frameBattle, from_=-100, to=100)
charModifierSpinbox.pack(pady=5, fill=X)
charModifierSpinbox.delete(0, "end")
charModifierSpinbox.insert(0, "0")

labelMonModifier = Label(frameBattle, text="Monster Modifier:")
labelMonModifier.pack(pady=5)
monModifierSpinbox = Spinbox(frameBattle, from_=-100, to=100)
monModifierSpinbox.pack(pady=5, fill=X)
monModifierSpinbox.delete(0, "end")
monModifierSpinbox.insert(0, "0")

# Calculate battle
btnCalculateBattle = Button(frameBattle, text="Calculate Battle", command=calculateBattle)
btnCalculateBattle.pack(pady=10)

# Monster Search Bar
labelSearchMonster = Label(frameMonsters, text="Search Monster:")
labelSearchMonster.pack(pady=5)

entrySearchMonster = Entry(frameMonsters)
entrySearchMonster.pack(pady=5, fill=X)
entrySearchMonster.bind("<KeyRelease>", searchMonster)

labelListMonsters = Label(frameMonsters, text="Monster List")
labelListMonsters.pack(pady=5)

# Equipment Search Bar
labelSearchArmor = Label(frameArmors, text="Search Equipment:")
labelSearchArmor.pack(pady=5)

entrySearchArmor = Entry(frameArmors)
entrySearchArmor.pack(pady=5, fill=X)
entrySearchArmor.bind("<KeyRelease>", searchArmor)

labelListArmors = Label(frameArmors, text="Equipment List")
labelListArmors.pack(pady=5)

refreshMonsterList()
refreshCharacterList()
refreshArmorList()
refreshEquipList()

root.mainloop()

conn.close()
