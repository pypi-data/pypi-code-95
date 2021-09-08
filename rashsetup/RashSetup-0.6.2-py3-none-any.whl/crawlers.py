import queue
import typing
import multiprocessing
import logging
import logging.handlers
import scrapy.crawler
import sys
import subprocess
from .RashScrappers.RashScrappers.spiders import *
from .shared import *

ALL.extend(
    [
        "QueueHandler",
        "SettingsParser",
        "Setup",
        "RepoSpider",
        "READMESpider",
        "RawSetup",
        "TempHandler",
        "Investigator",
    ]
)


class QueueHandler(logging.handlers.QueueHandler):
    def __init__(self, queue_: queue.Queue):
        super().__init__(queue_)

    def handle(self, record) -> bool:
        # to make this pickle-able
        # avoiding all lambda functions from scrapy logs

        modified = logging.LogRecord(
            record.name,
            record.levelno,
            record.pathname,
            record.lineno,
            record.getMessage(),
            args=(),
            exc_info=record.exc_info,
            func=record.funcName,
            sinfo=record.stack_info,
        )

        return super().handle(modified)


class SettingsParser:
    def __init__(self, json_url: str, path=False):
        self.parsed = (
            JsonHandler(json_url).load() if path else JsonHandler().parse_url(json_url)
        )
        self.url = json_url

    def __getitem__(self, key: str) -> typing.Union["SettingsParser", bool, str]:
        if key == "result":
            return self

        elif key == "failed":
            return not self.validate()

        else:
            return "" if self.validate() else "exception"

    def __contains__(self, item: str) -> bool:
        return True  # assuming we check only for result, failed, exception keys
        # ! Assumed 100 % efficiency since this is one of a internal class

    def load(self):
        return self

    def close(self):
        ...

    def settings(self) -> str:
        return self.url

    def name(self) -> str:
        return self.parsed["name"]

    def version(self) -> str:
        return self.parsed["version"]

    def hosted(self) -> str:
        return self.parsed["hosted"]

    def readme(self) -> typing.Union[str, bool]:
        return self.parsed.get("readme", False)

    def desc(self) -> str:
        return self.parsed.get("desc", "A Rash Module")

    def required(self) -> typing.List[str]:
        return self.parsed.get("requires", [])

    def update_readme(self, raw: str) -> typing.NoReturn:
        self.parsed["readme"] = raw

    def validate(self) -> bool:
        required = ("name", "version", "hosted")  # required

        return all((_ in self.parsed for _ in required))

    def install_required(self) -> bool:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", *self.required()], check=True
            )
        except Exception as _:
            logging.exception("Failed to Install packages for %s, Aborting !", self.name())
            return False

        logging.debug("Installed Packages for %s", self.name())
        return True


class Setup:
    def __init__(self, pipe, *args):
        self.pipe = pipe
        self.cache = self.pipe.saved

        self.logger = format_root()
        self._side()
        self.start(*args)

    def _side(self):
        ...

    def start(self, *args, **kwargs):
        ...

    def save(self, _):
        handler = JsonHandler(TempHandler()(suffix=".json"))
        self.logger.info("Saving Results in %s", handler.file)
        handler.dump(self.cache)

        self.pipe.saved = handler


class READMESetup(Setup):
    def start(self, *args):
        process = scrapy.crawler.CrawlerProcess(None, False)

        process.crawl(READMESpider, self.cache, *args)
        process.join().addCallback(self.save)

        process.start()


class RepoSetup(Setup):
    def start(self, *args):
        process = scrapy.crawler.CrawlerProcess(None, False)

        process.crawl(RepoSpider, self.cache, *args)
        process.join().addCallback(self.save)

        process.start()


class RawSetup:
    def __init__(self, setup, *args):
        self.cache = None
        self.process = None
        self._prepare(setup, *args)

    def _prepare(self, setup, *args):
        self.cache = multiprocessing.Manager().Namespace()
        self._cache()
        self.process = multiprocessing.Process(None, setup, args=(self.cache, *args))

    def _cache(self):
        self.cache.saved = {"failed": True, "exception": "", "result": ""}

    def parse(self):
        if not hasattr(self.cache.saved, "__enter__"):
            return not self.cache.saved["failed"], self.cache.saved["result"]

        with self.cache.saved as parsed:
            status = not parsed.get("failed", True)
            result = parsed.get("result", "")
            result = (
                result
                if status and result
                else parsed.get("exception", "Invalid Results")
            )

        return status, result
