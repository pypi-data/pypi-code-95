# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['invisible_hand',
 'invisible_hand.config',
 'invisible_hand.core',
 'invisible_hand.scripts',
 'invisible_hand.scripts.shared_options',
 'invisible_hand.utils']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=20.3.0,<21.0.0',
 'beautifulsoup4>=4.9.1,<5.0.0',
 'click>=7.1.2,<8.0.0',
 'colorama>=0.4.3,<0.5.0',
 'gitpython>=3.1.7,<4.0.0',
 'google-api-python-client>=1.10.0,<2.0.0',
 'google-auth-httplib2>=0.0.4,<0.0.5',
 'google-auth-oauthlib>=0.4.1,<0.5.0',
 'halo>=0.0.30,<0.0.31',
 'httpx>=0.14.1,<0.15.0',
 'iso8601>=0.1.12,<0.2.0',
 'lxml>=4.5.2,<5.0.0',
 'oauth2client>=4.1.3,<5.0.0',
 'prompt-toolkit>=3.0.6,<4.0.0',
 'pydantic>=1.7,<2.0',
 'pygsheets>=2.0.3,<3.0.0',
 'requests>=2.24.0,<3.0.0',
 'rich>=9.2.0,<10.0.0',
 'selenium>=3.141.0,<4.0.0',
 'tabulate>=0.8.7,<0.9.0',
 'tomlkit>=0.7.0,<0.8.0',
 'tqdm>=4.48.2,<5.0.0',
 'trio>=0.16.0,<0.17.0',
 'typer[all]>=0.3.2,<0.4.0',
 'xlsxwriter>=1.3.3,<2.0.0']

entry_points = \
{'console_scripts': ['hand = invisible_hand.cli:app']}

setup_kwargs = {
    'name': 'invisible-hand',
    'version': '0.3.1',
    'description': 'Automate your workflow with github classroom',
    'long_description': '# Invisible Hand 👊\n\nInvisible Hand helps you manage your classroom under Github organization.<br>\nIt utilizes `Google Sheets` , `GitHub Classroom` and `GitHub` seamlessly.\n\n## Installation\n\n#### 1. Install this tool via pip\n\n `pip install invisible-hand`\n\n Use `hand -h` to test if it is installed\n\n```\n╰─❯ hand -h\nUsage: hand [OPTIONS] COMMAND [ARGS]...\n\n  Manage your classroom under Github organization.\n\nOptions:\n  --custom-base TEXT    Use custom base folder for configs\n  --install-completion  Install completion for the current shell.\n  --show-completion     Show completion for the current shell, to copy it or\n                        customize the installation.\n\n  -h, --help            Show this message and exit.\n\nCommands:\n  add-students       Invite students to join our Github organization\n  announce-grade     Announce student grades to each hw repo\n  config             Config File utilities\n  crawl-classroom    Get student\'s submissions from Github Classroom\n  event-times        Retrieve information about late submissions <repo-\n                     hash>...\n\n  grant-read-access  Make TAs being able to read all homework repos...\n  patch-project      Patch to student homeworks\n```\n\n#### 2. Install chromedriver\n\n* Mac : `brew cask install chromedriver`\n* Ubuntu : `apt install chromium-chromedriver`\n\n## Getting Started\n\n**1. Create config file**\n\nThe main config file is located in `$HOME/.invisible-hand/config.toml`. <br>\nRun `hand config create` to create a template and use `hand config edit` to open it with an editor.\n\n**2. `(Not required)` Getting your `client_secret.json` for accessing GoogleSheets**\n\nTo run the command:[ `Announce Grade` ](#announce-grade), follow the steps below to setup your environment first\n\n1. Follow [Authorization for pygsheets][pygsheet-auth] to get your credential file (`client_secret.json`)\n2. Locate your secret file and use `hand config copy-client-secret YOUR-SECRET-FILE` to copy it into the cache.\n\n    This command would automatically rename your secret file to (`$HOME/.invisible-hand/client_secret.json`)\n\n[pygsheet-auth]: https://pygsheets.readthedocs.io/en/stable/authorization.html\n\n## Quick references\n\n(This tool supports auto-completion, use `hand --install-completion` to add completion support to your shell)\n\n+ `hand`: The root command, use `-h` to see more information\n  + `config`: subcommand to handle config files, use `-h` to see more information\n    + `create`: Create a config file from template to `$HOME/.invisible-hand/config.toml`\n    + `check`: Check if the format your config file is valid\n    + `path`: Show the root path to your config folder, default to `$HOME/.invisble-hand`\n    + `edit`: Open your config file with your default editor. (use `--editor <your editor>` to open your another one)\n    + `copy-client-secret`: Copy Google\'s `client_secret.json` to the cache folder.\n      + use `hand config copy-client-secret -h` to see more information\n  + [`add-students 🧑\u200d💼student1 🦸\u200d♂️student2 ...`][add-students]: Invite users into your GitHub organization\n    + `🧑\u200d💼student`- GitHub handle of the student\n  + `grant-read-access 📝 hw-title`:  Grant TA\'s group read access to all repo with such prefix.\n    + `📝 hw-title`- title prefix of the homework (e.g. `hw3`)\n  + [`patch-project 📝 hw-title  🚧 patch-branch`][patch-project]: Patch project to Students homeworks\n  + [`crawl-classroom 📝 hw-title 📦 submission-file`][crawl-classroom]: Crawl submission status of students on GitHub Classroom\n    + `📦 submission-file`- file to store submission output\n  + [`event-times 📦 submission-file`][event-times]: Check if there\'s late submissions\n  + [`announce-grade 📝 hw-title`][announce-grade]: Announce grade to students by opening issues in their repos\n\n\n---\n\n## Add Students\n\n#### FAQ\n\n* Some students report that they didn\'t get the invitation email.\n\n    Invite student into your organization from their email. This should be Github\'s issue.\n\n    > about 2 of 80 students got this issue from our previous experience.\n\n\n\n## Patch Project\n\nPatch to student homework repositories.\n\n**Workflow**\n\nTake homework : **`hw3`**(the title of your homework in github classroom) for example: <br>\nThe repository: **`tmpl-hw3`** would be your template for initializing homeworks.\n\n#### 1. Create another repo with name **`tmpl-hw3-revise`** to update your template\n\n#### 2. Inside **`tmpl-hw3-revise`**\n\n1. Create a revision branch **`2-revise-for-node-definition`** (whatever you like)\n\n<p align="center">\n<img src="./imgs/patch-branches.png" alt="name of the branch" width="640">\n</p>\n\n2. Create an issuse with the identiacal title **`2-revise-for-node-definition` )**\n   1.  the content of that issue would become the content of your PR message.\n\n<p align="center">\n<img src="./imgs/patch-template-issue.png" alt=" template issue" width="640">\n</p>\n\n#### 3. Open GitHub Classroom\n\nSelect your assignment (**`hw3`**) and disable `assignment invitation URL` of **`hw3`**\n\n<p align="center">\n<img src="./imgs/patch-diable-hw.png" alt="disable invitation url" width="640">\n</p>\n\n#### 4. Create an PR to your template repo (**`hw3`**)\n\n``` sh\nhand patch-project hw3 --only-repo="tmpl-hw3" 2-revise-for-node-definition\n```\n\n#### 5. Accept the PR in your template repository (**`tmpl-hw3`**)\n\nAfter that, enable the `assignment invitation URL` of `hw3` in GitHub Classroom.<br>\nNow you have succcessfully updated your template repo.\n\n#### 6. Create PRs to students template repositories ( `hw3-<their github id>` )\n\nPatch to every repository that uses **hw3** as the prefix under your GitHub organization.\n\n``` sh\nhand patch-project hw3 2-revise-for-node-definition\n```\n\n#### 7. Merge the revision branch **`2-revise-for-node-definition`** inside `tmpl-hw3`\n\n\nAfter this step, all documents are updated\n\n#### 8. Reactivate the invitation URL\n\n<p align="center">\n<img src="./imgs/patch-enable-hw.png" alt="reactivate invitation url" width="640">\n</p>\n\n\n## Crawl Classroom\n\nCrawling homework submission data from Github Classroom\n\nThis is a web crawler for Github Classroom, which is the input of [ `Event Times` ][event-times]\n\n### Config File\n\n* **config.toml**:\n  + `[crawl_classroom]:login` : your login id in Github Classroom\n  + `[crawl_classroom]:classroom_id` : the id field of your classroom RESTful page URL. (see the image below)\n\n<p align="center">\n <img src="./imgs/clsrm_id.png" alt="id field in the url of github classroom" width="640">\n</p>\n\n\n\n### FAQ\n\n* ChromeDriver\n\n  ```\n  selenium.common.exceptions.SessionNotCreatedException: Message: session not created:\n  This version of ChromeDriver only supports Chrome version 79\n  ```\n\n    upgrade your chromedriver via `brew cask upgrade chromedriver`\n  * All students not submitted\n    + Remember to set deadline of hw on the GitHub classroom (note that deadline can only be set at a future time)\n\n<p align="center">\n<strong>Demo</strong><br>\n<img src="./demos/github_classroom_craw.gif" alt="github_classroom_craw" width="640">\n</p>\n\n\n\n\n## Event Times\n\nRetrieve information about late submissions\n\n**What it actually does**\n\nCompare the last publish-time of specific git commit in each repository and print out which passed the deadline.\n\n\n**Example**\n\n``` sh\nhand event-times  --target-team="2020-inservice-students" --deadline="2019-11-12 23:59:59"  hw1-handin-0408.txt\n```\n\n\n\n## Announce Grade\n\nPublish feedbacks by creating Issue to student\'s homework repo.\n\nThis sciprt requires you to\n  + Use a `GoogleSpreadSheet` to record every student\'s grade inside a strictly named tab.\n  + Strictly structured Github repository.\n\n\n**Explanation**\n\nIn our scheme, each student would get a git repository for every homework project.<br>\n\nTake homework `hw3` with two students `Anna` and `Bella` for example.<br>\nWe expect there would be 2 repos under our GitHub organization, which are `hw3-Anna` and `hw3-Bella`.<br>\n\nAnnoucing the grade for `hw3` actually means to open 1 issue to `hw3-anna` and `hw3-bella` respectively.\n\nTo make sure the script correctly functions:\n+ students grade should be recorded in the SpreadSheet with a tab called `hw3`.\n+ You should keep a `Markdown` file for each student using their `student-id` as the filename to describe their homework result.\n  + e.g. (if `Anna`\'s sutdent-id is `0856039`, then `0856039.md` should record `Anna`\'s overall feedbacks).\n  + **Behold: `student-id` should be unique.**\n\n**Format and Structure for those files**\n\n+ 0856039.md (`Anna`)\n\n  ```markdown\n  Hi, @Anna\n\n  ## Information\n  + Grade: ${grade}\n    + testcase : ${grade_testcase}/100 pts\n    + report : ${grade_report}/5 pts\n\n  + Grader: @{grader}\n  + Feedback:\n      Good Job\n\n  ## Note\n  If you got any questions about your grade\n  please make a comment stating your arguments below and tag the grader in the comment.\n  ```\n\n  This markdown file contains python template strings(`${grade}`),<br>\n  These strings are the column names inside your SpreadSheet tab `hw3`.\n\n+ Structure of the GitHub Repo:\n  ``` markdown\n    . Hw-manager # root of your git repo (the name is configured in `$HOME/.invisible-hand/config.toml`)\n    ├── hw3\n    │\xa0\xa0 └── reports\n    │\xa0\xa0     ├── 0411276.md\n    │\xa0\xa0     ├── 0856039.md (**Anna**)\n    └── hw4 # other homework dir\n  ```\n\n+ Structure of the Google SpreadSheet\n  | student_id | grade | grade_report | grade_testcase | grader |\n  | :--------: | :---: | :----------: | :------------: | :----: |\n  |  0856039   |  93   |      5       |       87       |  @TA1  |\n  |  0411276   |  80   |      5       |       75       |  @TA2  |\n\n\n### Config file\n\n* **config.toml**\n  + `[github]:personal_access_token`\n  + `[github]:organization`\n  + `[announce_grade]:feedback_source_repo` (e.x.: Hw-manager)\n  + `[google_spreadsheet]:spreadsheet_id`\n* **client_secret.json** (follow [here](https://pygsheets.readthedocs.io/en/stable/authorization.html) to download your oauth2 secret file and renamed it to **client_secret.json**)\n\n#### Instructions to follow\n\n1. Edit config files properly.\n2. Create feedbacks for students in your `feedback_source_repo`\n   1. **Make sure you commit and push the feedbacks to `master` branch**\n   2. Fill out the SpreadSheet\n3. Use this script\n   1. For testing, it\'s recommended to use the `--only-id` option\n\n       ```sh\n       hand announce-grade <hw_title> [--only-id 👨\u200d🎓student-id]\n       ```\n\n\n[event-times]: #event-times\n[add-students]: #add-students\n[patch-project]: #patch-project\n[crawl-classroom]: #crawl-classroom\n[announce-grade]: #announce-grade',
    'author': 'Ian Chen',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
