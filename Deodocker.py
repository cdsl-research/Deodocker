#!/usr/bin/python3
import subprocess
import os

#lines = [line for line in dockerfile.split('\n')]
def make_new_Dockerfile(lines):
    run_lines = []
    new_Dockerfile = []
    for line_count in range(len(lines)):
        if 'ADD' in lines[line_count]:
            # ADDコマンドからADDコマンドのfileの削除処理が発生するまでのRUNコマンドを取得する．
            for ADD_line_count in range(line_count,len(lines)):
                if lines[ADD_line_count].startswith('RUN '):
                    run_lines.append(lines[ADD_line_count])
                    if "RUN rm" in lines[ADD_line_count]:
                        lines[ADD_line_count] = "None"
                        break
                    lines[ADD_line_count] = "None"
            #ADDコマンドの行を取得
            add_command = lines[line_count].split(' ')[1]
            #ADDコマンドの行を単語リストに分解
            add_words = add_command.replace('https://', '').replace('http://', '').split('/')
            #RUNコマンドを編集
            run_commands = ' && '.join([line.replace('RUN ', '') for line in run_lines])
            #新しいRUNコマンドの作成
            new_run_command = f"RUN curl -o {add_words[-1]} {add_command} && {run_commands}"
            new_run_command = new_run_command.replace('\n', '')
            new_Dockerfile.append(new_run_command)
        else:
            if lines[line_count] != "None":
                new_Dockerfile.append(lines[line_count].replace('\n', ''))
    print(new_Dockerfile)
    return new_Dockerfile

def replace_add_command(lines):
    flag = False
    # ADDコマンドを検出
    for line_count in range(len(lines)):
        if lines[line_count].startswith('ADD'):
            # tarファイルの解凍はADDで行う
            if '.tar' in lines[line_count]:
                continue
            #ADDコマンドの行を取得
            add_command = lines[line_count].split(' ')[1]
            #ADDコマンドの行を単語リストに分解
            add_words = add_command.replace('https://', '').replace('http://', '').split('/')
            print(add_words)
            for ADD_line_count in range(line_count,len(lines)):
                if ("RUN rm" in lines[ADD_line_count]) and (add_words[-1] in lines[ADD_line_count]):
                    flag = True
    if flag:
        print("start_chage")
        new_Dockerfile = make_new_Dockerfile(lines)
        return new_Dockerfile
    else:
        return "False"

def main():
    build_flag = False
    dockerdict_path = os.getcwd()
    dockerfile_path = dockerdict_path +  "/Dockerfile"
    new_dockerfile_path =  dockerdict_path +   "/new_Dockerfile"

    print(new_dockerfile_path)
    
    # Dockerfileが存在するディレクトリを取得する。
    dockerfile_dir = os.path.dirname(dockerfile_path)
    #Dockerfileの中身を取得する．
    with open(dockerfile_path, 'r') as file:
        lines = file.readlines()
    
    #判断関数へ移行
    #new_lines = [replace_add_command(line) for line in lines]
    new_Dockerfile =  replace_add_command(lines)
    print(new_Dockerfile)
    if new_Dockerfile != "False":
        build_flag = True
        with open(new_dockerfile_path, 'w') as f:
            for new_Dockerfile_line in new_Dockerfile:
                f.write("%s\n" % new_Dockerfile_line)
    # Docker buildコマンドを実行する。
    dockerfile_dir = os.getcwd()
    if build_flag:
        command_build = f"docker build -f new_Dockerfile -t after-image {dockerfile_dir}"
        print("提案実行時プロセス")
    else:
        command_build = f"docker build -f Dockerfile -t before-image {dockerfile_dir}"
        print("提案実行前プロセス")
    
    # コマンドを実行します。
    subprocess.run(command_build, shell=True)
    print("Successfully created NewDockerfile.")

if __name__ == "__main__":
    main()
