"""
网页抓取模块 - fetch.py
功能：从指定URL抓取网页内容，提取正文文本
"""

import requests
from bs4 import BeautifulSoup


def fetch_text(url: str, timeout: int = 10) -> dict:
    """
    从URL抓取网页内容并提取正文文本
    
    Args:
        url: 目标网页URL
        timeout: 请求超时时间（秒）
    
    Returns:
        dict: {
            'success': bool,      # 是否成功
            'html': str,          # 原始HTML
            'text': str,          # 提取的正文文本
            'title': str,         # 网页标题
            'error': str          # 错误信息（失败时）
        }
    """
    try:
        # 发送HTTP请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        
        # 自动检测编码
        if response.apparent_encoding:
            response.encoding = response.apparent_encoding
        else:
            # 兜底：从 headers 中获取编码
            content_type = response.headers.get('Content-Type', '')
            if 'charset=' in content_type.lower():
                charset = content_type.lower().split('charset=')[-1].split(';')[0].strip()
                response.encoding = charset
            else:
                response.encoding = 'utf-8'
        
        html = response.text
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取标题
        title = soup.title.string if soup.title else "无标题"
        
        # 移除script、style、nav、footer等非正文标签
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'iframe', 'noscript']):
            tag.decompose()
        
        # 提取正文文本
        text = soup.get_text(separator='\n', strip=True)
        
        # 清理多余空白
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = '\n'.join(lines)
        
        return {
            'success': True,
            'html': html,
            'text': text,
            'title': title,
            'error': None
        }
        
    except requests.Timeout:
        return {
            'success': False,
            'html': None,
            'text': None,
            'title': None,
            'error': '请求超时，请检查网络连接'
        }
    except requests.ConnectionError:
        return {
            'success': False,
            'html': None,
            'text': None,
            'title': None,
            'error': '网络连接失败，请检查URL是否正确'
        }
    except requests.RequestException as e:
        return {
            'success': False,
            'html': None,
            'text': None,
            'title': None,
            'error': f'请求失败: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'html': None,
            'text': None,
            'title': None,
            'error': f'未知错误: {str(e)}'
        }


def fetch_title(url: str) -> str:
    """
    仅提取网页标题
    
    Args:
        url: 目标网页URL
    
    Returns:
        str: 网页标题
    """
    result = fetch_text(url)
    return result.get('title', '无标题') if result['success'] else '获取失败'


if __name__ == '__main__':
    # 测试示例
    test_url = "https://news.sina.com.cn/"
    result = fetch_text(test_url)
    if result['success']:
        print(f"标题: {result['title']}")
        print(f"正文长度: {len(result['text'])} 字符")
        print(f"正文前200字:\n{result['text'][:200]}")
    else:
        print(f"错误: {result['error']}")