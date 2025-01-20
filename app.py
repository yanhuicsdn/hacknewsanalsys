import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

def extract_comments_from_hn(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取评论
        comments = []
        comment_rows = soup.find_all('tr', class_='athing comtr')
        
        for row in comment_rows:
            comment_text = row.find('div', class_='comment')
            if comment_text:
                comment_text = comment_text.get_text(strip=True)
                comments.append(comment_text)
        
        return comments
    except Exception as e:
        st.error(f"获取页面内容时出错: {str(e)}")
        return []

def analyze_comments(comments):
    if not comments:
        return None
        
    # 构建API请求数据
    prompt_data = {
        "task": "comment_analysis",
        "comments": comments,
        "request": "请分析这些评论中的不同观点，总结主要的讨论方向和各种不同的立场以及大概的占比。"
    }
    
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": "Bearer sk-ydcvskcyyzictsylxplbpqmqlpillcpkqznxclfjyohkefwt",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "messages": [{"role": "user", "content": json.dumps(prompt_data, ensure_ascii=False)}],
        "stream": False,
        "max_tokens": 4096,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"}
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data['choices'][0]['message']['content'].strip()
        else:
            st.error(f"API调用错误: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"API调用异常: {str(e)}")
        return None

def main():
    st.title("HackerNews 评论观点分析器")
    st.write("输入 HackerNews 讨论页面的URL，分析评论中的不同观点")
    
    url = st.text_input("请输入HackerNews讨论页面URL：")
    
    if st.button("分析观点"):
        if url:
            with st.spinner("正在获取评论内容..."):
                comments = extract_comments_from_hn(url)
                
            if comments:
                st.info(f"成功获取 {len(comments)} 条评论")
                
                with st.spinner("正在分析观点..."):
                    analysis = analyze_comments(comments)
                    
                if analysis:
                    st.subheader("观点分析结果")
                    st.write(analysis)
            else:
                st.warning("未能获取到任何评论，请确认URL是否正确")
        else:
            st.warning("请输入URL")

if __name__ == "__main__":
    main()
