import json, fire, os, re
from googletrans import Translator
import re

def is_contain_chinese(check_str):
    """
    判断传入的字符串中是否含有中文
    :param check_str: 需要检查的字符串
    :return: True - 包含中文；False - 不包含中文
    """
    zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
    # [\u4e00-\u9fa5]是Unicode3.0至Unicode8.0之间汉字的编码范围
    match = zh_pattern.search(check_str)
    if match:
        return True
    else:
        return False

def translate_text(text, dest_language='pt'):
    translator = Translator()
    return translator.translate(text, dest=dest_language).text

def translate_markdown(text, dest_language='pt'):
    # Regex expressions
    #MD_CODE_REGEX='```[a-z]*\n[\s\S]*?\n```'
    MD_CODE_REGEX = r'```[a-z]*\n[\s\S]*?\n```'
 
    CODE_REPLACEMENT_KW = 'xx_markdown_code_xx'

    #MD_LINK_REGEX="\[[^)]+\)"
    MD_LINK_REGEX = r"\[[^)]+\)"

    LINK_REPLACEMENT_KW = 'xx_markdown_link_xx'

    # Markdown tags
    END_LINE='\n'
    IMG_PREFIX='!['
    HEADERS=['### ', '###', '## ', '##', '# ', '#'] # Should be from this order (bigger to smaller)

     # Inner function to replace tags from text from a source list
    def replace_from_list(tag, text, replacement_list):
        list_to_gen = lambda: [(x) for x in replacement_list]
        replacement_gen = list_to_gen()
        return re.sub(tag, lambda x: next(iter(replacement_gen)), text)

    # Create an instance of Tranlator
    translator = Translator()

    # Inner function for translation
    def translate(text):
        # Get all markdown links
        md_links = re.findall(MD_LINK_REGEX, text)

        # Get all markdown code blocks
        md_codes = re.findall(MD_CODE_REGEX, text)

        # Replace markdown links in text to markdown_link
        text = re.sub(MD_LINK_REGEX, LINK_REPLACEMENT_KW, text)

        # Replace links in markdown to tag markdown_link
        text = re.sub(MD_CODE_REGEX, CODE_REPLACEMENT_KW, text)

        # Translate text
        text = translator.translate(text, dest=dest_language).text

        # Replace tags to original link tags
        text = replace_from_list('[Xx]'+LINK_REPLACEMENT_KW[1:], text, md_links)

        # Replace code tags
        text = replace_from_list('[Xx]'+CODE_REPLACEMENT_KW[1:], text, md_codes)

        return text

    # Check if there are special Markdown tags    
    if len(text)>=2:
        for header in HEADERS:
            len_header=len(header)
            if text[:len_header]==header:
                if text[-1:]==END_LINE: 
                    return header + translate(text[len_header:]) + '\n'
                else:
                    return header + translate(text[len_header:])  
                
        if text[-1:]==END_LINE: 
            return translate(text)+'\n'

        if text[:2]==IMG_PREFIX:
            return text

        # for header in HEADERS:
        #     print("header:",header)
        #     len_header=len(header)
        #     print("len_header:",len_header)
        #     print("text:",text,text[:len_header])
        #     if text[:len_header]==header:
        #         print("-------------------------------------------------??????")
        #         return header + translate(text[len_header:])

    return translate(text)

#export
def jupyter_translate(fname, language='pt', rename_source_file=False, translate_filename=True, print_translation=False):
    """
    TODO:
    add dest_path: Destination folder in order to save the translated files.
    """
    print("fname ---------", fname)
    # 翻译文件名
    if translate_filename:
        base_name, extension = os.path.splitext(fname)
        directory_path = os.path.dirname(base_name)
        file_name = os.path.basename(base_name)
        translate_file_name = translate_text(file_name, dest_language=language)
        if is_contain_chinese(file_name):
            print(f"Filename {file_name} contains Chinese characters....")
            return 
        if translate_file_name == file_name:
            print(f"Filename {file_name} not translated. Why ...")
            dest_fname = f"{'.'.join(fname.split('.')[:-1])}_{language}.ipynb"
        else:
            translated_base_name = os.path.join(directory_path, translate_file_name)
            dest_fname = f"{translated_base_name}{extension}"
    else:
        dest_fname = f"{'.'.join(fname.split('.')[:-1])}_{language}.ipynb"

    if os.path.exists(dest_fname):
        print(f'{dest_fname} already exists. Skipping...')
        return

    data_translated = json.load(open(fname, 'r'))
    skip_row=False
    for i, cell in enumerate(data_translated['cells']):
      if cell['cell_type'] == 'markdown':
        new_source = []  # 创建一个新的字符串列表
        skip_row = False
        for source in cell['source']:
            if source[:3] == '```':
                skip_row = not skip_row  # Invert flag until I find next code block

            if not skip_row:
                if source not in ['```\n', '```', '\n'] and source[:4] != '<img':
                    # 翻译并添加到新列表
                    translated = translate_markdown(source, dest_language=language)
                    new_source.append(translated)
                    if print_translation:
                        print(translated)
                else:
                    # 不需要翻译的部分直接添加到新列表
                    new_source.append(source)
            else:
                new_source.append(source)
        # 更新 cell['source'] 为新的字符串列表
        cell['source'] = new_source

    # # 翻译文件名
    # if translate_filename:
    #     base_name, extension = os.path.splitext(fname)
    #     directory_path = os.path.dirname(base_name)
    #     file_name = os.path.basename(base_name)
    #     translated_base_name = os.path.join(directory_path, translate_text(file_name, dest_language=language))
    #     dest_fname = f"{translated_base_name}{extension}"
    #     #print("____:",base_name,file_name,translated_base_name,dest_fname)
    # else:
    #     dest_fname = f"{'.'.join(fname.split('.')[:-1])}_{language}.ipynb"
    
    
   # 保存翻译后的文件
    if rename_source_file:
        fname_bk = f"{'.'.join(fname.split('.')[:-1])}_bk.ipynb"
        os.rename(fname, fname_bk)
        print(f'{fname} has been renamed as {fname_bk}')

    # # 使用 dest_file 作为输出文件路径
    # if dest_file is None:
    #     dest_file = f"{'.'.join(fname.split('.')[:-1])}_{language}.ipynb"

    # # 确保目标文件夹存在
    # os.makedirs(os.path.dirname(dest_file), exist_ok=True)


    with open(dest_fname, 'w') as f:
        json.dump(data_translated, f, ensure_ascii=False, indent=4)
    print(f'The {language} translation has been saved as {dest_fname}')

def markdown_translator(input_fpath, output_fpath, input_name_suffix=''):
    with open(input_fpath,'r') as f:
        content = f.readlines()
    content = ''.join(content)
    content_translated = translate_markdown(content)
    if input_name_suffix!='':
        new_input_name=f"{'.'.join(input_fpath.split('.')[:-1])}{input_name_suffix}.md"
        os.rename(input_fpath, new_input_name)
    with open(output_fpath, 'w') as f:
        f.write(content_translated)


if __name__ == '__main__':
    fire.Fire(jupyter_translate)
