import os
import io
import glob
import base64
import argparse
import datetime
from PIL import Image, ImageDraw, ImageFont

# 主函数入口
if __name__ == '__main__':
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='Convert a pile of still into PDF.')
    # 添加-i参数，用于指定输入文件的路径
    parser.add_argument('-i', '--input', required=True, help='Specify a Still input directory.')
    # 添加-o参数，用于指定输出目录的路径
    parser.add_argument('-o', '--output', required=True, help='Specify a Still output directory.')
    parser.add_argument('-p', '--project_name', required=True, help='Specify a project name.')
    parser.add_argument('-d', '--shooting_date', required=True, help='Designate a shooting day.')
    parser.add_argument('-l', '--logo', required=True, help='Logo_base64.')
    args = parser.parse_args()


# 解析命令行参数
folder_path = args.input
project_name = args.project_name
shooting_date = args.shooting_date
now = datetime.datetime.now()
Generation_time = now.strftime("%Y/%m/%d %H:%M:%S")
Generation_timefile = now.strftime("%Y-%m-%d_%H-%M-%S")
font_path = "/System/Library/Fonts/HelveticaNeue.ttc"  # HelveticaNeue 字体路径
titelfont_path = "/System/Library/Fonts/PingFang.ttc"  # PingFang 字体路径
output_directory = args.output
output_filename = f"{project_name}_{shooting_date}.pdf"

# 函数定义：分割文件名
def split_filename(filename):
    # 分割文件名以获取不同的部分
    filename = os.path.splitext(filename)[0]
    parts = filename.split('-')
    file_name_part = parts[0]
    look_name_part = parts[1]
    return file_name_part, look_name_part


# 函数定义：调整图像大小并添加文本和LOGO
def resize_images_with_text_and_logo(folder_path, project_name, shooting_date, Generation_time, width=1920, padding=100, font_path="/System/Library/Fonts/HelveticaNeue.ttc", titelfont_path = "/System/Library/Fonts/PingFang.ttc", logo_base64=None):
    # 定义支持的图像格式
    formats = ["*.jpeg", "*.jpg", "*.png", "*.tif", "*.tiff", "*.heic"]
    # 获取所有匹配格式的图像
    images = sorted([img for format in formats for img in glob.glob(os.path.join(folder_path, format))])

    print(f"Found {len(images)} images")

    resized_images = []
    # 设置文本字体
    Text = ImageFont.truetype(font_path, 28, index=1)
    Titel = ImageFont.truetype(titelfont_path, 56, index=6)  # 使用 titelfont_path
    Subtitel = ImageFont.truetype(font_path, 28, index=0)
    Description = ImageFont.truetype(font_path, 20, index=7)
    # 处理徽标
    if logo_base64:
        logo_bytes = base64.b64decode(logo_base64)
        logo = Image.open(io.BytesIO(logo_bytes))  # Load Logo
    # 遍历并处理每张图像
    for i, img_path in enumerate(images):
        with Image.open(img_path) as img:
            ratio = width / img.width
            new_height = int(img.height * ratio)
            new_img_height = new_height + 4 * padding if i == 0 else new_height + padding
            resized_img = img.resize((width, new_height), Image.Resampling.LANCZOS)

            background = Image.new("RGB", (width, new_img_height), "white")
            upper_left_corner = (0, 3 * padding) if i == 0 else (0, 0)
            background.paste(resized_img, upper_left_corner)

            draw = ImageDraw.Draw(background)
            # 添加项目名称、拍摄日期等信息
            if i == 0:
                draw.text((padding, padding), project_name, fill="black", font=Titel)
                draw.text((padding, padding + 70), shooting_date, fill="black", font=Subtitel)
                draw.text((padding, padding + 110), Generation_time, fill="black", font=Description)
                logo_position = (width - logo.size[0] - padding // 2, padding // 2)
                background.paste(logo, logo_position, logo)

            file_name_part, look_name_part = split_filename(os.path.splitext(os.path.basename(img_path))[0])
            draw.text((padding, new_img_height - padding + 30), file_name_part, fill="black", font=Text)
            draw.text((width - padding - 150, new_img_height - padding + 30), look_name_part, fill="black", font=Text)

            resized_images.append(background)

    return resized_images

def create_pdf(images, output_path):
    if not images:
        print("No images found for creating PDF")
        return

    cover = images[0]
    cover.save(output_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:])


# Base64 encoded logo
logo_base64 = args.shooting_date


# 处理图片并创建 PDF
resized_images = resize_images_with_text_and_logo(folder_path, project_name, shooting_date, Generation_time, font_path=font_path, titelfont_path=titelfont_path, logo_base64=logo_base64)
# 合并目录和文件名以形成完整的输出路径
complete_output_path = os.path.join(output_directory, output_filename)
create_pdf(resized_images, complete_output_path)
