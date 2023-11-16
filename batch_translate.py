import os
import subprocess
import fire

def translate_notebook_directory(source_dir, dest_dir, language='zh-cn'):
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.ipynb'):
                source_file = os.path.join(root, file)
                # 构建目标文件路径
                relative_path = os.path.relpath(root, source_dir)
                dest_file_root = os.path.join(dest_dir, relative_path)
                if not os.path.exists(dest_file_root):
                    os.makedirs(dest_file_root)
                dest_file = os.path.join(dest_file_root, file)

                # 调用 jupyter_translate.py
                subprocess.run(['python', 'jupyter_translate.py', source_file, '--language', language, '--dest_file', dest_file])

def main(source_directory='source_notebooks', destination_directory='translated_notebooks', language='zh-cn'):
    translate_notebook_directory(source_directory, destination_directory, language)

if __name__ == '__main__':
    fire.Fire(main)
