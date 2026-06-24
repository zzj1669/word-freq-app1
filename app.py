"""
词频分析可视化系统 - app.py
基于 Streamlit + pyecharts 的中文网页文本词频分析与可视化系统
"""

import streamlit as st
from streamlit_echarts import st_echarts
from pyecharts.charts import WordCloud, Bar, Line, Pie, Radar, Scatter, Funnel
from pyecharts import options as opts
import pandas as pd

# 导入自定义模块
from fetch import fetch_text
from tokenize_words import get_word_freq, get_text_stats, load_stopwords


def render_wordcloud(data: list, title: str = "词云图"):
    """生成词云图"""
    wc = WordCloud()
    wc.add("", data, word_size_range=[12, 60], shape="circle")
    wc.set_global_opts(title_opts=opts.TitleOpts(title=title))
    return wc


def render_bar(data: list, title: str = "柱状图"):
    """生成柱状图"""
    bar = Bar()
    bar.add_xaxis([item[0] for item in data])
    bar.add_yaxis("词频", [item[1] for item in data])
    bar.set_global_opts(
        title_opts=opts.TitleOpts(title=title, pos_left="center", pos_top="2%"),
        xaxis_opts=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(
                rotate=45,
                font_size=10,
                interval=0
            ),
            name="词汇",
            name_location="middle",
            name_gap=50
        ),
        yaxis_opts=opts.AxisOpts(name="词频"),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow")
    )
    return bar


def render_line(data: list, title: str = "折线图"):
    """生成折线图"""
    line = Line()
    line.add_xaxis([item[0] for item in data])
    line.add_yaxis("词频", [item[1] for item in data], is_smooth=True)
    line.set_global_opts(
        title_opts=opts.TitleOpts(title=title, pos_left="center", pos_top="2%"),
        xaxis_opts=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(
                rotate=45,
                font_size=10,
                interval=0
            ),
            name="词汇",
            name_location="middle",
            name_gap=50
        ),
        yaxis_opts=opts.AxisOpts(name="词频"),
        tooltip_opts=opts.TooltipOpts(trigger="axis")
    )
    return line


def render_pie(data: list, title: str = "饼图"):
    """生成饼图"""
    pie = Pie()
    pie.add(
        "词频占比",
        data,
        radius=["25%", "55%"],
        center=["60%", "55%"],
        label_opts=opts.LabelOpts(formatter="{b}: {d}%")
    )
    pie.set_global_opts(
        title_opts=opts.TitleOpts(title=title, pos_left="center", pos_top="2%"),
        legend_opts=opts.LegendOpts(
            orient="vertical",
            pos_left="left",
            pos_top="middle",
            textstyle_opts=opts.TextStyleOpts(font_size=12)
        )
    )
    return pie


def render_radar(data: list, title: str = "雷达图"):
    """生成雷达图（仅取前6个词）"""
    top6 = data[:6]
    max_freq = max([item[1] for item in top6]) if top6 else 1
    # 避免所有值相同时 max_freq=0 导致图表空白
    if max_freq <= 0:
        max_freq = 1

    radar = Radar()
    # pyecharts 2.x 的 RadarIndicatorItem 参数是 max_ 而非 max
    schema = [opts.RadarIndicatorItem(name=item[0], max_=max_freq) for item in top6]
    radar.add_schema(schema)
    radar.add("词频", [[item[1] for item in top6]],
              color="#E81860",
              areastyle_opts=opts.AreaStyleOpts(opacity=0.4))
    radar.set_global_opts(
        title_opts=opts.TitleOpts(title=title, pos_left="center"),
        legend_opts=opts.LegendOpts(pos_top="8%")
    )
    return radar


def render_scatter(data: list, title: str = "散点图"):
    """生成散点图"""
    scatter = Scatter()
    scatter.add_xaxis(range(1, len(data) + 1))
    scatter.add_yaxis("词频", [item[1] for item in data])
    scatter.set_global_opts(
        title_opts=opts.TitleOpts(title=title),
        xaxis_opts=opts.AxisOpts(name="词序"),
        yaxis_opts=opts.AxisOpts(name="词频")
    )
    return scatter


def render_funnel(data: list, title: str = "漏斗图"):
    """生成漏斗图"""
    funnel = Funnel()
    funnel.add(
        "词频",
        data,
        label_opts=opts.LabelOpts(position="inside"),
        tooltip_opts=opts.TooltipOpts(trigger="item", formatter="{b}: {c}次")
    )
    funnel.set_global_opts(
        title_opts=opts.TitleOpts(title=title, pos_left="center", pos_top="2%"),
        legend_opts=opts.LegendOpts(
            orient="horizontal",
            pos_top="8%",
            pos_left="center",
            item_width=12,
            item_height=12,
            textstyle_opts=opts.TextStyleOpts(font_size=10)
        )
    )
    return funnel


# 图表路由字典（dispatch table）
CHART_DISPATCH = {
    "词云": render_wordcloud,
    "柱状图": render_bar,
    "折线图": render_line,
    "饼图": render_pie,
    "雷达图": render_radar,
    "散点图": render_scatter,
    "漏斗图": render_funnel
}


def main():
    """主函数"""
    st.set_page_config(page_title="词频分析可视化系统", layout="wide")
    
    st.title("中文网页词频分析与可视化系统")
    st.markdown("---")
    
    # 侧边栏配置
    st.sidebar.header("图表设置")
    chart_type = st.sidebar.selectbox(
        "选择图表类型",
        list(CHART_DISPATCH.keys()),
        index=0
    )
    min_freq = st.sidebar.slider(
        "最低词频过滤",
        min_value=1,
        max_value=20,
        value=1,
        help="过滤词频低于此值的词汇（默认过滤低频无意义词）"
    )
    top_n = st.sidebar.slider(
        "显示词汇数量(Top-N)",
        min_value=5,
        max_value=50,
        value=20,
        help="设置图表中显示的高频词汇数量上限"
    )
    
    # 主界面
    url = st.text_input(
        "输入网页URL",
        placeholder="例如：https://news.sina.com.cn/",
        help="输入任意中文网页地址"
    )
    
    if url:
        with st.spinner("正在抓取网页内容..."):
            # Step 1: 抓取网页
            result = fetch_text(url)
            
            if not result['success']:
                st.error(f"❌ 抓取失败: {result['error']}")
                return
            
            st.success("✅ 网页抓取成功")
            
            # 显示标题
            st.subheader("网页标题")
            st.info(result['title'])
            
            # Step 2: 文本分析
            text = result['text']
            
            if not text or len(text.strip()) < 50:
                st.warning("提取的文本内容过短，可能无法进行有效分析")
                return
            
            # 获取文本统计
            stats = get_text_stats(text)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总字符数", stats['total_chars'])
            with col2:
                st.metric("中文字符数", stats['chinese_chars'])
            with col3:
                st.metric("词汇数", stats['total_words'])
            
            # Step 3: 词频统计
            top_words = get_word_freq(text, min_freq=min_freq, top_n=top_n)
            
            if not top_words:
                st.warning("未找到符合条件的词汇，请降低词频过滤阈值")
                return
            
            # 显示词频表格
            st.subheader(f"词频排名前{len(top_words)}的词汇")
            df_words = pd.DataFrame(top_words, columns=["词汇", "词频"])
            st.dataframe(df_words, use_container_width=True)
            
            # CSV下载
            csv = df_words.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="下载词频CSV",
                data=csv,
                file_name="word_freq.csv",
                mime="text/csv"
            )
            
            # Step 4: 图表可视化
            st.subheader(f"{chart_type}展示")
            
            # 使用字典派发渲染图表
            chart_func = CHART_DISPATCH.get(chart_type)
            if chart_func:
                try:
                    chart = chart_func(top_words, title=f"{chart_type} - {result['title']}")
                    st_echarts(chart, height=500)
                except Exception as e:
                    st.error(f"图表渲染失败: {str(e)}")
            
            # 显示原文片段
            with st.expander("查看原文片段"):
                st.text_area("提取的文本", text[:2000], height=200)


if __name__ == "__main__":
    main()
