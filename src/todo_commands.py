import os
import json
from discord import Interaction
from typing import Optional
from discord.app_commands import Group, Choice, command, describe, choices
from text_style import Style, format
from user import load_json, user_initialized, update_today_is_today

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

    def set_todo_default(self, id: int):
        todo_path: str = os.path.join(str(id), "todolist.json")
        with open(todo_path, 'w') as f:
            f.write(f"[]")

    def read_todo(self, id: int):
        return load_json(id, "todolist.json")

    def update_todo(self, id: int, todo) -> None:
        todo_path: str = os.path.join(str(id), "todolist.json")
        with open(todo_path, 'w') as f:
            f.write(json.dumps(todo))

    def update_lifetime(self, id: int, todo):
        if not update_today_is_today(id):
            return

        for i in range(len(todo) - 1, -1, -1):
            if todo[i][1] == "Once":
                todo.pop(i)
                continue
            todo[i][2] = self.status[2].name;
        self.update_todo(id, todo)

    def __init__(self):
        super().__init__(name="todo", description="todo commands")

    @command(name="add", description="add task")
    @describe(name="task name")
    @choices(lifetime=lifetime)
    async def add(self, interaction: Interaction, name: str, lifetime: Optional[Choice[str]]) -> None:
        if msg := user_initialized(interaction.user.id):
            await interaction.response.send_message(msg)
            return

        if lifetime is None:
            lifetime = self.lifetime[0] 

        todo = self.read_todo(interaction.user.id)
        if todo == None:
            self.set_todo_default(interaction.user.id)
            await interaction.response.send_message("here is no item. You can use /todo add.")
            return

        todo.append([name, lifetime.name, self.status[2].name])
        self.update_todo(interaction.user.id, todo)
        await interaction.response.send_message("todo - add a new task " + name)

    @command(name="show", description="show task")
    @choices(lifetime=lifetime)
    async def show(self, interaction: Interaction, lifetime: Optional[Choice[str]]) -> None:
        if msg := user_initialized(interaction.user.id):
            await interaction.response.send_message(msg)
            return

        todo = self.read_todo(interaction.user.id)
        if todo == None:
            self.set_todo_default(interaction.user.id)
            await interaction.response.send_message("here is no item. You can use /todo add.")
            return
        result: str = "todo list:\n"
        if len(todo) != 0:
            self.update_lifetime(interaction.user.id, todo)
            for i in range(len(todo)):
                if lifetime:
                    if lifetime.name == todo[i][1]:
                        result += format(f"{i} - {todo[i][0]} {self.status_char[todo[i][2]]}\n", style=Style.BulletedList)
                else:
                    result += format(f"{i} - {todo[i][0]} {self.status_char[todo[i][2]]}\n", style=Style.BulletedList)
        else:
            result = "here is no things to do :)"
        await interaction.response.send_message(result)

    def set_status(self, user_id, todo, iden, status) -> str:
        list_len = len(todo)
        if list_len == 0:
            return "here is no item. You can use /todo add."
        if iden.isdigit():
            id = int(iden)
            if list_len <= id or id < 0:
                return f"todo - index {id} is invalid"

            todo[id][2] = status.name
            self.update_todo(user_id, todo)
            return ""

        for i in range(list_len):
            if iden == todo[i][0]:
                todo[i][2] = status.name
                self.update_todo(user_id, todo)
                return ""
        return ""

    def set_lifetime(self, user_id, todo, iden, lifetime) -> str:
        list_len = len(todo)
        if list_len == 0:
            return "here is no item. You can use /todo add."
        if iden.isdigit():
            id = int(iden)
            if list_len <= id or id < 0:
                return f"todo - index {id} is invalid"

            todo[id][1] = lifetime.name
            self.update_todo(user_id, todo)
            return ""

        for i in range(list_len):
            if iden == todo[i][0]:
                todo[i][1] = lifetime.name
                self.update_todo(user_id, todo)
                return ""
        return ""

    @command(name="set", description="set task status")
    @describe(iden="task id / name")
    @describe(status="status")
    @choices(status=status)
    @choices(lifetime=lifetime)
    async def set(self, interaction: Interaction, iden: str, status: Optional[Choice[str]], lifetime: Optional[Choice[str]]) -> None:
        if msg := user_initialized(interaction.user.id):
            await interaction.response.send_message(msg)
            return

        if status is None and lifetime is None: 
            await interaction.response.send_message("todo - obviously you did nothing")
            return

        todo = self.read_todo(interaction.user.id)
        if todo == None:
            self.set_todo_default(interaction.user.id)
            await interaction.response.send_message("here is no item. You can use /todo add.")
            return

        self.update_lifetime(interaction.user.id, todo)

        if status:
            msg = self.set_status(interaction.user.id, todo, iden, status)
            if msg != "":
                await interaction.response.send_message(msg)
                return

        if lifetime:
            msg = self.set_lifetime(interaction.user.id, todo, iden, lifetime)
            if msg != "":
                await interaction.response.send_message(msg)
                return

        response = f"todo - set {iden} {"" if not status else status.name} {"" if not lifetime else lifetime.name}"
        await interaction.response.send_message(response)

    @command(name="del", description="del a task")
    @describe(iden="task id / name")
    async def delete(self, interaction: Interaction, iden: str) -> None:
        if msg := user_initialized(interaction.user.id):
            await interaction.response.send_message(msg)
            return

        todo = self.read_todo(interaction.user.id)
        if todo == None:
            self.set_todo_default(interaction.user.id)
            await interaction.response.send_message("here is no item. You can use /todo add.")
            return
        list_len = len(todo)
        if list_len == 0:
            await interaction.response.send_message("here is no item. You can use /todo add.")
            return

        self.update_lifetime(interaction.user.id, todo)
        if iden.isdigit():
            id = int(iden)
            if list_len <= id or id < 0:
                await interaction.response.send_message(f"todo - there is no id {id}")
                return
            todo.pop(id)
            self.update_todo(interaction.user.id, todo)
            await interaction.response.send_message(f"todo - delete task with id {id}")
            return

        for i in range(list_len):
            if iden == todo[i][0]:
                todo.pop(i)
                await interaction.response.send_message(f"todo - delete task with name {iden}")
                self.update_todo(interaction.user.id, todo)
                return
        await interaction.response.send_message(f"todo - not find name {iden}")

