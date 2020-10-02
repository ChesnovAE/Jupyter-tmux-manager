import libtmux
import time
import subprocess
import os
import tqdm
import argparse


parser = argparse.ArgumentParser(description='Tmux argparser')
# parser.add_argument('--start', type=int)
# parser.add_argument('--stop', type=bool)
# parser.add_argument('--stop-all', type=bool)
parser.add_argument('--action', type=str, help='start, stop or stop_all')
parser.add_argument('--session-name', default='test_session', type=str, help='Default session name is test_session')
parser.add_argument('--window-num', type=str)
parser.add_argument('--num-users', type=int)
parser.add_argument('--base-dir', default='./', type=str)


def start(num_users, tmux_session, base_dir='./'):
    """
    Запустить $num_users ноутбуков. У каждого рабочай директория $base_dir+$folder_num
    """
    for folder_num in tqdm.tqdm(range(num_users)):
        dir_path = os.path.join(base_dir, str(folder_num))
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        
        user_window = tmux_session.new_window(window_name=str(folder_num))
        pane = user_window.list_panes()[0]

        jupyter_start_command = "jupyter notebook --ip {} --no-browser --NotebookApp.notebook_dir='{}'"\
                                .format('0.0.0.0', dir_path)
        pane.send_keys(jupyter_start_command)
    tmux_session.kill_window('0')

def stop(session_name, num):
    """
    @:param session_name: Названия tmux-сессии, в которой запущены окружения
    @:param num: номер окружения, кот. можно убить
    """
    #  убивает сессию по айдишнику, так как в man tmux сказано, что сначала он пытается удалить по айдишнику
    #  чтобы убивать сессию по номеру, можно добавить сдвиг на +1, так как сначала создается нулевая сессия
    #  либо давать сессия в имена не номера, а что-то другое и подавать сюда не номер сессии, а имя сессии
    server = libtmux.Server()
    server.find_where({ "session_name": session_name}).kill_window(num + 1)


def stop_all(session_name):
    """
    @:param session_name: Названия tmux-сессии, в которой запущены окружения
    """
    server = libtmux.Server()
    server.find_where({ "session_name": session_name}).kill_session()


if __name__ == '__main__':
    args = parser.parse_args()

    if args.action.lower() == 'start':
        session_subprocess = subprocess.Popen(['tmux', 'new-session', '-d', '-s', '{}'.format(args.session_name)])
        time.sleep(1)  #  нужно, чтобы не вылетала ошибка, что сессии нет, так как код выполняется быстрее, чем создается сессия
        server = libtmux.Server()
        start(args.num_users, server.find_where({ "session_name": args.session_name}), args.base_dir)
    elif args.action.lower() == 'stop':
        stop(args.session_name, args.window_num)
    elif args.action.lower() == 'stop_all':
        stop_all(args.session_name)
