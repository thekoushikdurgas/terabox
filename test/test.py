import webbrowser

url = "https://d.1024tera.com/file/3d4f2086f2df1589df4019af69cc7cf8?fid=4398293442739-250528-894344255561041&dstime=1758252676&rt=sh&sign=FDtAER-DCb740ccc5511e5e8fedcff06b081203-L0%2B%2FI31vQ7F6o8d%2F5%2FiJBHv1TPc%3D&expires=8h&chkv=0&chkbd=0&chkpc=&dp-logid=299853021490518886&dp-callid=0&r=261785170&sh=1&region=jp"

# For Chrome (need to register first)
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
# webbrowser.get('chrome').open(url)

# # For Firefox (built-in support)
# webbrowser.get('firefox').open(url)
# import webbrowser

# url = "https://www.example.com"

# Open in default browser (same as above)
# webbrowser.open(url)

# Open in new browser window
# webbrowser.open_new(url)

# Open in new browser tab
webbrowser.open_new_tab(url)
