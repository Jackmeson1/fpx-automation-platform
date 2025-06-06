import time
from argparse import ArgumentParser, Namespace
import shlex
from typing import List

from selenium.common.exceptions import NoSuchElementException, WebDriverException, StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select

from SystemObject.gui_node import GuiNode, BrowserType, GuiType, GuiElemParser, FindBy
from SystemTestCase.SysTestCase import SysTcFail
from ftnt_nodes.ftnt_cli import FosCli
from monitor.pysys_log import pysys_logger


class FosParamParser:
    parser = ArgumentParser()
    parser.add_argument('-c', '--cate', type=str)
    parser.add_argument('-f', '--field', type=str)
    parser.add_argument('-s', '--sub_field', type=str)
    parser.add_argument('-t', '--menu_tab', type=str)
    parser.add_argument('-C', '--col', type=str)
    # parser.add_argument('-by', '--by', type=FindBy, choices=list(FindBy), default=FindBy.TEXT)
    parser.add_argument('-by', '--by', type=str, choices=[getattr(FindBy, k) for k in dir(FindBy)], default=FindBy.TEXT)
    parser.add_argument('value', nargs='*', type=str)


class FosGui(GuiNode):
    def __init__(self, ip='localhost',
                 port='',  # Use default port
                 user='admin',
                 passwd='',
                 conn_type=GuiType.HTTP,
                 browser_type=BrowserType.FIREFOX,
                 accept_untrusted_cert=True,
                 timeout=GuiNode.DEFAULT_TIMEOUT,
                 wait_time=GuiNode.DEFAULT_WAIT_TIME,
                 labels: dict = {}):
        GuiNode.__init__(self, ip, port, user, passwd, conn_type, browser_type, accept_untrusted_cert,
                         timeout=timeout, wait_time=wait_time, labels=labels)

    def _init_tc_func(self):
        super()._init_tc_func()
        self.tc_func.update({
            'expand_menu': self.expand_menu,
            'click_menu': self.click_menu,
            'edit_entry': self.edit_entry,
            'field_select': self.field_select,
            'field_set': self.field_set,
            'field_append': self.field_append,
            'field_input': self.field_set_text,
            'field_dropdown_select': self.field_dropdown_select,
            'radio_choose': self.radio_choose,
            'create_new': self.create_new,
            'delete_row': self.delete_row,
            'select_row': self.select_row,
            'select_all_rows': self.select_all_rows,
            'delete_all_rows': self.delete_all_rows,
            'validate_page': self.validate_page,
            'show_column': self.show_column
        })

    def login(self):
        # self.init_browser()
        # url = self.ip + ':' + self.port
        # if self.conn_type == GuiType.HTTP:
        #     url = 'http://' + url
        # elif self.conn_type == GuiType.HTTPS:
        #     url = 'https://' + url
        # else:  # unsupported protocols
        #     pysys_logger.error('unsupported protocol {} for url: {}'.format(self.conn_type, url))
        #     raise ConnectionError('unsupported protocol {} for url: {}'.format(self.conn_type, url))
        # self.get(url)
        super().login()
        # elem = self.find_elem_clickable('username', find_by=FindBy.ID)
        # elem.send_keys(self.user)
        # self.find_elem('secretkey', find_by=FindBy.ID).send_keys(self.passwd)
        # self.find_elem_clickable('login_button', find_by=FindBy.ID).click()
        for i in range(2):
            elem = self.find_elem_clickable('username', find_by=FindBy.ID)
            if elem:
                elem.send_keys(self.user)
                self.find_elem('secretkey', find_by=FindBy.ID).send_keys(self.passwd)
                self.find_elem_clickable('login_button', find_by=FindBy.ID).click()
            try:
                v, by = GuiNode.trans_find_value('Log & Report', FindBy.TEXT)
                # self.wait_for_visible(v, by, timeout=20)
                self.wait_for_visible(v, by)
                self.logged_in = True
                break
            except:
                continue
        if not self.logged_in:
            self.proc_err("Fails to login GuiNode: {}".format(self.node_name))

    def _parse_param(self, param: str) -> Namespace:
        opts = FosParamParser.parser.parse_args(shlex.split(param))
        # param_list = [x.strip('"') for x in shlex.split(param)]
        # opts = FosParamParser.parser.parse_args(param_list)
        if opts.value is None:
            self.proc_err('Element Target value must be set.')
        return opts

    def expand_menu(self, name: str):
        name = name.strip('"')
        menu = self.find_elem_text(name, tag='div')
        section = self.find_elem('./ancestor::*[contains(@class, "section")]', node=menu)
        if section.get_attribute('class').find('activate') == -1:  # not yet expanded
            section.click()
            self.tc_log_info('Expand menu: "{}"'.format(name))
            self.curr_elem = section
            return section
        if section.get_attribute('class').find('activate') == -1:  # still not yet expanded
            self.proc_err('Failed to expend the menu {}.'.format(name))

    def click_menu(self, parm_str: str):
        opts = self._parse_param(parm_str)
        if opts.menu_tab:
            section = self.expand_menu(opts.menu_tab)
        value: str = opts.value[0]
        self.find_elem('//a[normalize-space()="{}"]'.format(value), node=section).click()
        time.sleep(2)
        self.tc_log_info('Clicked menu "{}"'.format(value))
        # elif not self.curr_elem:
        #     self.curr_elem = self.find_elem('//body')
        # if opts.value:
        #     menu_elem = self.curr_elem.find_element_by_xpath('//a[normalize-space()="{}"]'.format(opts.value[0]))gg
        # else:
        #     err_text = 'Failed to click menu, menu name must be given.'
        #     self.tc_log_err(err_text)
        #     raise SysTcFail(err_text)
        # if menu_elem:
        #     menu_elem.click()
        # else:
        #     self.proc_err('Failed to click and open Menu {} does not exist.'.format(opts.menu))

    def field_select(self, param: str):
        opts = self._parse_param(param)
        if not opts.field:
            self.proc_err('"-f" (field) must be set for selecting value for a field')
        xpath = '//label[normalize-space()="{}"]/ancestor::div[1]//select'.format(opts.field)
        select = Select(self.find_elem(xpath))
        value: str = opts.value[0]
        try:
            select.select_by_visible_text(value)
            self.tc_log_info('Select "{}" on field "{}"'.format(value, opts.field))
        except NoSuchElementException:
            self.proc_err('Failed to select the given option: "{}"'.format(value))

    def field_dropdown_select(self, param: str):
        opts = self._parse_param(param)
        if not opts.field:
            self.proc_err('"-f" (field) must be set for selecting value for a field')
        xpath = '//label[normalize-space()="{}"]/ancestor::div[1]//div[contains(@class,"select-widget")]' \
            .format(opts.field)
        self.find_elem(xpath).click()
        # dropdown = self.find_elem_visible('//div[@class="selection-dropdown"]')
        xpath = '//div[@class="selection-dropdown"]//span[@class and normalize-space()="{}"]/f-icon'.format(
            opts.value[0])
        # to_select = self.find_elem_clickable(xpath)
        # to_select.click()
        self.click_elem(xpath)
        # self.find_elem_clickable(xpath).click()
        self.tc_log_info('Select "{}" from dropdown list for field "{}"'.format(opts.value[0], opts.field))

    def show_column(self, col: str):
        col = col.strip('"')
        action = ActionChains(self.browser)
        header_tab = self.find_elem_visible('fixed-header-container', FindBy.CLASS_NAME)
        # time.sleep(3)
        action.move_to_element(header_tab).perform()
        # time.sleep(2)
        button = self.find_elem_clickable('//button[contains(@class, "table-settings")]')
        # time.sleep(2)
        button.click()
        col_list_div = self.find_elem_visible('pop-up-menu-tooltip', FindBy.CLASS_NAME)
        col_item = self.find_elem_clickable('//button[.="{}"]'.format(col), node=col_list_div)
        if col_item.get_attribute('class') != 'fa-apply':  # if the desired the field is not shown on the table yet
            col_item.click()
        # self.click_button("Apply")
        self.click_elem('.//button[normalize-space()="Apply"]', FindBy.XPATH, node=col_list_div)
        self.tc_log_info('Column "{}" on current table page is shown.'.format(col))

    def delete_row(self, param: str):
        opts = self._parse_param(param)
        if not opts.col:
            self.proc_err('"-C / --col" (column) must be set for selecting value for a column')
        if self._select_row(opts.value[0], opts.col):
            self.click_button('Delete')
            self.click_button('OK')
        else:
            self.tc_log_warning('Not able to select row with field "{}" = "{}".'.format(opts.col, opts.value[0]))

    def select_row(self, param: str):
        opts = self._parse_param(param)
        if not opts.col:
            self.proc_err('"-C / --col" (column) must be set for selecting value for a column')
        if self._select_row(opts.value[0], opts.col) is None:
            self.tc_log_warning('Not able to select row with field "{}" = "{}".'.format(opts.col, opts.value[0]))

    def _select_row(self, value: str, col_name: str) -> WebElement:
        col_id = self._get_tab_column_id(col_name)
        xpath = '//div[@column-id="{}"]//div[normalize-space()="{}"]'.format(col_id, value)
        return self._click_elem(xpath, FindBy.XPATH)

    def select_all_rows(self) -> List[WebElement]:
        # return self._multi_ctrl_click('//div[contains(@class,"first-cell")][contains(@class,"row-cell")]', FindBy.XPATH)
        return self._shift_click_all('div.first-cell.row-cell', FindBy.CSS_SELECTOR)

    def delete_all_rows(self, implicit_row=True):
        # if self.select_all_rows() and self.click_button('Delete'):
        #     self.click_button('OK')
        while True:
            elems = self.shift_click_range('div.first-cell.row-cell', FindBy.CSS_SELECTOR)
            n = len(elems)
            if n == 0 or n == 1 and implicit_row:
                break
            if self.click_button('Delete'):
                self.click_button('OK')

    def validate_page(self):
        invalid_elem = self._find_elem('ng-invalid', FindBy.CLASS_NAME)
        if invalid_elem:
            self.proc_err('Page validation failed @ field "{}".'.format(invalid_elem.text))
        else:
            self.tc_log_info('Page validation succeeded.')

    def _get_tab_column_id(self, col_name: str) -> str:
        headers = self.find_elements('header-cell', FindBy.CLASS_NAME)
        for h in headers:
            if h.text == col_name:
                return h.get_attribute('data-column-id')
        return None

    def _get_atrr_by_text(self, text, attr_name, by, value) -> str:
        elems = self.find_elements(value, by)
        for elem in elems:
            if elem.text == text:
                return elem.get_attribute(attr_name)
        return None

    def get_col_id(self, col: str) -> str:
        xpath = '//div[@column-id and normalize-space()="{}"]'.format(col)
        return self.find_elem(xpath).get_attribute('column-id')

    def edit_entry(self, param: str):
        opts = self._parse_param(param)
        col_id = self.get_col_id(opts.col)
        value: str = opts.value[0]
        if col_id:
            xpath = '//div[@column-id="{}" and normalize-space()="{}"'.format(col_id, value)
            elem = self.find_elem(xpath)
            actions = ActionChains(self.browser)
            actions.double_click(elem).perform()
            self.tc_log_info('Double click to edit Entry of {} ({}) : {}'.format(opts.col, col_id, value))
        else:
            self.proc_err('Entry with value "{}" on column "{}" does not exist on current page'
                          .format(value, opts.col))

    def create_new(self, name: str = None):
        self.click_button('Create New')
        info_text = 'Created New Entry'
        if name:
            self.click_button(name)
            info_text += ' of "{}"'.format(name)
        self.wait_for_visible('dialog.form', FindBy.NAME)
        self.tc_log_info(info_text)

    def toggle_enable(self, field: str):
        self._toggle(field)
        self.tc_log_info('Toggle enable field "{}"'.format(field))

    def toggle_disable(self, field: str):
        self._toggle(field, turn_off=True)
        self.tc_log_info('Toggle disable field "{}"'.format(field))

    def _toggle(self, field: str, turn_off=False):
        xpath = '//field-label[normalize-space()="{}"]/input[@type="checkbox"]'.format(field)
        elem = self.find_elem(xpath)
        cls_attr = elem.get_attribute('class')
        assert type(cls_attr) is str
        if turn_off != cls_attr.find('ng-empty') >= 0:
            elem.click()

    def radio_choose(self, param: str):
        opts = self._parse_param(param)
        if opts.field is None:
            self.proc_err('"-f" (Field) must be set')
        sector = self.find_elem('//label[normalize-space()="{}"]//ancestor::div[1]'.format(opts.field))
        value = opts.value[0]
        # self.click_elem('//label[normalize-space()="{}"]/preceding-sibling::input[1]'.format(value), node=sector)
        self.click_elem('//label[normalize-space()="{}"]'.format(value), node=sector)
        self.tc_log_info('Radio value: "{}" has been chosen for field "{}"'.format(value, opts.field))

    def field_set_text(self, param: str):
        opts = self._parse_param(param)
        if opts.field is None:
            self.proc_err('"-f" (Field) must be set')
        value = opts.value[0]
        self.find_elem('//label[normalize-space()="{}"]/..//input[@type="text"]'.format(opts.field)).send_keys(value)
        self.tc_log_info('TEXT value "{}" has been set for field "{}"'.format(value, opts.field))

    def field_set(self, param: str):
        # TODO: unselected the current selected options first

        # append options to be set
        # opts, value_set, sub_field_text = self._multi_select_parse(param)
        # for v in opts.value:
        #     target = self.find_elem_clickable('//*[text()="{}"]/ancestor::div[1]'.format(v), node=option_list)
        #     if target.get_attribute('class').find('selected') == -1:
        #        # target value is not yet selected
        # target.click()
        # self.click_button('Close')
        # info_text = 'Set "{}" as "{} {}"'.format(opts.field, sub_field_text, value_set)
        # self.tc_log_info(info_text)
        self.field_append(param)

    def field_append(self, param: str):
        opts, value_set, sub_field_text = self._multi_select_parse(param)
        for v in opts.value:
            attempts = self.attempts
            while attempts > 0:
                option_list = self.find_elem("virtual-results", FindBy.CLASS_NAME)
                # target = self.find_elem_clickable('//*[text()="{}"]/ancestor::div[1]'.format(v), node=option_list)
                target = self._wait_to_click('//*[text()="{}"]/ancestor::div[1]'.format(v), node=option_list)
                if target:
                    if target.get_attribute('class').find('selected') == -1:
                        # target value is not yet selected
                        target.click()
                    break
                else:
                    attempts -= 1
            if attempts <= 0:
                self.proc_err('Failed to select target option "{}"'.format(v))

        self.click_button('Close')
        info_text = 'Append "{}" as "{} {}"'.format(opts.field, sub_field_text, value_set)
        self.tc_log_info(info_text)

    def _multi_select_parse(self, param: str):
        opts = self._parse_param(param)
        if opts.field is None:
            self.proc_err('"-f" (Field) must be set')
        sector = self.find_elem('//label[normalize-space()="{}"]/ancestor::div[1]'.format(opts.field))
        self.find_elem('//div[contains(@class,"select-widget")]', node=sector).click()
        # dialog = self.find_elem('//div[@class="dialog"]')
        # dialog = self.find_elem_visible('//div[@class="dialog"]')
        # wait until all inputs are enabled under multiple selection dialog
        # self.wait_non_presence('//div/[@class="dialog"]//input[@disabled]', FindBy.XPATH)
        dialog_path = '//div[@class="dialog"]'
        if opts.sub_field:
            # self.find_elem('//label[normalize-space()="{}"]/preceding-sibling::input[1]'.format(opts.sub_field),
            #                node=dialog).click()

            # self.wait_for_invisible('//f-icon[contains(@class, "fa-loading"]', FindBy.XPATH)
            # self.wait_for_invisible('radio-group', FindBy.CLASS_NAME, node=dialog)
            # self.wait_non_presence('input[@disabled]', FindBy.XPATH, node=dialog)
            # self.wait_non_presence('//div/[@class="dialog"//input[@disabled]', FindBy.XPATH)
            # cat = self.find_elem_clickable('//label[normalize-space()="{}"]'.format(opts.sub_field), node=dialog)
            xpath = dialog_path + '//label[normalize-space()="{}"]'.format(opts.sub_field)
            cat = self.find_elem_clickable(xpath)
            self.wait_till_enabled('..//input', FindBy.XPATH, node=cat)
            cat.click()
        if opts.cate:
            # categories = self.find_elements(dialog_path + '//label[@class="category"]')
            # for cate in categories:
            #     cate_text: str = cate.text
            #     expand_button = self.find_elem('/button', node=cate)
            #     cate_expended = expand_button.get_attribute('class').find('activate') >= 0
            #     if cate_text.lstrip().upper().startswith(opts.cate):  # it is the targeted category
            #         if not cate_expended:
            #             expand_button.click()
            #     elif cate_expended:  # not targeted sub category but expanded
            #         expand_button.click()
            i = 1
            cate_path = dialog_path + '//label[@class="category"]'
            cate = self.find_elem(cate_path + '[1]')
            while cate:
                more = self.attempts
                while more > 0:
                    try:
                        cate_text: str = cate.text
                        expand_button = self.find_elem('/button', node=cate)
                        cate_expended = expand_button.get_attribute('class').find('active') >= 0
                        if cate_text.lstrip().upper().startswith(opts.cate):  # it is the targeted category
                            if not cate_expended:
                                expand_button.click()
                        elif cate_expended:  # not targeted sub category but expanded
                            expand_button.click()
                        break
                    except StaleElementReferenceException:
                        cate = self.find_elem(cate_path + '[{}]'.format(i))
                        more -= 1
                i += 1
                cate = self._find_elem(cate_path + '[{}]'.format(i))

        # option_list = self.find_elem(dialog_path + '//div[@class="virtual-results"]')
        value_set = ', '.join(opts.value)
        sub_field_text = opts.sub_field + ':' if opts.sub_field else ''
        return opts, value_set, sub_field_text


class FpxGui(FosGui):
    def __init__(self, ip='localhost',
                 port='',  # Use default port
                 user='admin',
                 passwd='',
                 conn_type=GuiType.HTTP,
                 browser_type=BrowserType.FIREFOX,
                 accept_untrusted_cert=True,
                 timeout=GuiNode.DEFAULT_TIMEOUT,
                 wait_time=GuiNode.DEFAULT_WAIT_TIME,
                 labels={}):
        super().__init__(ip, port, user, passwd, conn_type, browser_type, accept_untrusted_cert, timeout, wait_time, labels)
