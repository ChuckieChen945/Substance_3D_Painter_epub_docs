'''
将爬取的手册转制成epub
'''
import shutil
import os
import json
from pyquery import PyQuery as pq

ORDER = 1

def generate_manifest(manifest,folder_tag):
    
    for root, _, files in os.walk(f'./epub_output/{folder_tag}'):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if os.path.isfile(file_path):
                # 根据文件扩展名定义媒体类型
                if file_name.endswith('.html') or file_name.endswith('.xhtml'):
                    media_type = 'application/xhtml+xml'
                elif file_name.endswith('.css'):
                    media_type = 'text/css'
                elif file_name.endswith('.jpg') or file_name.endswith('.jpeg'):
                    media_type = 'image/jpeg'
                elif file_name.endswith('.png'):
                    media_type = 'image/png'
                elif file_name.endswith('.svg'):
                    media_type = 'image/svg+xml'
                elif file_name.endswith('.js'):
                    media_type = 'application/javascript'
                elif file_name.endswith('.bmp'):
                    media_type = 'image/bmp'
                elif file_name.endswith('.gif'):
                    media_type = 'image/gif'
                else:
                    # 忽略其他文件类型，或根据需要添加其他类型
                    continue

                file_path = os.path.relpath(file_path,'./epub_output').replace('\\','/')

                # item ID 使用文件名去掉扩展名，href 为文件相对路径
                item_id = file_path
                item =pq( f'<item id="{item_id}" href="{file_path}" media-type="{media_type}"/>\n')
                manifest.append(item)

def di_gui_nav_map(insert_point,prefix,chapter):
    global ORDER
    id = chapter.get('id')

    children = None
    src = chapter.get('ln')
    while src == '' or src is None:
        # 第一次，初始化
        if children is None:
            children = chapter.get('children')[0]
        # 第二次及以上查询
        else:
            children = children.get('children')[0]
        src = children.get('ln')

    # src = src[src.rfind('/')+1:]
    if src.endswith('.htm'):
        src=src+'l'
    # fix_head(src,prefix)
    nav_label = prefix + ' ' + chapter.get('ttl')
    child= append_nav_point(insert_point, id,nav_label,src,ORDER)
    ORDER = ORDER + 1
    if chapter.get('children'):
        for index,child_chapter in enumerate(chapter.get('children')):
            di_gui_nav_map(child,prefix + '.' +str(index+1),child_chapter)

def fix_head(src,prefix):
    """
    给页面标题加上前缀
    """
    if len(src)==0:
        return
    if src == 'index.html':
        return
        
    with open(f'./epub_output/html/{src}', 'r', encoding = 'utf-8') as file:
        html = file.read()
    content = pq(html)
    title = content.find('div.head-text > h1') or content.find('div.head-block > h1')
    title.text(prefix+ ' '+ title.text())
    with open(f'./epub_output/html/{src}', 'w', encoding = 'utf-8') as file:
        file.write(content.outer_html())


def append_nav_point(insert_point, id,nav_label,src,play_order):
    """
    递归插入目录节点
    返回被插入的节点的指针
    """

    if src !='' and src is not None:
        nav_point_template = f"""    <navPoint id="{id}" playOrder="{play_order}">
            <navLabel>
                <text>{nav_label}</text>
            </navLabel>
            <content src="html{src}">
            </navPoint>
        """
    else:
        raise
    nav_point = pq( nav_point_template)
    insert_point.append(nav_point)

    return nav_point


def copy_folder(src_folder, dest_folder):
    """
    复制整个文件夹
    """
    # 检查源文件夹是否存在
    if not os.path.exists(src_folder):
        print(f"源文件夹 '{src_folder}' 不存在")
        return

    # 如果目标文件夹不存在，则创建它
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    folder_name = os.path.basename(src_folder)
    dest_path = os.path.join(dest_folder, folder_name)

    shutil.copytree(src_folder, dest_path)

    print(f"已成功将 '{src_folder}' 复制到 '{dest_folder}'")

def copy_folder_contents(src_folder, dest_folder):
    """
    只复制文件夹中的内容
    """
    # 检查源文件夹是否存在
    if not os.path.exists(src_folder):
        print(f"源文件夹 '{src_folder}' 不存在")
        return

    # 如果目标文件夹不存在，则创建它
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    # 遍历源文件夹中的所有文件和文件夹
    for item in os.listdir(src_folder):
        src_path = os.path.join(src_folder, item)
        dest_path = os.path.join(dest_folder, item)

        # 如果是文件夹，使用 copytree 递归复制
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dest_path)
        # 如果是文件，使用 copy2 保留文件元数据
        else:
            shutil.copy2(src_path, dest_path)

    print(f"已成功将 '{src_folder}' 的内容复制到 '{dest_folder}'")

def di_gui_spine(spine, chapter):
    id = chapter.get('id')
    itemref = pq(f'<itemref idref="html{id}"/>')
    if chapter.get('ln')!='' and chapter.get('ln') is not None:
        spine.append(itemref)
    if chapter.get('children'):
        for child in chapter.get('children'):
            di_gui_spine(spine,child)

copy_folder_contents('./epub_template', './epub_output')
# copy_folder('./html', './epub_output')
# copy_folder('./images', './epub_output')
# copy_folder('./scripts', './epub_output')
# copy_folder('./style', './epub_output')

with open('./toc.json', 'r', encoding='utf-8') as file:
    toc_json = json.load(file)

# toc.ncx > nav_map
nav_map = pq('<navMap></navMap>')
for index,chapter in enumerate(toc_json.get('books')):
    di_gui_nav_map(nav_map,str(index+1),chapter)

# toc.ncx
with open('./epub_output/toc.ncx', 'r', encoding = 'utf-8') as file:
    string = file.read()
string = string.replace('<navMap><!-- navMap insert point --></navMap>',nav_map.outer_html())
with open('./epub_output/toc.ncx', 'w', encoding = 'utf-8') as file:
    file.write(string)

# content.opf > spine
spine = pq('<spine toc="ncx"></spine>')
for chapter in toc_json.get('books'):
    di_gui_spine(spine, chapter)

# content.opf > manifest
manifest= pq('<manifest></manifest>')
generate_manifest(manifest,'html')
generate_manifest(manifest,'images')
generate_manifest(manifest,'scripts')
generate_manifest(manifest,'style')

# content.opf
with open('./epub_output/content.opf', 'r', encoding = 'utf-8') as file:
    string = file.read()
string = string.replace('<spine toc="ncx"><!-- spine insert point --></spine>',spine.outer_html())
string = string.replace('<!-- manifest insert point -->',manifest.html())
with open('./epub_output/content.opf', 'w', encoding = 'utf-8') as file:
    file.write(string)



