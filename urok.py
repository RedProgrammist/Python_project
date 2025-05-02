import mysql.connector
import re


class Request:
    def __init__(self, name, func):
        self.name = name
        self.func = func


def desc_req(*args):
    return f'Select title, description from film where description Like "%{args[0]}%"'


def ganre_req(*args):
    anf_str = f'Select film.title, category.name from film_category Left join category on film_category.category_id = category.category_id Left join film on film_category.film_id = film.film_id Where category.name Like "%{args[0]}%"'
    if len(args) == 1:
        return anf_str
    if len(args) == 2:
        return f'{anf_str} and release_year = {args[1]}'
    return f'{anf_str} and release_year between {args[1]} and {args[2]}'


def cnt_req(cursor, req_type, inp):
    cop_type = req_type
    if cop_type == "genre and year" and len(inp) == 1:
        cop_type = "genre"
    anf_str = f'Update requests set cnt_req = cnt_req + 1 where req_type = "{cop_type}" and arg1 = "{inp[0]}"'
    if len(inp) >= 2:
        anf_str += f' and arg2 = {inp[1]}'
    if len(inp) >= 3:
        if cop_type == "genre and year":
            cop_type = "genre and between year"
            anf_str = f'Update requests set cnt_req = cnt_req + 1 where req_type = "{cop_type}" and arg1 = "{inp[0]}"'
        anf_str += f' and arg3 = {inp[2]}'
    cursor.execute(anf_str)

    if cursor.rowcount == 0:
        cursor.fetchall()
        anf_str = f'Insert into requests (req_type, arg1, arg2, arg3, cnt_req, req_date) values ("{cop_type}", "{inp[0]}"'
        if len(inp) >= 2 and req_type == "genre and year":
            anf_str += f', {inp[1]}'
        else:
            anf_str += f', NULL'
        if len(inp) >= 3 and req_type == "genre and year":
            anf_str += f', {inp[2]}'
        else:
            anf_str += f', NULL'
        anf_str += f', 1, CURDATE())'
        cursor.execute(anf_str)
        cursor.fetchall()


def is_int(a):
    res = True
    try:
        int(a)
        res = True
    except Exception as e:
        res = False
    return res


programm_work = True

try:
    conn = mysql.connector.connect(
        host="ich-db.edu.itcareerhub.de",
        user="ich1",
        password="password",
        database="sakila"
    )

    conn_save = mysql.connector.connect(
        host="ich-edit.edu.itcareerhub.de",
        user="ich1",
        password="ich1_password_ilovedbs"
    )

    conn_save.cursor().execute("CREATE DATABASE IF NOT EXISTS Oleksandr_Kiselov_poject")

    conn_save = conn_save = mysql.connector.connect(
        host="ich-edit.edu.itcareerhub.de",
        user="ich1",
        password="ich1_password_ilovedbs",
        database="Oleksandr_Kiselov_poject"
    )
    cursor = conn.cursor()
    cursor_save = conn_save.cursor()
except Exception as e:
    programm_work = False
    print("There was an error connecting to the server. For assistance, you can contact our support team at 12345678")

reqs = [Request("description", desc_req), Request("genre and year", ganre_req)]

const_lim = False
lim = 10
inst_const_lim = True

while programm_work:
    req_num = None

    norm_antw = False
    while not norm_antw:
        req_num = input(
            "what request you?\n 1/description - request by description\n 2/genre/genre and year - request by genre und year\n 3/request statistics - list of the most popular queries that were searched\n")
        if req_num == "1" or req_num == "description":
            norm_antw = True
            req_num = 1
            print("please, enter: description")
        elif req_num == "2" or req_num == "genre" or req_num == "genre and year":
            norm_antw = True
            req_num = 2
            print("please, enter: genre/genre, year/genre, year1, year2")
        elif req_num == "3" or req_num == "request statistics":
            norm_antw = True
            req_num = 3
        else:
            print("please, clarify your request")

    if req_num <= 2:
        inp = re.split(r'[,\s]+', input("\n"))

    if not const_lim:
        quest = input(
            f"""Do you want a {lim} line query length limit?\n If yes, enter "yes" or anything,\n If you want to change the limit, enter any positive number,\n If you don't want a limit, enter a negative number\n""")

        if quest.lstrip('-+').isdigit():
            lim = int(quest)

        if inst_const_lim:
            inst_const_lim = False
            quest = input(
                """If you want to keep the limit for all subsequent requests, enter "yes". Attention! Your choice can only be changed by turning off the program!\n""")
            if quest.lower() == "yes":
                const_lim = True
    fetch = []
    if req_num <= 2:
        if lim >= 0:

            cursor.execute(f"{reqs[int(req_num) - 1].func(*inp)} Limit {lim}")
        else:
            cursor.execute(reqs[int(req_num) - 1].func(*inp))

        fetch = cursor.fetchall()
        cursor_save.execute(
            "CREATE TABLE IF NOT EXISTS requests (request_id INT AUTO_INCREMENT PRIMARY KEY,req_type VARCHAR(35) NOT NULL,arg1 VARCHAR(100),arg2 INT,arg3 INT,cnt_req INT,req_date date);")
        cnt_req(cursor_save, reqs[int(req_num) - 1].name, inp)

    else:
        if lim >= 0:
            cursor_save.execute(f"select * from requests Limit {lim}")
        else:
            cursor_save.execute("select * from requests")
        fetch = cursor_save.fetchall()

    for i in fetch:
        print(i)

    is_of = input("of programm\n")
    if is_of.lower() == "yes":
        programm_work = False

try:
    conn.close()
    cursor.close()
    conn_save.close()
    cursor_save.close()
except Exception as e:
    print("no close")
