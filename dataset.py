import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm


def debug_page_structure(driver, url):
    """调试页面结构，找到正确的选择器"""
    driver.get(url)
    time.sleep(3)

    print(f"调试页面: {url}")
    print("页面标题:", driver.title)

    # 尝试多种可能的选择器
    selectors_to_try = [
        'a.title',
        'a[class*="title"]',
        'h2 a',
        'h3 a',
        '.post-title a',
        '[data-post] a',
        'a[href*="/p/"]',
        'a[href*="/post/"]'
    ]

    for selector in selectors_to_try:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"选择器 '{selector}' 找到 {len(elements)} 个元素")
                # 打印前3个链接作为示例
                for i, elem in enumerate(elements[:3]):
                    href = elem.get_attribute('href')
                    text = elem.text.strip()
                    print(f"  {i + 1}. {text[:50]}... -> {href}")
                return selector
        except Exception as e:
            print(f"选择器 '{selector}' 出错: {e}")

    return None


def get_post_urls(driver, base_url, pages=3, debug_first=True):
    """批量获取帖子链接，遍历N页"""
    urls = []

    # 既然已经知道有效选择器是 'a[href*="/p/"]'，可以直接使用
    correct_selector = 'a[href*="/p/"]'

    # 如果需要调试，仍然可以运行调试函数
    if debug_first:
        first_page_url = f"{base_url}/?page=1"
        debug_selector = debug_page_structure(driver, first_page_url)
        if debug_selector:
            correct_selector = debug_selector

    print(f"使用选择器: {correct_selector}")

    for page in range(1, pages + 1):
        url = f"{base_url}/?page={page}"
        print(f"正在处理第{page}页: {url}")

        try:
            driver.get(url)
            # 等待页面加载
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            time.sleep(2)  # 额外等待时间

            # 尝试找到帖子链接
            links = driver.find_elements(By.CSS_SELECTOR, correct_selector)

            if not links:
                print(f"第{page}页未找到帖子链接")
                continue

            page_urls = []
            for link in links:
                href = link.get_attribute('href')
                if href and ('biostars.org' in href or href.startswith('/')):
                    if href.startswith('/'):
                        href = base_url + href
                    page_urls.append(href)

            print(f"第{page}页找到 {len(page_urls)} 个链接")
            urls.extend(page_urls)

        except Exception as e:
            print(f"第{page}页加载异常: {e}")
            # 打印更多调试信息
            try:
                print(f"当前URL: {driver.current_url}")
                print(f"页面标题: {driver.title}")
            except:
                pass

    return urls


def debug_post_structure(driver, url):
    """调试单个帖子的结构"""
    driver.get(url)
    time.sleep(3)

    print(f"\n调试帖子: {url}")
    print("页面标题:", driver.title)

    # 尝试多种内容选择器
    content_selectors = [
        'span[itemprop="text"]',
        '.post-body',
        '.post-content',
        '[class*="content"]',
        '.question-body',
        '.answer-body',
        'div[data-post]',
        '.post-text'
    ]

    for selector in content_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"内容选择器 '{selector}' 找到 {len(elements)} 个元素")
                for i, elem in enumerate(elements[:2]):
                    text = elem.text.strip()[:100]
                    print(f"  {i + 1}. {text}...")
                return selector
        except Exception as e:
            print(f"选择器 '{selector}' 出错: {e}")

    return None


def scrape_post(driver, url):
    """抓取单个帖子内容：title, question, answers"""
    try:
        driver.get(url)
        # 等待页面加载
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        time.sleep(3)  # 增加等待时间

        # 获取标题
        title = driver.title.split(' — ')[0].strip() if ' — ' in driver.title else driver.title.strip()

        # Biostars特定的内容选择器
        content_selectors = [
            # 原始选择器
            'span[itemprop="text"]',
            # Biostars常见的内容选择器
            '.post-content',
            '.post-body',
            '[class*="post-text"]',
            '[class*="content"]',
            # 问题和答案的特定选择器
            '.question .post-body',
            '.answer .post-body',
            # 更通用的选择器
            'div[data-value]',
            '.rendered-content',
            # 如果是markdown渲染的内容
            '.markdown-body'
        ]

        question = ""
        answers = []
        found_content = False

        for selector in content_selectors:
            try:
                all_texts = driver.find_elements(By.CSS_SELECTOR, selector)
                if all_texts and any(elem.text.strip() for elem in all_texts):
                    # 过滤掉空内容
                    valid_texts = [elem.text.strip() for elem in all_texts if elem.text.strip()]
                    if valid_texts:
                        question = valid_texts[0]
                        answers = valid_texts[1:] if len(valid_texts) > 1 else []
                        found_content = True
                        print(f"成功使用选择器 '{selector}' 获取内容")
                        break
            except Exception as e:
                continue

        # 如果标准选择器都失败了，尝试更详细的调试
        if not found_content:
            print(f"标准选择器失败，调试页面结构: {url}")
            try:
                # 尝试查找所有可能包含文本的元素
                text_elements = driver.find_elements(By.XPATH, "//*[string-length(normalize-space(text())) > 50]")
                if text_elements:
                    # 取前几个有意义的文本块
                    texts = []
                    for elem in text_elements[:10]:  # 只取前10个
                        text = elem.text.strip()
                        if len(text) > 50 and not any(
                                skip in text.lower() for skip in ['cookie', 'javascript', 'error', 'loading']):
                            texts.append(text)

                    if texts:
                        question = texts[0]
                        answers = texts[1:] if len(texts) > 1 else []
                        found_content = True
                        print(f"使用XPath获取到 {len(texts)} 个文本块")
            except Exception as e:
                print(f"XPath方法也失败: {e}")

        # 最后的备选方案
        if not found_content:
            try:
                # 获取页面的主要内容区域
                main_content = driver.find_element(By.TAG_NAME, 'main')
                if main_content and main_content.text.strip():
                    question = main_content.text.strip()[:1000]  # 限制长度
                    found_content = True
                    print("使用main标签获取内容")
            except:
                try:
                    # 最后尝试body的文本内容
                    body = driver.find_element(By.TAG_NAME, 'body')
                    body_text = body.text.strip()
                    if body_text:
                        # 简单清理，去除导航和页脚内容
                        lines = body_text.split('\n')
                        content_lines = [line.strip() for line in lines if len(line.strip()) > 20]
                        if content_lines:
                            question = content_lines[0][:1000]
                            print("使用body文本获取内容")
                        else:
                            question = "无法获取页面内容"
                    else:
                        question = "页面内容为空"
                except:
                    question = "内容获取失败"

        result = {
            'url': url,
            'title': title,
            'question': question,
            'answers': answers
        }

        # 打印调试信息
        print(f"标题: {title[:50]}...")
        print(f"问题长度: {len(question)}")
        print(f"答案数量: {len(answers)}")

        return result

    except Exception as e:
        print(f"抓取帖子失败 {url}: {e}")
        import traceback
        traceback.print_exc()
        return None


def main(pages=3, output_file='biostars_qa.json', debug_mode=True):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    driver = webdriver.Chrome(options=options)

    try:
        base_url = "https://www.biostars.org"
        print(f"开始抓取 {pages} 页帖子链接...")

        # 如果是调试模式，先只处理1页
        if debug_mode:
            pages = 1
            print("调试模式：只处理第1页")

        post_urls = get_post_urls(driver, base_url, pages, debug_mode)
        print(f"共抓取到帖子链接数: {len(post_urls)}")

        if not post_urls:
            print("没有获取到帖子链接，请检查网站结构是否变化")
            return

        # 如果是调试模式，也调试第一个帖子的结构
        if debug_mode and post_urls:
            print("\n调试第一个帖子结构...")
            debug_post_structure(driver, post_urls[0])

        results = []
        print(f"开始抓取帖子内容...")

        # 限制抓取数量（调试时）
        urls_to_process = post_urls[:5] if debug_mode else post_urls

        for url in tqdm(urls_to_process):
            data = scrape_post(driver, url)
            if data:
                results.append(data)
            time.sleep(1)  # 添加延迟

        print(f"共抓取有效帖子数: {len(results)}")

        if results:
            print(f"保存到文件 {output_file} ...")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print("完成！")
        else:
            print("没有成功抓取到任何帖子内容")

    finally:
        driver.quit()


if __name__ == "__main__":
    # 首先以调试模式运行
    # main(pages=1, debug_mode=True)

    # 如果调试成功，可以注释上面一行，取消注释下面一行运行完整版本
     main(pages=5, debug_mode=False)