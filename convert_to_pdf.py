from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_JUSTIFY
import re

# 注册中文字体
pdfmetrics.registerFont(TTFont('SimSun', 'C:\\Windows\\Fonts\\simsun.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('SimHei', 'C:\\Windows\\Fonts\\simhei.ttf'))

# 创建PDF文档
doc = SimpleDocTemplate(
    r"C:\Users\Eleanor's computer\Desktop\数字经济时代平台经济反垄断监管的困境与出路——基于监管政策效果评估的理论分析.pdf",
    pagesize=A4,
    rightMargin=2*cm,
    leftMargin=2*cm,
    topMargin=2*cm,
    bottomMargin=2*cm
)

# 创建样式
styles = getSampleStyleSheet()

# 标题样式
title_style = ParagraphStyle(
    'Title',
    parent=styles['Title'],
    fontName='SimHei',
    fontSize=18,
    spaceAfter=20,
    alignment=1  # 居中
)

# 副标题样式
subtitle_style = ParagraphStyle(
    'Subtitle',
    parent=styles['Title'],
    fontName='SimHei',
    fontSize=14,
    spaceAfter=20,
    alignment=1  # 居中
)

# 摘要样式
abstract_style = ParagraphStyle(
    'Abstract',
    parent=styles['Normal'],
    fontName='SimSun',
    fontSize=10,
    leading=16,
    spaceAfter=10,
    alignment=TA_JUSTIFY,
    leftIndent=1*cm,
    rightIndent=1*cm
)

# 正文样式
body_style = ParagraphStyle(
    'Body',
    parent=styles['Normal'],
    fontName='SimSun',
    fontSize=12,
    leading=20,
    spaceAfter=12,
    alignment=TA_JUSTIFY,
    firstLineIndent=2*cm  # 首行缩进
)

# 标题样式
heading1_style = ParagraphStyle(
    'Heading1',
    parent=styles['Heading1'],
    fontName='SimHei',
    fontSize=16,
    spaceAfter=15,
    spaceBefore=20,
    leading=24
)

heading2_style = ParagraphStyle(
    'Heading2',
    parent=styles['Heading2'],
    fontName='SimHei',
    fontSize=14,
    spaceAfter=10,
    spaceBefore=15,
    leading=20
)

heading3_style = ParagraphStyle(
    'Heading3',
    parent=styles['Heading3'],
    fontName='SimHei',
    fontSize=12,
    spaceAfter=8,
    spaceBefore=12,
    leading=18
)

# 关键词样式
keyword_style = ParagraphStyle(
    'Keyword',
    parent=styles['Normal'],
    fontName='SimSun',
    fontSize=10,
    spaceAfter=20,
    alignment=1
)

# 参考文献样式
ref_style = ParagraphStyle(
    'Reference',
    parent=styles['Normal'],
    fontName='SimSun',
    fontSize=10,
    leading=15,
    spaceAfter=6,
    leftIndent=0.5*cm,
    alignment=TA_JUSTIFY
)

# 读取markdown内容
with open(r"D:\wj\study\2025下学期各学科作业\平台经济论文\数字经济时代平台经济反垄断监管的困境与出路——基于监管政策效果评估的理论分析.md", "r", encoding="utf-8") as f:
    content = f.read()

# 解析markdown
story = []
lines = content.split('\n')
current_section = None
in_abstract = False
in_keywords = False

for line in lines:
    line = line.strip()

    # 空行
    if not line:
        if current_section == 'body':
            story.append(Spacer(1, 0.2*cm))
        continue

    # 处理标题
    if line.startswith('# '):
        title = line[2:].strip()
        story.append(Paragraph(title, title_style))
        current_section = 'title'
    elif line.startswith('## '):
        if current_section == 'abstract':
            in_abstract = False
        heading = line[3:].strip()
        story.append(Paragraph(heading, heading1_style))
        current_section = 'heading1'
    elif line.startswith('### '):
        heading = line[4:].strip()
        story.append(Paragraph(heading, heading2_style))
        current_section = 'heading2'
    elif line.startswith('#### '):
        heading = line[5:].strip()
        story.append(Paragraph(heading, heading3_style))
        current_section = 'heading3'

    # 处理摘要
    elif line.startswith('摘要：'):
        in_abstract = True
        abstract_text = line[3:].strip()
        story.append(Paragraph('<b>摘要：</b>' + abstract_text, abstract_style))
        current_section = 'abstract'
    elif in_abstract and line:
        # 继续摘要内容
        story.append(Paragraph(line, abstract_style))

    # 处理关键词
    elif line.startswith('关键词：'):
        in_keywords = True
        keywords_text = line[4:].strip()
        story.append(Paragraph('<b>关键词：</b>' + keywords_text, keyword_style))
        current_section = 'keywords'
        in_abstract = False

    # 处理参考文献
    elif line.startswith('参考文献'):
        story.append(Paragraph(line, heading1_style))
        current_section = 'references'
    elif current_section == 'references':
        if line.startswith('['):
            story.append(Paragraph(line, ref_style))
        elif line.strip():
            # 继续参考文献内容
            last_ref = story.pop()
            if hasattr(last_ref, 'text'):
                story.append(Paragraph(last_ref.text + ' ' + line, ref_style))
            else:
                story.append(Paragraph(line, ref_style))

    # 处理正文
    else:
        # 如果是正文段落
        if current_section in ['heading1', 'heading2', 'heading3', 'keywords', 'title']:
            current_section = 'body'

        if current_section == 'body' and line:
            # 转义特殊字符
            escaped_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

            # 处理引号
            escaped_line = escaped_line.replace('"', '&quot;')

            # 处理数字引用
            escaped_line = re.sub(r'(\d+)\.(\d+)', r'\1<super>.\2</super>', escaped_line)

            story.append(Paragraph(escaped_line, body_style))
            story.append(Spacer(1, 0.3*cm))

# 构建PDF
doc.build(story)
print("PDF生成成功！")