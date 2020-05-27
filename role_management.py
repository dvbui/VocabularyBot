import discord
import pickle


role_info = {}


def get_max_score(list_of_users):
    result = 0
    for user in list_of_users:
        result = max(result, list_of_users[user]["score"])
    return result


async def give_role(guild, member, role):
    try:
        member = guild.get_member(member.id)
        await member.add_roles(role)
    except discord.Forbidden:
        print("Can't give role")
        print(member)
        print(role)


def add_role(db, server_id, setter_id, role_id, percentage, score):
    roles_ref = db.collection(u'roles').document(str(server_id))

    try:
        doc = roles_ref.get().to_dict()
    except:
        print("Cannot get role document")
        return

    if int(doc["admin_id"]) != setter_id:
        print("Not an admin")
        return

    content = {}
    if doc["content"] != "":
        content = pickle.loads(doc["content"])

    content[role_id] = {"percentage": percentage, "score": score}

    print("after add")
    print(content)

    try:
        roles_ref.set({"admin_id": doc["admin_id"], "content": pickle.dumps(content)})
    except:
        print("Cannot update role")
        return


def remove_role(db, server_id, setter_id, role_id):
    roles_ref = db.collection(u'roles').document(str(server_id))
    try:
        doc = roles_ref.get().to_dict()
    except:
        print("Cannot get role document")
        return

    if int(doc["admin_id"]) != setter_id:
        print("Not an admin")
        return

    content = {}
    if doc["content"] != "":
        content = pickle.loads(doc["content"])

    if role_id in content:
        del content[role_id]

    try:
        roles_ref.set({"admin_id": doc["admin_id"], "content": pickle.dumps(content)})
    except:
        print("Cannot update role")
        return


def init_roles(client, db):
    roles_ref = db.collection(u'roles')
    docs = roles_ref.stream()
    global role_info
    for doc in docs:
        guild = client.get_guild(int(doc.id))
        if not (guild is None):
            real_doc = doc.to_dict()
            if real_doc["content"] != "":
                role_info[guild] = pickle.loads(real_doc["content"])

    print(role_info)


async def update_roles(client, db, list_of_users):
    if role_info == {}:
        init_roles(client, db)

    max_score = get_max_score(list_of_users)
    for user in list_of_users:
        user_score = list_of_users[user]["score"]
        percentage = user_score / max_score * 100
        for guild in role_info:
            for role_id in role_info[guild]:
                condition1 = role_info[guild][role_id]["percentage"] <= percentage
                condition2 = role_info[guild][role_id]["score"] <= user_score
                if condition1 and condition2:
                    role = discord.utils.get(guild.roles, id=role_id)
                    await give_role(guild, user, role)



