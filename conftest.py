import base64

import allure
import pytest
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from application.common.utils import Util
from application.task.executeTask import get_test_message, use_data

driver = None


# 获取运行用例信息
def pytest_generate_tests(metafunc):
    if "case" in metafunc.fixturenames:
        metafunc.parametrize("case", get_test_message(use_data))


# 指定运行默认站点
def pytest_addoption(parser):
    parser.addoption("--url", action="store", default="http://10.1.40.220")


@pytest.fixture
def node_url(request):
    return request.config.getoption("--url")


@pytest.fixture(scope='session', autouse=True)
def drivers(request):
    global driver
    if driver is None:
        chrome_options = webdriver.ChromeOptions()
        # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
        chrome_options.add_argument('--headless')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        # driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.set_window_size(1920, 1080)

    def fn():
        # 终结函数，用于driver对象的删除
        driver.quit()

    request.addfinalizer(fn)
    return driver


# 钩子函数，获取测试用例不同阶段的测试结果
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item):
    # 当测试失败的时候，自动截图，展示到html报告中
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    report.description = str(item.function.__doc__)
    # 返回report对象属性extra值
    extra = getattr(report, 'extra', [])
    if report.when == 'call':
        # 判断是否有该属性 ，xfail是预期错误标志
        xfail = hasattr(report, 'wasxfail')
        if (report.skipped and xfail) or (report.failed and not xfail):
            screen_img = _capture_screenshot_fail(item)
            if screen_img:
                html = '<div><img src="data:image/png;base64,%s" alt="screenshot" style="width:1920px;height:1080px;" ' \
                       'onclick="window.open(this.src)" align="right"/></div>' % screen_img
                extra.append(pytest_html.extras.html(html))
        elif report.passed:
            screen_img = _capture_screenshot_succ(item)
            if screen_img:
                html = '<div><img src="data:image/png;base64,%s" alt="screenshot" style="width:1920px;height:1080px;" ' \
                       'onclick="window.open(this.src)" align="right"/></div>' % screen_img
                extra.append(pytest_html.extras.html(html))
        report.extra = extra


def _capture_screenshot_fail(item):
    # 截图保存为base64
    screen_file = Util().screen_path_fail(item)
    driver.save_screenshot(screen_file)
    allure.attach.file(screen_file, "失败截图{}".format(item.function.__name__), allure.attachment_type.PNG)
    with open(screen_file, 'rb') as f:
        imageBase64 = base64.b64encode(f.read())
    return imageBase64.decode()


def _capture_screenshot_succ(item):
    screen_file = Util().screen_path_succ(item)
    driver.save_screenshot(screen_file)
    allure.attach.file(screen_file, "成功截图{}".format(item.function.__name__), allure.attachment_type.PNG)
    with open(screen_file, 'rb') as f:
        imageBase64 = base64.b64encode(f.read())
    return imageBase64.decode()
