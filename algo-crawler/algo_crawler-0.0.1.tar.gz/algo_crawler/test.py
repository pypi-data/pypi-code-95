import unittest
from .model import Problem, Baekjoon, Leetcode, Kattis, Codeforce, Hackerrank, Codechef


class ModelTest(unittest.TestCase):
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_baekjoon(self):
    bj = Baekjoon()
    problem = bj.crawl_problem(1000)
    self.assertEqual(problem, Problem("BJ_1000", '1', "https://www.acmicpc.net/problem/1000", "A+B"))

    solution = bj.crawl_solutions("rbtmd1010")
    self.assertEqual(solution.user_id, "rbtmd1010")
    self.assertGreater(len(solution.problem_codes), 1000)

  def test_leetcode(self):
    lc = Leetcode()
    problem = lc.crawl_problem(1)
    self.assertEqual(problem, Problem(
        "LC_1",
        "1",
        "https://leetcode.com/problems/two-sum",
        "Two Sum",
    ))

  def test_kattis(self):
    kt = Kattis()
    problem = kt.crawl_problem("hello")
    self.assertEqual(problem, Problem(
        "KT_hello",
        '1.1',
        "https://open.kattis.com/problems/hello",
        "Hello World!",
    ))

  def test_codeforce(self):
    cf = Codeforce()
    problem = cf.crawl_problem("1A")
    self.assertEqual(problem, Problem(
        "CF_1A",
        '1000',
        'https://codeforces.com/contest/1/problem/A',
        'Theatre Square',
    ))

  def test_hackerrank(self):
    hr = Hackerrank()
    problem = hr.crawl_problem("30-hello-world")
    self.assertEqual(
        problem,
        Problem(
            "HR_30-hello-world",
            'Medium',
            'https://www.hackerrank.com/challenges/30-hello-world/problem',
            '30-hello-world',
        ))

  def test_codechef(self):
    cc = Codechef()
    problem = cc.crawl_problem("HS08TEST")
    self.assertEqual(
        problem, Problem(
            "CC_HS08TEST",
            'Practice(Beginner)',
            'https://www.codechef.com/problems/HS08TEST',
            'ATM',
        ))


if __name__ == '__main__':
  unittest.main()
