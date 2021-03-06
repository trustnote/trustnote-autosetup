import os
import json
import platform
import sqlite3
import subprocess
import time

class Tools:
    """common tool functions."""

    def __init__(self):
        return

    @staticmethod
    def run_shell_command(command):
        Tools.log("command: {0}".format(command))
        os.system(command)
    
    @staticmethod
    def run_shell_command_with_output(command):
        Tools.log("command: {0}".format(command))
        process = os.popen(command)
        output = process.read()
        process.close()
        return output

    @staticmethod
    def run_shell_cd(path):
        Tools.log("command: cd {0}".format(path))
        os.chdir(path)

    @staticmethod
    def log(message):
        Tools.append_file("main_chain_setter.log", "[{0}]{1}\n".format(time.strftime("%Y-%m-%d %H:%M:%S"), message))
        print(message)

    @staticmethod
    def read_file(path):
        text = ""
        with open(path) as content:
             text = content

        return text

    @staticmethod
    def read_file_to_json(path):
        text = []
        with open(path) as content:
             text = json.load(content)

        return text

    @staticmethod
    def read_file_to_lines(path):
        lines = []
        with open(path, 'r', encoding='UTF-8') as f:
            lines = f.readlines()
        return lines

    @staticmethod
    def file_lines_replacer(path, modify_dictionary):
        lines = Tools.read_file_to_lines(path)

        for index in range(len(lines)):
            for key in modify_dictionary.keys():
                if key in lines[index]:
                    lines[index] = lines[index].replace(key, modify_dictionary[key])
                    Tools.log("Changed value from:{0} to :{1}".format(key, modify_dictionary[key]))

        Tools.write_file_in_lines(path, lines)
        return

    @staticmethod
    def write_file_in_lines(path, lines):
        with open(path, 'w', encoding='UTF-8') as f:
            f.writelines(lines)
    
    @staticmethod
    def append_file(path, content):
        with open(path, 'a+', encoding='UTF-8') as f:
            f.write(content)

    @staticmethod
    def execute_sqlite_sql(path, sql):
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        conn.close()
        return data
    
    @staticmethod
    def current_paltform():
        platform_value = platform.platform()
        if ( "Windows" in platform_value ):
            return "Windows"
        elif ( "Linux" in platform_value ):
            return "Linux"
        else:
            return "Unkown"

    @staticmethod
    def cross_platfrom_path(path):
        platform_value = Tools.current_paltform()
        if ( platform_value != "Windows" ):
            return path.replace("\\", "/")
        
        return path.replace("/", "\\")