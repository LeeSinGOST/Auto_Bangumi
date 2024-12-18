import logging
import requests
import json
from module.models import Notification
from module.network import RequestContent

logger = logging.getLogger(__name__)


class QQpushNotification(RequestContent):
    """Server酱推送"""
    def __init__(self, token, chat_id):
        super().__init__()
        self.notification_url = f"https://push/sent"
        self.chat_id = chat_id
        self.token = token

    @staticmethod
    def gen_message(notify: Notification) -> str:
        text = f"""
        番剧名称：{notify.official_title}\n季度： 第{notify.season}季\n更新集数： 第{notify.episode}集\n
        """
        return text.strip()

    def post_msg(self, notify: Notification) -> bool:

        text = self.gen_message(notify)
        data = {'id':self.chat_id,'content':text,'from':'AB'}
        r = requests.post(self.token,json=data,timeout=0.1)
        logger.debug(f"qqpush notification: {token} {resp.status_code}")
        return resp.status_code == 200