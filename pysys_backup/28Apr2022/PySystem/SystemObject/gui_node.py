import time

from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.remote.command import Command as WebCommand
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from enum import Enum
from argparse import ArgumentParser, Namespace
import shlex

from selenium.webdriver.remote.webelement import WebElement

from SystemObject.cli_node import CliNode
from SystemObject.sys_obj import SysObj

from typing import List

from SystemTestCase.SysTestCase import SysTcFail
from monitor.pysys_log import pysys_logger


class GuiType:
    HTTP = 'HTTP',
    HTTPS = 'HTTPS'


class BrowserType:
    FIREFOX = 'FIREFOX',
    CHROME = 'CHROME',
    IE = 'IE',
    EDGE = 'EDGE'


'''
    ID = "id"
    XPATH = "xpath"
    LINK_TEXT = "link text"
    PARTIAL_LINK_TEXT = "partial link text"
    NAME = "name"
    TAG_NAME = "tag name"
    CLASS_NAME = "class name"
    CSS_SELECTOR = "css selector"
'''

class FindBy(object):
    # cloned from By Class
    ID = By.ID
    XPATH = By.XPATH
    LINK_TEXT = By.LINK_TEXT
    PARTIAL_LINK_TEXT = By.PARTIAL_LINK_TEXT
    NAME = By.NAME
    TAG_NAME = By.TAG_NAME
    CLASS_NAME = By.CLASS_NAME
    CSS_SELECTOR = By.CSS_SELECTOR
    # defined by user
    TEXT = 'plain text'
    PLACE_HOLDER = 'place holder'


class GuiElemParser:
    parser = ArgumentParser()
    parser.add_argument('value', nargs='*')
    # parser.add_argument('-by', '--by', type=FindBy, choices=list(FindBy), default=FindBy.TEXT)
    parser.add_argument('-by', '--by', type=str, choices=[getattr(FindBy, k) for k in dir(FindBy)], default=FindBy.TEXT)
    parser.add_argument('-s', '--select', type=str)
    parser.add_argument('-i', '--input', type=str)
    parser.add_argument('-k', '--key', type=str)

    @classmethod
    def elem_parse(cls, elem_str: str) -> Namespace:
        return cls.parser.parse_args(elem_str)


class GuiParams:
    DEFAULT_TIMEOUT = 60
    DEFAULT_ATTEMPTS = 3
    DEFAULT_WAIT_TIME = 10


class GuiNode(CliNode):
    # LOWER_SET = 'abcdefghijklmnopqrstuvwxyz'
    # UPPER_SET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    DEFAULT_TIMEOUT = 60
    DEFAULT_ATTEMPTS = 3
    DEFAULT_WAIT_TIME = 10

    def __init__(self, ip='localhost',
                 port='8080',
                 user='admin',
                 passwd='',
                 conn_type=GuiType.HTTP,
                 browser_type=BrowserType.FIREFOX,
                 accept_untrusted_cert=False,
                 timeout=DEFAULT_TIMEOUT,
                 attempts=DEFAULT_ATTEMPTS,
                 wait_time=DEFAULT_WAIT_TIME,
                 labels: dict = {}):
        # SysObj.__init__(self, conn_type, ip, port, user, passwd, labels=labels)
        super().__init__(ip, port, user, passwd, conn_type,
                         timeout=timeout, attempts=attempts, wait_time=wait_time, labels=labels)
        # self.conn_type = conn_type
        self.browser_type = browser_type
        self.accept_untrusted_cert = accept_untrusted_cert
        # self.browser = self.init_browser(browser_type)
        self.curr_elem = None
        self.browser = None

    def _init_tc_func(self):
        super()._init_tc_func()
        self.tc_func.update({'click': self.click_at,
                             'click_button_xpath': self.click_button_xpath,
                             'click_button': self.click_button,
                             'search_elem': self.search_elem,
                             'locate_element': self.locate_element,
                             'right_select': self.right_select,
                             'right_click': self.right_click,
                             'ctrl_click': self.ctrl_click,
                             'shift_click': self.shift_click,
                             'press_key': self.press_key,
                             'validate': self.validate,
                             'validate_not': self.validate_not,
                             'input_text': self.input_text
                             })

    def proc_err(self, msg):
        self.tc_log_err(msg)
        raise SysTcFail(msg)

    def _parse_elem_param(self, param: str) -> Namespace:
        opts = GuiElemParser.parser.parse_args(shlex.split(param))
        if opts.value is None:
            self.proc_err('Element Target value must be set.')
        if not opts.by:
            opts.by = FindBy.TEXT
        if opts.by == FindBy.TEXT:
            opts.by = By.XPATH
            opts.value = ['//*[normalize-space()="{}"]'.format(opts.value[i]) for i in range(len(opts.value))]
        elif opts.by == FindBy.PLACE_HOLDER:
            opts.by = By.XPATH
            opts.value = ['//*[@placeholder="{}"]'.format(opts.value[i]) for i in range(len(opts.value))]
        return opts

    def locate_element(self, param: str):
        opts = self._parse_elem_param(param)
        # find_by = opts.by or FindBy.TEXT
        self.curr_elem = self.find_elem(opts.value[0], opts.by)

    def find_elements(self, value: str, find_by=FindBy.XPATH, tag='*', node: WebElement = None) -> List[WebElement]:
        value, by = self.trans_find_value(value, find_by, tag=tag)
        self.curr_elem = None
        if not node:
            node = self.browser
        return node.find_elements(by, value)

    def find_elem_xpath(self, value: str, node: WebElement = None) -> WebElement:
        return self.find_elem(value, node)

    def find_elem_text(self, value: str, node: WebElement = None, tag='*') -> WebElement:
        return self.find_elem(value, FindBy.TEXT, node=node, tag=tag)

    def find_elem_visible(self, value: str, find_by=FindBy.XPATH, tag='*', node: WebElement = None) -> WebElement:
        value, by = self.trans_find_value(value, find_by, tag)
        return self.wait_for_visible(value, by, node=node)
        # return self.find_elem(value, find_by, node)

    def find_elem_clickable(self, value: str, find_by=FindBy.XPATH, node: WebElement = None) -> WebElement:
        elem = self._wait_to_click(value, find_by, node=node)
        if elem:
            return elem
        else:
            self.proc_err('Could not find clickable element by "{}" : "{}"'.format(find_by, value))

    def _click_elem(self, value: str, find_by=FindBy.XPATH, node: WebElement = None) -> WebElement:
        for i in range(self.attempts):
            elem = self._wait_to_click(value, find_by, node=node)
            if elem:
                action = ActionChains(self.browser)
                action.move_to_element(elem).click().perform()
                break
        return elem

    def click_elem(self, value: str, find_by=FindBy.XPATH, node: WebElement = None) -> WebElement:
        elem = self._click_elem(value, find_by, node)
        if not elem:
            self.proc_err('Failed to click element "{} : {}"'.format(find_by, value))
        return elem

    def find_elem(self, value: str, find_by=FindBy.XPATH, node: WebElement = None, tag='*') -> WebElement:
        # if not node:
        #     node = self.curr_elem
        self.curr_elem = self._find_elem(value, find_by, node=node, tag=tag)
        if self.curr_elem is None:
            self.proc_err('Could not find any element with "{}" : "{}"'.format(find_by, value))
        else:
            return self.curr_elem

    def _find_elem(self, value: str, find_by=FindBy.XPATH, node: WebElement = None, tag='*') -> WebElement:
        elems = self.find_elements(value, find_by, tag=tag, node=node)
        elem = None
        if elems:
            if len(elems) != 1:
                self.tc_log_warning('More than 1 element found for {}: "{}"'.format(find_by, value))
            # self.curr_elem = elems[0]
            elem = elems[0]
        return elem

    def search_elem(self, param) -> bool:
        opts = self._parse_elem_param(param)
        # find_by = opts.by or FindBy.TEXT
        result = False
        for v in opts.value:
            if self._find_elem(v, opts.by):
                self.tc_log_info('Element is found with "{}" by "{}"'.format(v, opts.by))
                result = True
            else:
                self.proc_err('Could not find any element with "{}" : "{}"'.format(opts.by, v))
        return result

    def wait_for_show(self, param: str):
        opts = self._parse_elem_param(param)
        self.wait_for_visible(opts.value, opts.by)
        self.tc_log_info('element of "{}" shows up.'.format(param))

    def wait_for_presence(self, value, by, timeout=0, node: WebElement = None):
        if not node:
            node = self.browser
        if timeout == 0:
            timeout = self.timeout
        wait = WebDriverWait(node, timeout)
        wait.until(ec.presence_of_element_located((by, value)))

    def wait_non_presence(self, value, by, timeout=0, node: WebElement = None):
        if not node:
            node = self.browser
        if timeout == 0:
            timeout = self.timeout
        wait = WebDriverWait(node, timeout)
        res = wait.until_not(ec.presence_of_element_located((by, value)))
        return res

    # wait until the specified element presents and doesn't have "disabled" attribute
    def wait_till_enabled(self, value: str, by=FindBy.XPATH, node: WebElement = None, timeout=0):
        if not node:
            node = self.browser
        if timeout == 0:
            timeout = self.timeout
        value, by = self.trans_find_value(value, by)
        wait = WebDriverWait(node, timeout)
        target = wait.until(ec.presence_of_element_located((by, value)))
        wait = WebDriverWait(target, timeout)
        res = wait.until_not(ec.presence_of_element_located((FindBy.XPATH, "./self::*[@disabled]")))
        return res

    # wait until the specified element presents and its descendant and itself don't have "disabled" attribute
    def wait_till_enabled_all(self, value: str, by=FindBy.XPATH, node: WebElement = None, timeout=0):
        if not node:
            node = self.browser
        if timeout == 0:
            timeout = self.timeout
        value, by = self.trans_find_value(value, by)
        wait = WebDriverWait(node, timeout)
        target = wait.until(ec.presence_of_element_located((by, value)))
        wait = WebDriverWait(target, timeout)
        # res = wait.until_not(ec.presence_of_element_located((FindBy.XPATH, "//*[1]/descendant-or-self::*[@disabled]")))
        res = wait.until_not(ec.presence_of_element_located((FindBy.XPATH, "./descendant-or-self::*[@disabled]")))
        return res

    # wait until non of elements under the given node has "disabled" attribute
    def wait_till_enabled_descendant(self, node: WebElement = None, timeout=0):
        if not node:
            node = self.browser
        if timeout == 0:
            timeout = self.timeout
        wait = WebDriverWait(node, timeout)
        res = wait.until_not(ec.presence_of_element_located((FindBy.XPATH, "//*[@disabled]")))
        return res

    def wait_for_visible(self, value, by, timeout=0, node: WebElement = None) -> WebElement:
        if not node:
            node = self.browser
        if timeout == 0:
            timeout = self.timeout
        wait = WebDriverWait(node, timeout)
        return wait.until(ec.visibility_of_element_located((by, value)))

    def _wait_to_click(self, value: str, find_by=FindBy.XPATH, timeout=0, node: WebElement = None) -> WebElement:
        value, by = self.trans_find_value(value, find_by)
        if not node:
            node = self.browser
        if timeout == 0:
            timeout = self.timeout
        wait = WebDriverWait(node, timeout, ignored_exceptions=[StaleElementReferenceException])
        try:
            return wait.until(ec.element_to_be_clickable((by, value)))
        except TimeoutException:
            return None

    def wait_for_invisible(self, value, by, timeout=0, node: WebElement = None):
        if not node:
            node = self.browser
        if timeout == 0:
            timeout = self.timeout
        wait = WebDriverWait(node, timeout)
        value, by = GuiNode.trans_find_value(value, by)
        wait.until(ec.invisibility_of_element_located((by, value)))

    def validate(self, elem_str: str):
        opts = self._parse_elem_param(elem_str)
        if self._find_elem(opts.value[0], find_by=opts.by):
            self.tc_log_info('Validation succeeded with "{}".'.format(elem_str))
        else:
            self.proc_err('Validation failed - "{}.'.format(elem_str))

    def validate_not(self, elem_str: str):
        opts = self._parse_elem_param(elem_str)
        if self._find_elem(opts.value[0], find_by=opts.by):
            self.proc_err('Validation failed - "{}.'.format(elem_str))
        else:
            self.tc_log_info('Validation succeeded with "{}".'.format(elem_str))

    def click_at(self, elem_str: str):
        opts = self._parse_elem_param(elem_str)
        # find_by = opts.by or FindBy.TEXT
        self.find_elem(opts.value[0], find_by=opts.by).click()
        self.tc_log_info('Clicked At "{}": "{}"'.format(opts.by, opts.value[0]))

    def _click_at(self, value: str, by=FindBy.XPATH, node: WebElement = None):
        self.find_elem(value, by, node).click()

    def click_button_xpath(self, value: str) -> WebElement:
        # button = self.find_elem(value)
        button = self.find_elem(value)
        if not button:
            self.proc_err('button: ')
        if button.get_attribute('disabled'):
            button = None
            self.tc_log_warning('button XPATH - "%s" is disabled.' % value)
        else:
            button.click()
            self.tc_log_info('Clicked button @ XPATH "{}"'.format(value))
        return button

    def click_button(self, name: str) -> WebElement:
        name = name.strip('"')
        # value, by = self.trans_find_value(name, FindBy.TEXT, tag='button')
        # button = self._wait_to_click(value, by)
        try:
            button = self.find_elem_visible(name, FindBy.TEXT, tag='button')
        except TimeoutException:
            self.proc_err('button: "%s" doesn\'t exits' % name)
        if button.get_attribute('disabled'):
            button = None
            self.tc_log_warning('button "%s" is disabled.' % name)
        else:
            for i in range(self.attempts):
                try:
                    button.click()
                    self.tc_log_info('Clicked button "{}"'.format(name))
                    break
                except WebDriverException as e:
                    time.sleep(self.wait_time)
                    self.tc_log_warning('Failed to click button: "%s" due to: "%s".  trying again' % (name, str(e)))
        return button

    def right_click(self, elem_str: str):
        opts = self._parse_elem_param(elem_str)
        action = ActionChains(self.browser)
        # find_by = opts.by or FindBy.TEXT
        elem = self.find_elem(opts.value[0], find_by=opts.by)
        action.context_click(elem).perform()

    def right_select(self, elem_str: str):
        opts = self._parse_elem_param(elem_str)
        action = ActionChains(self.browser)
        # find_by = opts.by or FindBy.TEXT
        self.curr_elem = elem = self.find_elem(opts.value[0], opts.by)
        action.context_click(elem).perform()

    def press_key(self, elem_str: str):
        opts = GuiElemParser.elem_parse(elem_str)
        action = ActionChains(self.browser)
        # elem = self.find_elem(opts.by, opts.value[0])
        action.key_down(opts.key).key_up(opts.key).perform()

    def ctrl_click(self, elem_str: str):
        opts = GuiElemParser.elem_parse(elem_str)
        self._ctrl_click(opts.value[0], opts.by)

    def _ctrl_click(self, value: str, find_by=FindBy.TEXT, node: WebElement = None):
        if not node:
            node = self.browser
        self.curr_elem = elem = self.find_elem(value, find_by, node)
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).click(elem).key_up(Keys.CONTROL).perform()

    # BUG: click always perform as right click ?
    def _multi_ctrl_click(self, value: str, find_by=FindBy.TEXT, node: WebElement = None) -> List[WebElement]:
        if not node:
            node = self.browser
        if not self._wait_to_click(value, find_by, node=node):
            return []
        elems = self.find_elements(value, find_by, node=node)
        action = ActionChains(self.browser)
        action.key_down(Keys.CONTROL).perform()
        for elem in elems:
            # action.key_down(Keys.CONTROL).click(elem).key_up(Keys.CONTROL).perform()
            action.click(elem).perform()
        action.key_up(Keys.CONTROL).perform()
        return elems

    def _shift_click_all(self, value: str, find_by=FindBy.TEXT, node: WebElement = None) -> List[WebElement]:
        if not node:
            node = self.browser
        if not self._wait_to_click(value, find_by, node=node):
            return []
        elems = self.find_elements(value, find_by, node=node)
        action = ActionChains(self.browser)
        n = len(elems)
        if n == 1:
            elems[0].click()
        elif n > 1:
            elems[-1].location_once_scrolled_into_view
            elems[-1].click()
            action.move_to_element(elems[-1]).perform()
            # action.move_to_element(elems[-1]).click(elems[-1]).key_down(Keys.SHIFT).click(elems[0]).key_up(Keys.SHIFT).perform()
            action.move_to_element(elems[-1]).click().key_down(Keys.SHIFT).\
                move_to_element(elems[0]).click().key_up(Keys.SHIFT).perform()
        return elems

    def shift_click_range(self, value: str, find_by=FindBy.CSS_SELECTOR, node=None) -> List[WebElement]:
        if not node:
            node = self.browser
        if not self._wait_to_click(value, find_by, node=node):
            return []
        elems = self.find_elements(value, find_by, node=node)
        n = len(elems)
        if n >= 1:
            more = self.attempts
            while more > 0:
                try:
                    elems[0].click()
                    break
                except WebDriverException as e:
                    more -= 1
                    if more == 0:
                        self.proc_err('Failed to select the elements with given range by {}: {} due to Esception: {}'
                                      .format(find_by, value, e.msg))
                    time.sleep(self.wait_time)
                    elems = self.find_elements(value, find_by, node=node)
        if n > 1:
            action = ActionChains(self.browser)
            elems[-1].location_once_scrolled_into_view
            action.key_down(Keys.SHIFT).click(elems[-1]).key_up(Keys.SHIFT).perform()
        return elems

    def shift_click(self, elem_str: str):
        opts = GuiElemParser.elem_parse(elem_str)
        action = ActionChains(self.browser)
        # find_by = opts.by or FindBy.TEXT
        self.curr_elem = elem = self.find_elem(opts.value[0], opts.by)
        action.key_down(Keys.SHIFT).click(elem).key_up(Keys.SHIFT).perform()

    def input_text(self, elem_str: str):
        opts = GuiElemParser.elem_parse(elem_str)
        # find_by = opts.by or FindBy.TEXT
        self.curr_elem = elem = self.find_elem(opts.value[0], opts.by)
        elem.send_keys(opts.input)

    def exec_cmd(self, cmd, param=None):
        func_text = cmd + '({})'.format(param) if param else cmd
        try:
            eval('self.browser.' + func_text)
        except Exception:
            raise SysTcFail('Error: function {} is not supported for GUI node {}'.format(func_text, self.node_name))

    def get(self, url) -> dict:
        """
        Loads a web page in the current browser session.
        """
        return self.browser.execute(WebCommand.GET, {'url': url})

    def post(self, url) -> dict:
        return self.browser.execute(WebCommand.STATUS)

    def init_browser(self):
        if self.browser_type == BrowserType.FIREFOX:
            profile = webdriver.FirefoxProfile()
            profile.accept_untrusted_certs = self.accept_untrusted_cert
            profile.assume_untrusted_cert_issuer = self.accept_untrusted_cert
            self.browser = webdriver.Firefox(firefox_profile=profile)
        elif self.browser_type == BrowserType.CHROME:
            options = webdriver.ChromeOptions()
            if self.accept_untrusted_cert:
                options.add_argument('--ignore-certificate-errors')
            self.browser = webdriver.Chrome(chrome_options=options)
        elif self.browser_type == BrowserType.IE or self.browser_type == BrowserType.EDGE:
            capabilities = webdriver.DesiredCapabilities().INTERNETEXPLORER
            capabilities['acceptSslCerts'] = self.accept_untrusted_cert
            if self.browser_type == BrowserType.IE:
                self.browser = webdriver.Ie(capabilities=capabilities)
            else:
                self.browser = webdriver.Edge(capabilities=capabilities)
        else:
            raise AttributeError('Broswer Type: {} is not supported yet.'.format(self.browser_type))

    def login(self):
        self.init_browser()
        url = self.ip + ':' + self.port
        if self.conn_type == GuiType.HTTP:
            url = 'http://' + url
        elif self.conn_type == GuiType.HTTPS:
            url = 'https://' + url
        else:  # unsupported protocols
            pysys_logger.error('unsupported protocol {} for url: {}'.format(self.conn_type, url))
            raise ConnectionError('unsupported protocol {} for url: {}'.format(self.conn_type, url))
        self.get(url)

    def logout(self):
        self.browser.close()
        self.logged_in = False

    def http_login(self):
        self.get('http://{}'.format(self.ip))
        button = self.browser.find_element_by_xpath('//button[normalize-space(text())="Advanced"]')
        action = ActionChains()
        action.context_click(button)
        button.click()
        pass

    def https_login(self):
        pass

    def cli_login(self):
        pass

    @staticmethod
    def trans_find_value(value: str, by: FindBy, tag='*') -> tuple:
        if by == FindBy.TEXT:
            by = By.XPATH
            # value = './/{}[normalize-space(text())="{}"]'.format(tag, value)
            value = './/{}[normalize-space()="{}"]'.format(tag, value)
        elif by == FindBy.PLACE_HOLDER:
            by = By.XPATH
            value = './/{}[@placeholder="{}"]'.format(tag, value)
        if by == By.XPATH and value[0] != '.':
            value = '.' + value
        return value, by


class RepeatOperation(object):
    def __init__(self, operation: callable, node: GuiNode, msg: str = None):
        self.operation = operation
        self.node = node
        self.msg = msg if msg else 'Failed to execute {}.'.format(operation.__name__)

    def __call__(self, *args, **kwargs):
        def wraper(*args, **kwargs):
            more = self.node.attempts
            while more >= 1:
                try:
                    return self.operation(*args, **kwargs)
                except Exception as e:
                    if e in self.ignore_exceptions:
                        more -= 1
                        time.sleep(self.node.wait_time)
                    else:
                        raise e
            if more == 0:
                self.node.proc_err(self.msg)

            return wraper
