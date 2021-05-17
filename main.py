import redis
import PySimpleGUI as sg

def layout():
    pass

def main():
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

if __name__ == '__main__':
    main()