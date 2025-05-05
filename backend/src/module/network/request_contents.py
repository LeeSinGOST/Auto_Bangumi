import logging
import re
import xml.etree.ElementTree

from module.conf import settings
from module.models import Torrent

from .request_url import RequestURL
from .site import rss_parser

logger = logging.getLogger(__name__)


class RequestContent(RequestURL):
    def get_torrents(
        self,
        _url: str,
        _filter: str = None,
        limit: int = None,
        retry: int = 3,
    ) -> list[Torrent]:
        soup = self.get_xml(_url, retry)
        if soup:
            torrent_titles, torrent_urls, torrent_homepage = rss_parser(soup)
            torrents: list[Torrent] = []
            if _filter is None:
                _filter = "|".join(settings.rss_parser.filter)
            
            # 过滤掉无效的种子链接
            valid_items = []
            for _title, torrent_url, homepage in zip(
                torrent_titles, torrent_urls, torrent_homepage
            ):
                # 检查种子链接是否有效
                if self.check_torrent_url(torrent_url):
                    valid_items.append((_title, torrent_url, homepage))
                else:
                    logger.warning(f"[Network] Invalid torrent URL skipped: {torrent_url}")
            
            # 处理有效的种子链接
            for _title, torrent_url, homepage in valid_items:
                if re.search(_filter, _title) is None:
                    torrents.append(
                        Torrent(name=_title, url=torrent_url, homepage=homepage)
                    )
                if isinstance(limit, int):
                    if len(torrents) >= limit:
                        break
            return torrents
        else:
            logger.warning(f"[Network] Failed to get torrents: {_url}")
            return []
    
    def check_torrent_url(self, url: str) -> bool:
        """检查种子链接是否有效"""
        req = self.get_url(url, retry=1, check_status=True)
        return req is not None

    def get_xml(self, _url, retry: int = 3) -> xml.etree.ElementTree.Element:
        req = self.get_url(_url, retry)
        if req:
            return xml.etree.ElementTree.fromstring(req.text)

    # API JSON
    def get_json(self, _url) -> dict:
        req = self.get_url(_url)
        if req:
            return req.json()

    def post_json(self, _url, data: dict) -> dict:
        return self.post_url(_url, data).json()

    def post_data(self, _url, data: dict) -> dict:
        return self.post_url(_url, data)

    def post_files(self, _url, data: dict, files: dict) -> dict:
        return self.post_form(_url, data, files)

    def get_html(self, _url):
        return self.get_url(_url).text

    def get_content(self, _url):
        req = self.get_url(_url)
        if req:
            return req.content

    def check_connection(self, _url):
        return self.check_url(_url)

    def get_rss_title(self, _url):
        soup = self.get_xml(_url)
        if soup:
            return soup.find("./channel/title").text
