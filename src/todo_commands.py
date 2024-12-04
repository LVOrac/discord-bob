import os
import json
from discord import Interaction
from typing import Optional
from discord.app_commands import Group, Choice, command, describe, choices
from text_style import Style, format
from user import load_json, user_initialized, update_today_is_today

def read_listname(interaction: Interaction):
    return load_json(interaction, "listnames.json")

def get_listname(interaction: Interaction):
    listname = read_listname(interaction)
    if listname == None or listname[0] == '':
        return None
    return listname

def update_listname(interaction: Interaction, todo) -> None:
    path: str = os.path.join(str(interaction.user.id), "listnames.json")
    with open(path, 'w') as f:
        f.write(json.dumps(todo))

class TodoCommands(Group):
    status = [
        Choice(name="Done", value="Done"),
        Choice(name="In Progress", value="In progress"),
        Choice(name="Missing", value="Missing"),
    ]

    status_char = {
            status[0].name: '☑',
            status[1].name: '⧖',
            status[2].name: '☒',
    }

    lifetime = [
        Choice(name="Daily", value="daily"),
        Choice(name="Once", value="once"),
    ]

    def update_todo(self, interaction: Interaction, todo, name) -> None:
        todo_path: str = os.path.join(str(interaction.user.id), name)
        with open(todo_path, 'w') as f:
            f.write(json.dumps(todo))

    def update_lifetime(self, interaction: Interaction, todo, name) -> None:
        if not update_today_is_today(interaction):
            return

        for i in range(len(todo) - 1, -1, -1):
            if todo[i][1] == "Once":
                todo.pop(i)
                continue
            todo[i][2] = self.status[2].name;
        self.update_todo(interaction, todo, name)

    def __init__(self):
        super().__init__(name="todo", description="todo commands")
        self.add_command(self.ListCommands())

    class ListCommands(Group):
        def __init__(self):
            super().__init__(name="list", description="list commands")

        def set_listname_default(self, interaction: Interaction) -> None:
            path: str = os.path.join(str(interaction.user.id), "listnames.json")
            with open(path, 'w') as f:
                f.write("[\"\"]")

        def new_list(self, interaction: Interaction, name: str) -> None:
            path: str = os.path.join(str(interaction.user.id), f"{name}.json")
            with open(path, 'w') as f:
                f.write("[]")

        def rename_list(self, interaction: Interaction, old_name: str, new_name: str) -> None:
            old_path: str = os.path.join(str(interaction.user.id), f"{old_name}.json")
            new_path: str = os.path.join(str(interaction.user.id), f"{new_name}.json")
            os.rename(old_path, new_path)

        def del_list(self, interaction: Interaction, name: str) -> None:
            path: str = os.path.join(str(interaction.user.id), f"{name}.json")
            os.remove(path)

        @command(name="add", description="add a list")
        async def add(self, interaction: Interaction, name: str) -> None:
            if msg := user_initialized(interaction):
                await interaction.response.send_message(msg)
                return

            listname = read_listname(interaction)
            if listname == None:
                self.set_listname_default(interaction)
                listname = read_listname(interaction)

            if listname == None:
                await interaction.response.send_message("todo - not found listname.json")
                return

            if name.isdigit():
                await interaction.response.send_message(f"todo - list name cannot be number '{name}'")
                return

            if name in listname[1:]:
                await interaction.response.send_message(f"todo - list name {name} already exist")
                return

            listname.append(name)
            self.new_list(interaction, name)
            if len(listname) == 2:
                listname[0] = name
            update_listname(interaction, listname)
            await interaction.response.send_message(f"todo - add list {name}")

        @command(name="show", description="show lists")
        async def show(self, interaction: Interaction) -> None:
            if msg := user_initialized(interaction):
                await interaction.response.send_message(msg)
                return

            listname = read_listname(interaction)
            if listname == None or len(listname) == 1:
                await interaction.response.send_message("todo - here is no list")
                return

            ret = "### Lists\n"
            for i in range(1, len(listname)):
                ret += f"- [{i:>2}] " + listname[i] + (" <- " if listname[i] == listname[0] else '') + '\n'
            await interaction.response.send_message(ret)

        def find_iden_then(self, do, listname, iden: str) -> str:
            if iden.isdigit():
                id = int(iden)
                if len(listname) <= id or id < 1:
                    return f"todo - there is no id {id}"
                return do(listname, id)

            for i in range(1, len(listname)):
                if listname[i] == iden:
                    return do(listname, i)

            return f"todo - not find iden {iden}"

        @command(name="remove", description="remove a list")
        async def remove(self, interaction: Interaction, iden: str) -> None:
            if msg := user_initialized(interaction):
                await interaction.response.send_message(msg)

            listname = read_listname(interaction)
            if listname == None:
                self.set_listname_default(interaction)
                listname = read_listname(interaction)

            if listname == None:
                await interaction.response.send_message("todo - not found listname.json")

            if iden == listname:
                await interaction.response.send_message(f"todo - list {iden} already exist")

            def do(listname, i: int):
                if listname[0] == listname[i]:
                    listname[0] = ''
                self.del_list(interaction, listname[i])
                listname.pop(i)
                update_listname(interaction, listname)
                return f"todo - remove list {iden}"
            await interaction.response.send_message(self.find_iden_then(do, listname, iden))

        @command(name="rename", description="rename a list")
        async def rename(self, interaction: Interaction, iden: str, name: str) -> None:
            if msg := user_initialized(interaction):
                await interaction.response.send_message(msg)

            listname = read_listname(interaction)
            if listname == None:
                self.set_listname_default(interaction)
                listname = read_listname(interaction)

            if listname == None:
                await interaction.response.send_message("todo - not found listname.json")

            def do(listname, i: int):
                oldname = listname[i]
                listname[i] = name
                if listname[0] == oldname:
                    listname[0] = listname[i]
                self.rename_list(interaction, oldname, listname[i])
                update_listname(interaction, listname)
                return f"todo - rename list {oldname} to {name}"
            await interaction.response.send_message(self.find_iden_then(do, listname, iden))

    @command(name="help", description="show todo's functions")
    async def help(self, interaction: Interaction) -> None:
        help = """Usage:
        /todo <Commands> [settings ...]
Commands: add show set delete target
        """
        await interaction.response.send_message(format(help, style=Style.Bold))

    @command(name="target", description="show target list")
    async def target(self, interaction: Interaction) -> None:
        listname = read_listname(interaction)
        if listname == None or (listname[0] == '' and len(listname) == 1):
            await interaction.response.send_message("todo - here is no list. You can use /todo list add")
            return

        await interaction.response.send_message(f"todo - current target is {"not been setted" if listname[0] == '' else listname[0]}")

    @command(name="swtich", description="switch to another list")
    async def switch(self, interaction: Interaction, iden: str) -> None:
        listname = read_listname(interaction)
        if listname == None or (listname[0] == '' and len(listname) == 1):
            await interaction.response.send_message("todo - here is no list. You can use /todo list add")
            return

        def do(listname, i: int):
            oldname = listname[0]
            listname[0] = listname[i]
            update_listname(interaction, listname)
            return f"todo - switch from {"'current'" if oldname == '' else oldname} to {listname[0]}"

        await interaction.response.send_message(self.ListCommands().find_iden_then(do, listname, iden))

    @command(name="add", description="add task")
    @describe(name="task name")
    @choices(lifetime=lifetime)
    async def add(self, interaction: Interaction, name: str, lifetime: Optional[Choice[str]]) -> None:
        if msg := user_initialized(interaction):
            await interaction.response.send_message(msg)
            return

        if lifetime == None:
            lifetime = self.lifetime[0] 

        target = read_listname(interaction)
        if target == None or (target[0] == '' and len(target) == 1):
            await interaction.response.send_message("todo - here is no list. You can use /todo list add")
            return

        if target[0] == '':
           await interaction.response.send_message("todo - here is no target list. You can use /todo switch")
           return

        target = f"{target[0]}.json"
        todo = load_json(interaction, target)
        if todo == None:
            await interaction.response.send_message(f"todo - target {target} is missing")
            return

        self.update_lifetime(interaction, todo, target)
        todo.append([name, lifetime.name, self.status[2].name])
        self.update_todo(interaction, todo, target)
        await interaction.response.send_message("todo - add a new task " + name)

    @command(name="show", description="show task")
    @choices(lifetime=lifetime)
    async def show(self, interaction: Interaction, lifetime: Optional[Choice[str]]) -> None:
        if msg := user_initialized(interaction):
            await interaction.response.send_message(msg)
            return

        listname = read_listname(interaction)
        if listname == None or (listname[0] == '' and len(listname) == 1):
            await interaction.response.send_message("todo - here is no list. You can use /todo list add")
            return

        if listname[0] == '':
           await interaction.response.send_message("todo - here is no target list. You can use /todo switch")
           return

        target = f"{listname[0]}.json"
        todo = load_json(interaction, target)
        if todo == None:
            await interaction.response.send_message(f"todo - target {target} is missing")
            return

        result: str = f"### {listname[0]} Tasks:\n"
        if len(todo) != 0:
            self.update_lifetime(interaction, todo, target)
            for i in range(len(todo)):
                if lifetime:
                    if lifetime.name == todo[i][1]:
                        result += format(f"[{i:>2}] - {todo[i][0]} {self.status_char[todo[i][2]]}\n", style=Style.BulletedList)
                else:
                    result += format(f"[{i:>2}] - {todo[i][0]} {self.status_char[todo[i][2]]}\n", style=Style.BulletedList)
        else:
            result = "here is no things to do :)"
        await interaction.response.send_message(result)

    def find_item_then(self, todo, iden, do) -> str:
        list_len = len(todo)
        if list_len == 0:
            return "here is no item. You can use /todo add."
        if iden.isdigit():
            id = int(iden)
            if list_len <= id or id < 0:
                return f"todo - index {id} is invalid"
            return do(todo, id)

        for i in range(list_len):
            if iden == todo[i][0]:
                return do(todo, i)
        return ""

    @command(name="set", description="set task status")
    @describe(iden="task id / name")
    @describe(status="status")
    @choices(status=status)
    @choices(lifetime=lifetime)
    async def set(self, interaction: Interaction, iden: str, status: Optional[Choice[str]], lifetime: Optional[Choice[str]]) -> None:
        if msg := user_initialized(interaction):
            await interaction.response.send_message(msg)
            return

        if status is None and lifetime is None: 
            await interaction.response.send_message("todo - obviously you did nothing")
            return

        target = read_listname(interaction)
        if target == None or (target[0] == '' and len(target) == 1):
            await interaction.response.send_message("todo - here is no list. You can use /todo list add")
            return

        if target[0] == '':
           await interaction.response.send_message("todo - here is no target list. You can use /todo switch")
           return

        target = f"{target[0]}.json"
        todo = load_json(interaction, target)
        if todo == None:
            await interaction.response.send_message(f"todo - target {target} is missing")
            return

        self.update_lifetime(interaction, todo, target)

        if status:
            def do(todo, i: int):
                todo[i][2] = status.name
                self.update_todo(interaction, todo, target)
                return ""
            msg = self.find_item_then(todo, iden, do)
            if msg != "":
                await interaction.response.send_message(msg)
                return

        if lifetime:
            def do(todo, i: int):
                todo[i][1] = lifetime.name
                self.update_todo(interaction, todo, target)
                return ""
            msg = self.find_item_then(todo, iden, do)
            if msg != "":
                await interaction.response.send_message(msg)
                return

        response = f"todo - set {iden} {"" if not status else status.name} {"" if not lifetime else lifetime.name}"
        await interaction.response.send_message(response)

    @command(name="del", description="del a task")
    @describe(iden="task id / name")
    async def delete(self, interaction: Interaction, iden: str) -> None:
        if msg := user_initialized(interaction):
            await interaction.response.send_message(msg)
            return

        target = read_listname(interaction)
        if target == None or (target[0] == '' and len(target) == 1):
            await interaction.response.send_message("todo - here is no list. You can use /todo list add")
            return

        if target[0] == '':
           await interaction.response.send_message("todo - here is no target list. You can use /todo switch")
           return

        target = f"{target[0]}.json"
        todo = load_json(interaction, target)
        if todo == None:
            await interaction.response.send_message(f"todo - target {target} is missing")
            return

        def do(todo, i: int):
            todo.pop(i)
            self.update_todo(interaction, todo, target)
            return ""

        if msg := self.find_item_then(todo, iden, do):
            await interaction.response.send_message(msg)
            return

        await interaction.response.send_message(f"todo - not find name {iden}")

