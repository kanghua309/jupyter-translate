import os
import subprocess
import time
import fire

def translate_notebook(source_file, language, max_retries=3):
    retries = 0
    while retries < max_retries:
        result = subprocess.run(['python', 'jupyter_translate.py', source_file, '--language', language])
        if result.returncode == 0:  # 成功执行
            break
        else:  # 翻译失败
            time.sleep(5)  # 等待 5 秒
            retries += 1

def translate_notebook_directory(source_dir, language='zh-cn'):
    for root, dirs, files in os.walk(source_dir):
        print("root:",root)
        if '.ipynb_checkpoints' in root:
            continue

        for file in files:
            if file.endswith('.ipynb'):
                source_file = os.path.join(root, file)
                translate_notebook(source_file, language)

def main(source_directory='source_notebooks', language='zh-cn'):
    translate_notebook_directory(source_directory, language)

if __name__ == '__main__':
    fire.Fire(main)
