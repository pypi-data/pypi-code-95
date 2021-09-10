import argparse
import logging
import os
from dataclasses import asdict
from .model import AlgoSite


def get_parser():
  parser = argparse.ArgumentParser()
  parser.add_argument('-l', '--log_level', type=int, default=20)
  parser.add_argument('-s', '--site_prefix', type=str, required=True)
  parser.add_argument('-p', '--problem_id', type=str)
  parser.add_argument('-u', '--user_id', type=str)
  return parser.parse_args()


if __name__ == '__main__':
  os.environ["WDM_LOG_LEVEL"] = str(logging.WARNING)
  ag = get_parser()
  logging.basicConfig(
      format='%(asctime)s %(levelname)-6s [%(filename)s:%(lineno)d] %(message)s',
      datefmt='%H%M%S',
  )
  logging.getLogger().setLevel(ag.log_level)
  logger = logging.getLogger('selenium.webdriver.remote.remote_connection')
  logger.setLevel(logging.WARNING)  # or any variant from ERROR, CRITICAL or NOTSET

  assert ag.problem_id or ag.user_id
  algosite = AlgoSite.get_site_by_prefix(ag.site_prefix)
  if ag.problem_id:
    print(asdict(algosite.crawl_problem(ag.problem_id)))
  else:
    print(asdict(algosite.crawl_solutions(ag.user_id)))
