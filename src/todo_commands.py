import os
import json
from discord import app_commands
from discord import Interaction
from typing import Optional
from text_style import Style, format

def read_todo(id: int):
    todo_path: str = os.path.join(str(id), "todolist.json")
    if not os.path.exists(todo_path):
        with open(todo_path, 'w') as f:
            f.write("[]")
    with open(todo_path, 'r') as f:
        return json.load(f)

def update_todo(id: int, todo: str) -> None:
    todo_path: str = os.path.join(str(id), "todolist.json")
    with open(todo_path, 'w') as f:
        f.write(todo)

class TodoCommands(app_commands.Group):
    def __init__(self):
        super().__init__(name="todo", description="todo commands")

    status = [
        app_commands.Choice(name="Done", value="Done"),
        app_commands.Choice(name="In Progress", value="In progress"),
        app_commands.Choice(name="Missing", value="Missing"),
    ]

    status_char = {
            status[0].name: '☑',
            status[1].name: '⧖',
            status[2].name: '☒',
    }

    lifetime = [
        app_commands.Choice(name="Once", value="once"),
        app_commands.Choice(name="Daily", value="daily"),
    ]

    @app_commands.command(name="add", description="add task")
    @app_commands.describe(name="task name")
    @app_commands.choices(lifetime=lifetime)
    async def add(self, interaction: Interaction, name: str, lifetime: Optional[app_commands.Choice[str]]) -> None:
        if lifetime is None:
            lifetime = self.lifetime[0] 
        todo = read_todo(interaction.user.id)
        todo.append([name, lifetime.name, self.status[2].name])
        update_todo(interaction.user.id, json.dumps(todo))
        await interaction.response.send_message("todo - add a new task " + name)

    @app_commands.command(name="show", description="show task")
    @app_commands.choices(lifetime=lifetime)
    async def show(self, interaction: Interaction, lifetime: Optional[app_commands.Choice[str]]) -> None:
        todo = read_todo(interaction.user.id)
        result: str = "todo list:\n"
        if len(todo) != 0:
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
            return "todo - here is no task"
        if iden.isdigit():
            id = int(iden)
            if list_len <= id or id < 0:
                return f"todo - there is no id {id}"

            todo[id][2] = status.name
            update_todo(user_id, json.dumps(todo))
            return f"todo - set id {id} to {status.name}"

        for i in range(list_len):
            if iden == todo[i][0]:
                todo[i][2] = status.name
                update_todo(user_id, json.dumps(todo))
                return f"todo - set name {iden} to {status.name}"
        return f"todo - not find name {iden}"

    @app_commands.command(name="set", description="set task status")
    @app_commands.describe(iden="task id / name")
    @app_commands.describe(status="status")
    @app_commands.choices(status=status)
    @app_commands.choices(lifetime=lifetime)
    async def set(self, interaction: Interaction, iden: str, status: Optional[app_commands.Choice[str]], lifetime: Optional[app_commands.Choice[str]]) -> None:
        if status is None and lifetime is None: 
            await interaction.response.send_message("todo - obviously you did nothing")
            return

        todo = read_todo(interaction.user.id)
        if status:
            self.set_status(interaction.user.id, todo, iden, status)

        if lifetime: # TODO: implement self.set_lifetime func
            await interaction.response.send_message(f"todo - set {iden} lifetime to {lifetime.name}")
        response = f"todo - set {iden} {"" if not status else status.name} {"" if not lifetime else lifetime.name}"
        await interaction.response.send_message(response)

    @app_commands.command(name="del", description="del a task")
    @app_commands.describe(iden="task id / name")
    async def delete(self, interaction: Interaction, iden: str) -> None:
        todo = read_todo(interaction.user.id)
        list_len = len(todo)
        if list_len == 0:
            await interaction.response.send_message("todo - here is no task")
            return
        if iden.isdigit():
            id = int(iden)
            if list_len <= id or id < 0:
                await interaction.response.send_message(f"todo - there is no id {id}")
                return
            todo.pop(id)
            update_todo(interaction.user.id, json.dumps(todo))
            await interaction.response.send_message(f"todo - delete task with id {id}")
            return

        for i in range(list_len):
            if iden == todo[i][0]:
                todo.pop(i)
                await interaction.response.send_message(f"todo - delete task with name {iden}")
                update_todo(interaction.user.id, json.dumps(todo))
                return
        await interaction.response.send_message(f"todo - not find name {iden}")

