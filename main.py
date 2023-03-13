from gui.custom_window import CustomWindow
from util.html_source import WebPage, write_html_file, create_style_css
from util.image_processing import create_clear_png

if __name__ == "__main__":
    create_clear_png()
    browser = WebPage()
    create_style_css()
    write_html_file(browser, "resources/images/clear.png", 1)
    write_html_file(browser, "resources/images/clear.png", 2)
    custom_window = CustomWindow(browser=browser)
    custom_window.mainloop()
