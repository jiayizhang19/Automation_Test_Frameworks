
# 初始化配置
conf = configparser.ConfigParser()
conf.read(os.path.join(CONFIGDIR, 'conf.ini'), encoding='utf-8')

class Message_manager:
    pass
    # 业务方法：发动钉钉消息-整体报告
    def send_all_result(self, result):
       pass

    # 业务方法：发送单条钉钉消息
    def send_result(self, file_name, case_result, case_name, report_part_path):
        pass

    # 基础方法：发送钉钉消息，失败转发
    def send_to_dingding(self, dingding_token, title, text, at_all=False):
        pass

    # 基础方法：发送钉钉消息
    def send_to_dingding_base(self, dingding_index, title, text, at_all=False):
       pass