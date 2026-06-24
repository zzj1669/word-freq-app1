"""
分词与词频统计模块 - tokenize_words.py
功能：中文分词、停用词过滤、词频统计
"""

import jieba
from collections import Counter
import os
import re


# 停用词文件路径（可配置）
STOPWORDS_FILE = os.path.join(os.path.dirname(__file__), 'stopwords_cn.txt')


def load_stopwords(filepath: str = STOPWORDS_FILE) -> set:
    """
    加载停用词表
    
    Args:
        filepath: 停用词文件路径
    
    Returns:
        set: 停用词集合
    """
    stopwords = set()
    
    # 默认停用词（如果文件不存在）
    default_stopwords = [
        '的', '了', '和', '是', '就', '都', '而', '及', '与', '着',
        '或', '一个', '没有', '我们', '你们', '他们', '它们', '这个', '那个',
        '之', '以', '为', '于', '上', '下', '中', '里', '外', '内',
        '这', '那', '它', '他', '她', '我', '你', '谁', '什么', '怎么',
        '如何', '为什么', '因为', '所以', '但是', '然而', '如果', '虽然',
        '可以', '可能', '应该', '需要', '必须', '一定', '非常', '很', '太',
        '更', '最', '把', '被', '让', '给', '向', '从', '到', '在',
        '有', '无', '没', '不', '也', '还', '又', '再', '只', '就',
        '要', '会', '能', '做', '去', '来', '看', '说', '想', '知道',
        '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
        '百', '千', '万', '亿', '年', '月', '日', '时', '分', '秒',
        '号', '第', '等', '等等', '及', '其', '其中', '其他', '另外',
        '以下', '以上', '之间', '通过', '根据', '按照', '关于', '对于',
        '由于', '为了', '使得', '从而', '进而', '因此', '于是', '然后',
        '接着', '最后', '首先', '其次', '再次', '最终', '开始', '结束',
        '进行', '进行', '实现', '实现', '完成', '完成', '使用', '使用',
        '包括', '包含', '涉及', '相关', '相应', '对应', '属于', '属于',
        '作为', '作为', '成为', '成为', '形成', '形成', '产生', '产生',
        '出现', '出现', '发生', '发生', '存在', '存在', '具有', '具有',
        '保持', '保持', '维持', '维持', '继续', '继续', '持续', '持续',
        '不断', '不断', '一直', '一直', '已经', '已经', '正在', '正在',
        '将', '将要', '即将', '即将', '曾', '曾经', '曾经', '刚刚',
        '刚刚', '刚才', '刚才', '目前', '目前', '现在', '现在', '当前',
        '当前', '今天', '今天', '昨天', '昨天', '明天', '明天', '今年',
        '今年', '去年', '去年', '明年', '明年', '近期', '近期', '近期',
        '最近', '最近', '最近', '此前', '此前', '此后', '此后', '之后',
        '之后', '之前', '之前', '以前', '以前', '今后', '今后', '将来',
        '将来', '未来', '未来', '过去', '过去', '历史', '历史', '长期',
        '长期', '短期', '短期', '中期', '中期', '暂时', '暂时', '永久',
        '永久', '始终', '始终', '总', '总是', '总是', '全', '全部',
        '全部', '整体', '整体', '局部', '局部', '部分', '部分', '个别',
        '个别', '某些', '某些', '有些', '有些', '很多', '很多', '许多',
        '许多', '大量', '大量', '少量', '少量', '少许', '少许', '多少',
        '多少', '几', '几个', '几个', '多少', '多少', '若干', '若干',
        '一些', '一些', '一点', '一点', '一定', '一定', '某种', '某种',
        '某些', '某些', '每个', '每个', '各个', '各个', '各自', '各自',
        '本身', '本身', '自身', '自身', '本身', '本身', '自己', '自己',
        '大家', '大家', '各位', '各位', '各位', '各位', '彼此', '彼此',
        '互相', '互相', '相互', '相互', '共同', '共同', '一起', '一起',
        '一同', '一同', '同时', '同时', '同步', '同步', '先后', '先后',
        '依次', '依次', '逐渐', '逐渐', '逐步', '逐步', '渐渐', '渐渐',
        '慢慢', '慢慢', '迅速', '迅速', '快速', '快速', '立即', '立即',
        '马上', '马上', '立刻', '立刻', '顿时', '顿时', '瞬间', '瞬间',
        '瞬间', '刹那', '刹那', '刹那', '突然', '突然', '忽然', '忽然',
        '意外', '意外', '偶然', '偶然', '偶尔', '偶尔', '经常', '经常',
        '常常', '常常', '往往', '往往', '通常', '通常', '一般', '一般',
        '正常', '正常', '常规', '常规', '惯例', '惯例', '传统', '传统',
        '现代', '现代', '新型', '新型', '新型', '新型', '新型', '新型',
        '新型', '新型', '新型', '新型', '新型', '新型', '新型', '新型',
        '新型', '新型', '新型', '新型', '新型', '新型', '新型', '新型'
    ]
    
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    word = line.strip()
                    if word:
                        stopwords.add(word)
        else:
            stopwords = set(default_stopwords)
    except Exception as e:
        print(f"加载停用词失败: {e}, 使用默认停用词")
        stopwords = set(default_stopwords)
    
    return stopwords


def tokenize(text: str, stopwords: set = None) -> list:
    """
    对文本进行分词
    
    Args:
        text: 待分词文本
        stopwords: 停用词集合（可选）
    
    Returns:
        list: 分词结果列表
    """
    if not text or not text.strip():
        return []
    
    # 使用jieba进行分词
    words = jieba.cut(text, cut_all=False)
    
    # 过滤停用词和无效词
    if stopwords is None:
        stopwords = load_stopwords()
    
    valid_words = []
    for word in words:
        word = word.strip()
        # 过滤条件：长度>=2，不在停用词表中，不是纯数字/标点
        if len(word) >= 2 and word not in stopwords:
            # 过滤纯数字
            if not re.match(r'^[\d\s\.,;:!?\'"()\[\]{}\-]+$', word):
                valid_words.append(word)
    
    return valid_words


def get_word_freq(text: str, min_freq: int = 1, top_n: int = 20) -> list:
    """
    统计词频并返回高频词列表
    
    Args:
        text: 待分析文本
        min_freq: 最低词频阈值
        top_n: 返回前N个高频词
    
    Returns:
        list: [(word, freq), ...] 按词频降序排列
    """
    if not text or not text.strip():
        return []
    
    # 分词
    words = tokenize(text)
    
    if not words:
        return []
    
    # 统计词频
    counter = Counter(words)
    
    # 过滤低频词并排序
    filtered = [(word, freq) for word, freq in counter.items() if freq >= min_freq]
    sorted_words = sorted(filtered, key=lambda x: x[1], reverse=True)
    
    # 返回前top_n个
    return sorted_words[:top_n]


def get_text_stats(text: str) -> dict:
    """
    获取文本统计信息
    
    Args:
        text: 待分析文本
    
    Returns:
        dict: 统计信息字典
    """
    if not text:
        return {
            'total_chars': 0,
            'chinese_chars': 0,
            'english_chars': 0,
            'digit_chars': 0,
            'total_words': 0,
            'unique_words': 0
        }
    
    # 统计各类字符
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    digit_chars = len(re.findall(r'[\d]', text))
    total_chars = len(text)
    
    # 分词统计
    words = tokenize(text)
    total_words = len(words)
    unique_words = len(set(words))
    
    return {
        'total_chars': total_chars,
        'chinese_chars': chinese_chars,
        'english_chars': english_chars,
        'digit_chars': digit_chars,
        'total_words': total_words,
        'unique_words': unique_words
    }


if __name__ == '__main__':
    # 测试示例
    test_text = """
    人工智能是计算机科学的一个分支，它企图了解智能的实质，
    并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
    该领域的研究包括机器人、语言识别、图像识别、自然语言处理等。
    """
    
    print("=== 分词测试 ===")
    words = tokenize(test_text)
    print(f"分词结果: {words[:20]}")
    
    print("\n=== 词频统计 ===")
    top_words = get_word_freq(test_text, min_freq=1, top_n=10)
    for word, freq in top_words:
        print(f"{word}: {freq}次")
    
    print("\n=== 文本统计 ===")
    stats = get_text_stats(test_text)
    for key, value in stats.items():
        print(f"{key}: {value}")