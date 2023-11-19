import os
import json

class db:
    path = 'db.txt'
    def get():
        if os.path.exists(db.path):
            with open(db.path, "r") as file:
                data = eval(file.read())
        else:
            with open(db.path, "w") as file:
                file.write("{}")
                print('db.txt를 생성했습니다.')
                data = '{}'
        return data

    def exist_user(user_id):
        data = db.get()
        try:
            data[user_id]
            return True
        except:
            return False

    def register(user_id, name):
        if db.exist_user(user_id):
            return False
        else:
            data = db.get()
            data[user_id] = {'point' : 0}
            data[user_id]['name'] = name
            db.update(data)
            return True

    def update(data):
        with open(db.path, "w") as file:
            file.write(json.dumps(data, ensure_ascii=False))

    def user_info(user_id):
        rank = db.point.user_rank(user_id)
        data = db.get()
        point = data[user_id]['point']
        return f'귀하는 {point}포인트를 보유하고 있으며, 이는 \'서버 {rank}위\'입니다!'

    def check_name(user_id, nick):
        data = db.get()
        if data[user_id]['name'] != nick:
            data[user_id]['name'] = nick
            db.update(data)

    def get_name(user_id):
        data = db.get()
        return data[user_id]['name']

    class point:
        def plus(user_id, value):
            data = db.get()
            data[user_id]['point'] += value
            db.update(data)

        def user_rank(user_id):
            rank = db.point.rank()
            for i in range(0, len(rank)):
                if rank[i] == user_id:
                    break
            return i + 1
        
        def rank():
            data = db.get()
            sorted_data = dict(sorted(data.items(), key=lambda x: x[1]['point']))
            rank = []
            for s in sorted_data:
                rank.append(s)
            rank.reverse()
            return rank

        def rank_table():
            rank = db.point.rank()
            data = db.get()
            rank_table = ''
            for i in range(0, len(rank)):
                name = data[rank[i]]['name']
                point = data[rank[i]]['point']
                rank_table += f'{i + 1}위: {name} / {point}포인트\n'
            return f'```{rank_table}```'

        def check(user_id):
            data = db.get()
            return data[user_id]['point']