#!/usr/bin/env python3
from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/simplify', methods=['GET'])
def simplify():
    # 获取请求参数中的 URL
    url = request.args.get('url')
    if not url:
        return "URL is required", 400
    
    try:
        # 请求目标 URL 获取网页内容
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        # 如果请求失败，返回错误信息
        return f"Error: {str(e)}", 400
    
    # 使用 BeautifulSoup 解析网页内容
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 移除不需要的标签，包括脚本、样式、图片、导航等
    for element in soup(["script", "style", "img", "svg", "head", "header", "sidebar", "nav", "aside", "footer"]):
        element.decompose()
    
    # 移除特定类名的广告和不需要的元素
    unwanted_classes = ["ad", "ads", "advertisement", "promo", "side-panel"]
    for ad in soup.select(', '.join(f'.{cls}' for cls in unwanted_classes)):
        ad.decompose()
    
    # 删除所有标签的属性
    for tag in soup.find_all(True):  # True 匹配所有标签
        tag.attrs = {}
    
    # 将简化后的 HTML 内容转换为字符串
    simplified_html = soup.prettify()
    
    # 定义模板，包含一些基本样式
    template = """
      <!doctype html>
    <html lang="en">
      <head>
    <style>
      body { font-family: monospace; margin: 0 auto; line-height: 1.4; color: #333; max-width: 800px; }
      h1, h2, h3 { font-family: monospace; color: #333366; }
      p, li { font-size: 16px; text-align: justify; }
      a { color: #1a0dab; text-decoration: none; }
      a:hover { text-decoration: underline; }
      img { max-width: 100%; height: auto; }
      .container { padding: 40px; }
    </style>
    </head>
      <body>
        <div class="container">
          {{ content | safe }}
        </div>
      </body>
    </html>
    """
    # 使用 Flask 的 render_template_string 方法渲染 HTML 模板
    return render_template_string(template, content=simplified_html)

if __name__ == '__main__':
    app.run(debug=True)
