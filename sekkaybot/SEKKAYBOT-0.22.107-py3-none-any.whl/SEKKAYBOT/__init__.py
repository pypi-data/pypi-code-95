try:
    # System imports.
    from typing import Tuple, Any, Union, Optional

    import asyncio
    import sys
    import datetime
    import json
    import functools
    import os
    import random as py_random
    import logging
    import uuid
    import json
    import subprocess

    # Third party imports.
    from fortnitepy.ext import commands
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
    from functools import partial

    import crayons
    import fortnitepy
    import BenBotAsync
    import FortniteAPIAsync
    import sanic
    import aiohttp
    import uvloop
except ModuleNotFoundError as e:
    print(f'Error: {e}\nAttempting to install packages now (this may take a while).')

    for module in (
        'crayons',
        'fortnitepy',
        'BenBotAsync',
        'FortniteAPIAsync',
        'sanic',
        'aiohttp',
        'requests',
        'uvloop'
    ):
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])

    os.system('clear')

    print('Installed packages, restarting script.')

    python = sys.executable
    os.execl(python, python, *sys.argv)


print(crayons.cyan(f'\nSekkayBOT made by Sekkay & Cousin. '
                   'USE CODE DEXE !'))
print(crayons.cyan(f'Discord server: discord.gg/tvJtRF25s2 - For support, questions, etc.'))

sanic_app = sanic.Sanic(__name__)
server = None

name = ""
friend = ""

password = "0098"
admin = "lil Sekkay","Sekkay Bot","TwitchCousin"
message_banned = "fnpy",'doener','Item','Notice','ク','ア','や','招','待','式','ボ','公','テ'
copied_player = ""
banned_player = "Kutchup Bot","1-MagoBot","2-MagoBot","3-MagoBot","4-MagoBot","5-MagoBot","6-MagoBot","7-MagoBot","8-MagoBot","9-MagoBot","10-MagoBot","11-MagoBot","12-MagoBot","13-MagoBot","14-MagoBot","15-MagoBot","16-MagoBot","17-MagoBot","18-MagoBot","19-MagoBot","20-MagoBot","21-MagoBot","22-MagoBot","23-MagoBot","24-MagoBot","25-MagoBot","26-MagoBot","27-MagoBot","28-MagoBot","29-MagoBot","30-MagoBot","31-MagoBot","32-MagoBot","33-MagoBot","35-MagoBot","36-MagoBot","1_MagoBot","2_MagoBot","3_MagoBot","4_MagoBot","5_MagoBot","6_MagoBot","7_MagoBot","8_MagoBot","9_MagoBot","10_MagoBot","11_MagoBot","12_MagoBot","13_MagoBot","14_MagoBot","15_MagoBot","16_MagoBot","17_MagoBot","18_MagoBot","19_MagoBot","20_MagoBot","21_MagoBot","22_MagoBot","23_MagoBot","24_MagoBot","25_MagoBot","26_MagoBot","27_MagoBot","28_MagoBot","29_MagoBot","30_MagoBot","31_MagoBot","32_MagoBot","33_MagoBot","34_MagoBot","35_MagoBot","36_MagoBot","37_MagoBot","38_MagoBot","39_MagoBot","40_MagoBot","41_MagoBot","42_MagoBot","43_MagoBot","44_MagoBot","45_MagoBot","46_MagoBot","47_MagoBot","48_MagoBot","49_MagoBot","50_MagoBot","51_MagoBot","52_MagoBot","53_MagoBot","54_MagoBot","55_MagoBot","56_MagoBot","57_MagoBot","58_MagoBot","59_MagoBot","60_MagoBot","1.AlphaBot","2.AlphaBot","3.AlphaBot","4.AlphaBot","5.AlphaBot","6.AlphaBot","7.AlphaBot","8.AlphaBot","9.AlphaBot","10.AlphaBot","11.AlphaBot","12.AlphaBot","13.AlphaBot","14.AlphaBot","15.AlphaBot","16.AlphaBot","17.AlphaBot","18.AlphaBot","19.AlphaBot","20.AlphaBot","21.AlphaBot","22.AlphaBot","23.AlphaBot","24.AlphaBot","25.AlphaBot","26.AlphaBot","27.AlphaBot","28.AlphaBot","29.AlphaBot","30.AlphaBot","31.AlphaBot","32.AlphaBot","33.AlphaBot","34.AlphaBot","35.AlphaBot","36.AlphaBot","37.AlphaBot","38.AlphaBot","39.AlphaBot","40.AlphaBot","41.AlphaBot","42.AlphaBot","43.AlphaBot","44.AlphaBot","45.AlphaBot","46.AlphaBot","47.AlphaBot","48.AlphaBot","49.AlphaBot","50.AlphaBot","51.AlphaBot","52.AlphaBot","53.AlphaBot","54.AlphaBot","55.AlphaBot","56.AlphaBot","57.AlphaBot","58.AlphaBot","59.AlphaBot","60.AlphaBot","61.AlphaBot","62.AlphaBot","63.AlphaBot","64.AlphaBot","65.AlphaBot","66.AlphaBot","67.AlphaBot","68.AlphaBot","69.AlphaBot","70.AlphaBot","71.AlphaBot","72.AlphaBot","73.AlphaBot","74.AlphaBot","75.AlphaBot","76.AlphaBot","77.AlphaBot","78.AlphaBot","79.AlphaBot","80.AlphaBot","81.AlphaBot","82.AlphaBot","83.AlphaBot","84.AlphaBot","85.AlphaBot","86.AlphaBot","87.AlphaBot","88.AlphaBot","89.AlphaBot","90.AlphaBot","91.AlphaBot","92.AlphaBot","93.AlphaBot","94.AlphaBot","95.AlphaBot","96.AlphaBot","97.AlphaBot","98.AlphaBot","99.AlphaBot","100.AlphaBot","1-AlphaBot","2-AlphaBot","3-AlphaBot","4-AlphaBot","5-AlphaBot","6-AlphaBot","1-AlphaBot","7-AlphaBot","8-AlphaBot","9-AlphaBot","10-AlphaBot","11-AlphaBot","12-AlphaBot","13-AlphaBot","14-AlphaBot","15-AlphaBot","16-AlphaBot","17-AlphaBot","18-AlphaBot","19-AlphaBot","20-AlphaBot","21-AlphaBot","22-AlphaBot","23-AlphaBot","24-AlphaBot","25-AlphaBot","26-AlphaBot","27-AlphaBot","28-AlphaBot","29-AlphaBot","30-AlphaBot","31-AlphaBot","32-AlphaBot","33-AlphaBot","34-AlphaBot","35-AlphaBot","36-AlphaBot","37-AlphaBot","38-AlphaBot","39-AlphaBot","40-AlphaBot","41-AlphaBot","42-AlphaBot","43-AlphaBot","44-AlphaBot","45-AlphaBot","46-AlphaBot","47-AlphaBot","48-AlphaBot","49-AlphaBot","50-AlphaBot","51-AlphaBot","52-AlphaBot","53-AlphaBot","54-AlphaBot","55-AlphaBot","56-AlphaBot","57-AlphaBot","58-AlphaBot","59-AlphaBot","60-AlphaBot","61-AlphaBot","62-AlphaBot","63-AlphaBot","64-AlphaBot","65-AlphaBot","66-AlphaBot","67-AlphaBot","68-AlphaBot","69-AlphaBot","70-AlphaBot","71-AlphaBot","72-AlphaBot","73-AlphaBot","74-AlphaBot","75-AlphaBot","76-AlphaBot","77-AlphaBot","78-AlphaBot","79-AlphaBot","80-AlphaBot","81-AlphaBot","82-AlphaBot","83-AlphaBot","84-AlphaBot","85-AlphaBot","86-AlphaBot","87-AlphaBot","88-AlphaBot","89-AlphaBot","90-AlphaBot","91-AlphaBot","92-AlphaBot","93-AlphaBot","94-AlphaBot","95-AlphaBot","96-AlphaBot","97-AlphaBot","98-AlphaBot","99-AlphaBot","100-AlphaBot","USE CODE BIGHEAD"
banned_player = "lil wayne","Finns 69","Recon Bot 1","Recon Bot 2","Recon Bot 3","Recon Bot 4","Recon Bot 5","Recon Bot 6","Recon Bot 7","Recon Bot 8","Recon Bot 9","Recon Bot 10","Recon Bot 11","Recon Bot 12","Recon Bot 13","Recon Bot 14","Recon Bot 15","Recon Bot 16","Recon Bot 17","Recon Bot 18","Recon Bot 19","Recon Bot 20","Recon Bot 21","Recon Bot 22","Recon Bot 23","Recon Bot 24","Recon Bot 25","Recon Bot 26","Recon Bot 27","Recon Bot 28","Recon Bot 29","Recon Bot 30","Recon Bot 31","Recon Bot 32","Recon Bot 33","Recon Bot 34","Recon Bot 35","Recon Bot 36","Recon Bot 37","Recon Bot 38","Recon Bot 39","Recon Bot 40","Recon Bot 41","Recon Bot 42","Recon Bot 43","Recon Bot 44","Recon Bot 45","Recon Bot 46","Recon Bot 47","Recon Bot 48","Recon Bot 49","Recon Bot 50","Recon Bot 51","Recon Bot 52","Recon Bot 53","Recon Bot 54","Recon Bot 55","Recon Bot 56","Recon Bot 57","Recon Bot 58","Recon Bot 59","Recon Bot 60","Recon Bot 61","Recon Bot 62","Recon Bot 63","Recon Bot 64","Recon Bot 65","Recon Bot 66","Recon Bot 67","Recon Bot 68","Recon Bot 69","Recon Bot 70","Recon Bot 71","Recon Bot 72","Recon Bot 73","Recon Bot 74","Recon Bot 75","Recon Bot 76","Recon Bot 77","Recon Bot 78","Recon Bot 79","Recon Bot 80","Recon Bot 81","Recon Bot 82","Recon Bot 83","Recon Bot 84","Recon Bot 85","Recon Bot 86","Recon Bot 87","Recon Bot 88","Recon Bot 89","Recon Bot 90","Recon Bot 91","Recon Bot 92","Recon Bot 93","Recon Bot 94","Recon Bot 95","Recon Bot 96","Recon Bot 97","Recon Bot 98","Recon Bot 99","Recon Bot 100","Recon Bot 101","Recon Bot 102","Recon Bot 103","Recon Bot 104","Recon Bot 105","Recon Bot 106","Recon Bot 107","Recon Bot 108","Recon Bot 109","Recon Bot 110","Recon Bot 111","Recon Bot 112","Recon Bot 113","Recon Bot 114","Recon Bot 115","Recon Bot 116","Recon Bot 117","Recon Bot 118","Recon Bot 119","Recon Bot 120","Recon Bot 121","Recon Bot 122","Recon Bot 123","Recon Bot 124","Recon Bot 125","Recon Bot 126","Recon Bot 127","Recon Bot 128","Recon Bot 129","Recon Bot 130","Recon Bot 131","Recon Bot 132","Recon Bot 133","Recon Bot 134","Recon Bot 135","Recon Bot 136","Recon Bot 137","Recon Bot 138","Recon Bot 139","Recon Bot 140","Recon Bot 141","Recon Bot 142","Recon Bot 143","Recon Bot 144","Recon Bot 145","Recon Bot 146","Recon Bot 147","Recon Bot 148","Recon Bot 149","Recon Bot 150","Recon Bot 151","Recon Bot 152","Recon Bot 153","Recon Bot 154","Recon Bot 155","Recon Bot 156","Recon Bot 157","Recon Bot 158","Recon Bot 159","Recon Bot 160","Recon Bot 161","Recon Bot 162","Recon Bot 163","Recon Bot 164","Recon Bot 165","Recon Bot 166","Recon Bot 167","Recon Bot 168","Recon Bot 169","Recon Bot 170","Recon Bot 171","Recon Bot 172","Recon Bot 173","Recon Bot 174","Recon Bot 175","Recon Bot 176","Recon Bot 177","Recon Bot 178","Recon Bot 179","Recon Bot 180","Recon Bot 181","Recon Bot 182","Recon Bot 183","Recon Bot 184","Recon Bot 185","Recon Bot 186","Recon Bot 187","Recon Bot 188","Recon Bot 189","Recon Bot 190","Recon Bot 191","Recon Bot 192","Recon Bot 193","Recon Bot 194","Recon Bot 195","Recon Bot 196","Recon Bot 197","Recon Bot 198","Recon Bot 199","Recon Bot 200","Recon Bot 201","Recon Bot 202","Recon Bot 203","Recon Bot 204","Recon Bot 205","Recon Bot 206","Recon Bot 207","Recon Bot 208","Recon Bot 209","Recon Bot 210","Recon Bot 211","Recon Bot 212","Recon Bot 213","Recon Bot 214","Recon Bot 215","Recon Bot 216","Recon Bot 217","Recon Bot 218","Recon Bot 219","Recon Bot 220","Recon Bot 221","Recon Bot 222","Recon Bot 223","Recon Bot 224","Recon Bot 225","Recon Bot 226","Recon Bot 227","Recon Bot 228","Recon Bot 229","Recon Bot 230","Recon Bot 231","Recon Bot 232","Recon Bot 233","Recon Bot 234","Recon Bot 235","Recon Bot 236","Recon Bot 237","Recon Bot 238","Recon Bot 239","Recon Bot 240","Recon Bot 241","Recon Bot 242","Recon Bot 243","Recon Bot 244","Recon Bot 245","Recon Bot 246","Recon Bot 247","Recon Bot 248","Recon Bot 249","Recon Bot 250","Recon Bot 251","Recon Bot 252","Recon Bot 253","Recon Bot 254","Recon Bot 255","Recon Bot 256","Recon Bot 257","Recon Bot 258","Recon Bot 259","Recon Bot 260","Recon Bot 261","Recon Bot 262","Recon Bot 263","Recon Bot 264","Recon Bot 265","Recon Bot 266","Recon Bot 267","Recon Bot 268","Recon Bot 269","Recon Bot 270","Recon Bot 271","Recon Bot 272","Recon Bot 273","Recon Bot 274","Recon Bot 275","Recon Bot 276","Recon Bot 277","Recon Bot 278","Recon Bot 279","Recon Bot 280","Recon Bot 281","Recon Bot 282","Recon Bot 283","Recon Bot 284","Recon Bot 285","Recon Bot 286","Recon Bot 287","Recon Bot 288","Recon Bot 289","Recon Bot 290","Recon Bot 291","Recon Bot 292","Recon Bot 293","Recon Bot 294","Recon Bot 295","Recon Bot 296","Recon Bot 297","Recon Bot 298","Recon Bot 299","Recon Bot 300","Recon Bot 301","Recon Bot 302","Recon Bot 303","Recon Bot 304","Recon Bot 305","Recon Bot 306","Recon Bot 307","Recon Bot 308","Recon Bot 309","Recon Bot 310","Recon Bot 311","Recon Bot 312","Recon Bot 313","Recon Bot 314","Recon Bot 315","Recon Bot 316","Recon Bot 317","Recon Bot 318","Recon Bot 319","Recon Bot 320","Recon Bot 321","Recon Bot 322","Recon Bot 323","Recon Bot 324","Recon Bot 325","Recon Bot 326","Recon Bot 327","Recon Bot 328","Recon Bot 329","Recon Bot 330","Recon Bot 331","Recon Bot 332","Recon Bot 333","Recon Bot 334","Recon Bot 335","Recon Bot 336","Recon Bot 337","Recon Bot 338","Recon Bot 339","Recon Bot 340","Recon Bot 341","Recon Bot 342","Recon Bot 343","Recon Bot 344","Recon Bot 345","Recon Bot 346","Recon Bot 347","Recon Bot 348","Recon Bot 349","Recon Bot 350","Recon Bot 351","Recon Bot 352","Recon Bot 353","Recon Bot 354","Recon Bot 355","Recon Bot 356","Recon Bot 357","Recon Bot 358","Recon Bot 359","Recon Bot 360","Recon Bot 361","Recon Bot 362","Recon Bot 363","Recon Bot 364","Recon Bot 365","Recon Bot 366","Recon Bot 367","Recon Bot 368","Recon Bot 369","Recon Bot 370","Recon Bot 371","Recon Bot 372","Recon Bot 373","Recon Bot 374","Recon Bot 375","Recon Bot 376","Recon Bot 377","Recon Bot 378","Recon Bot 379","Recon Bot 380","Recon Bot 381","Recon Bot 382","Recon Bot 383","Recon Bot 384","Recon Bot 385","Recon Bot 386","Recon Bot 387","Recon Bot 388","Recon Bot 389","Recon Bot 390","Recon Bot 391","Recon Bot 392","Recon Bot 393","Recon Bot 394","Recon Bot 395","Recon Bot 396","Recon Bot 397","Recon Bot 398","Recon Bot 399","Recon Bot 400","Recon Bot 401","Recon Bot 402","Recon Bot 403","Recon Bot 404","Recon Bot 405","Recon Bot 406","Recon Bot 407","Recon Bot 408","Recon Bot 409","Recon Bot 410","Recon Bot 411","Recon Bot 412","Recon Bot 413","Recon Bot 414","Recon Bot 415","Recon Bot 416","Recon Bot 417","Recon Bot 418","Recon Bot 419","Recon Bot 420","Recon Bot 421","Recon Bot 422","Recon Bot 423","Recon Bot 424","Recon Bot 425","Recon Bot 426","Recon Bot 427","Recon Bot 428","Recon Bot 429","Recon Bot 430","Recon Bot 431","Recon Bot 432","Recon Bot 433","Recon Bot 434","Recon Bot 435","Recon Bot 436","Recon Bot 437","Recon Bot 438","Recon Bot 439","Recon Bot 440","Recon Bot 441","Recon Bot 442","Recon Bot 443","Recon Bot 444","Recon Bot 445","Recon Bot 446","Recon Bot 447","Recon Bot 448","Recon Bot 449","Recon Bot 450","Recon Bot 451","Recon Bot 452","Recon Bot 453","Recon Bot 454","Recon Bot 455","Recon Bot 456","Recon Bot 457","Recon Bot 458","Recon Bot 459","Recon Bot 460","Recon Bot 461","Recon Bot 462","Recon Bot 463","Recon Bot 464","Recon Bot 465","Recon Bot 466","Recon Bot 467","Recon Bot 468","Recon Bot 469","Recon Bot 470","Recon Bot 471","Recon Bot 472","Recon Bot 473","Recon Bot 474","Recon Bot 475","Recon Bot 476","Recon Bot 477","Recon Bot 478","Recon Bot 479","Recon Bot 480","Recon Bot 481","Recon Bot 482","Recon Bot 483","Recon Bot 484","Recon Bot 485","Recon Bot 486","Recon Bot 487","Recon Bot 488","Recon Bot 489","Recon Bot 490","Recon Bot 491","Recon Bot 492","Recon Bot 493","Recon Bot 494","Recon Bot 495","Recon Bot 496","Recon Bot 497","Recon Bot 498","Recon Bot 499","Recon Bot 500","Recon Bot 501","Recon Bot 502","Recon Bot 503","Recon Bot 504","Recon Bot 505","Recon Bot 506","Recon Bot 507","Recon Bot 508","Recon Bot 509","Recon Bot 510","Recon Bot 511","Recon Bot 512","Recon Bot 513","Recon Bot 514","Recon Bot 515","Recon Bot 516","Recon Bot 517","Recon Bot 518","Recon Bot 519","Recon Bot 520","Recon Bot 521","Recon Bot 522","Recon Bot 523","Recon Bot 524","Recon Bot 525","Recon Bot 526","Recon Bot 527","Recon Bot 528","Recon Bot 529","Recon Bot 530","Recon Bot 531","Recon Bot 532","Recon Bot 533","Recon Bot 534","Recon Bot 535","Recon Bot 536","Recon Bot 537","Recon Bot 538","Recon Bot 539","Recon Bot 540","Recon Bot 541","Recon Bot 542","Recon Bot 543","Recon Bot 544","Recon Bot 545","Recon Bot 546","Recon Bot 547","Recon Bot 548","Recon Bot 549","Recon Bot 550","Recon Bot 551","Recon Bot 552","Recon Bot 553","Recon Bot 554","Recon Bot 555","Recon Bot 556","Recon Bot 557","Recon Bot 558","Recon Bot 559","Recon Bot 560","Recon Bot 561","Recon Bot 562","Recon Bot 563","Recon Bot 564","Recon Bot 565","Recon Bot 566","Recon Bot 567","Recon Bot 568","Recon Bot 569","Recon Bot 570","Recon Bot 571","Recon Bot 572","Recon Bot 573","Recon Bot 574","Recon Bot 575","Recon Bot 576","Recon Bot 577","Recon Bot 578","Recon Bot 579","Recon Bot 580","Recon Bot 581","Recon Bot 582","Recon Bot 583","Recon Bot 584","Recon Bot 585","Recon Bot 586","Recon Bot 587","Recon Bot 588","Recon Bot 589","Recon Bot 590","Recon Bot 591","Recon Bot 592","Recon Bot 593","Recon Bot 594","Recon Bot 595","Recon Bot 596","Recon Bot 597","Recon Bot 598","Recon Bot 599","Recon Bot 600","Recon Bot 601","Recon Bot 602","Recon Bot 603","Recon Bot 604","Recon Bot 605","Recon Bot 606","Recon Bot 607","Recon Bot 608","Recon Bot 609","Recon Bot 610","Recon Bot 611","Recon Bot 612","Recon Bot 613","Recon Bot 614","Recon Bot 615","Recon Bot 616","Recon Bot 617","Recon Bot 618","Recon Bot 619","Recon Bot 620","Recon Bot 621","Recon Bot 622","Recon Bot 623","Recon Bot 624","Recon Bot 625","Recon Bot 626","Recon Bot 627","Recon Bot 628","Recon Bot 629","Recon Bot 630","Recon Bot 631","Recon Bot 632","Recon Bot 633","Recon Bot 634","Recon Bot 635","Recon Bot 636","Recon Bot 637","Recon Bot 638","Recon Bot 639","Recon Bot 640","Recon Bot 641","Recon Bot 642","Recon Bot 643","Recon Bot 644","Recon Bot 645","Recon Bot 646","Recon Bot 647","Recon Bot 648","Recon Bot 649","Recon Bot 650","Recon Bot 651","Recon Bot 652","Recon Bot 653","Recon Bot 654","Recon Bot 655","Recon Bot 656","Recon Bot 657","Recon Bot 658","Recon Bot 659","Recon Bot 660","Recon Bot 661","Recon Bot 662","Recon Bot 663","Recon Bot 664","Recon Bot 665","Recon Bot 666","Recon Bot 667","Recon Bot 668","Recon Bot 669","Recon Bot 670","Recon Bot 671","Recon Bot 672","Recon Bot 673","Recon Bot 674","Recon Bot 675","Recon Bot 676","Recon Bot 677","Recon Bot 678","Recon Bot 679","Recon Bot 680","Recon Bot 681","Recon Bot 682","Recon Bot 683","Recon Bot 684","Recon Bot 685","Recon Bot 686","Recon Bot 687","Recon Bot 688","Recon Bot 689","Recon Bot 690","Recon Bot 691","Recon Bot 692","Recon Bot 693","Recon Bot 694","Recon Bot 695","Recon Bot 696","Recon Bot 697","Recon Bot 698","Recon Bot 699","Recon Bot 700","Recon Bot 701","Recon Bot 702","Recon Bot 703","Recon Bot 704","Recon Bot 705","Recon Bot 706","Recon Bot 707","Recon Bot 708","Recon Bot 709","Recon Bot 710","Recon Bot 711","Recon Bot 712","Recon Bot 713","Recon Bot 714","Recon Bot 715","Recon Bot 716","Recon Bot 717","Recon Bot 718","Recon Bot 719","Recon Bot 720","Recon Bot 721","Recon Bot 722","Recon Bot 723","Recon Bot 724","Recon Bot 725","Recon Bot 726","Recon Bot 727","Recon Bot 728","Recon Bot 729","Recon Bot 730","Recon Bot 731","Recon Bot 732","Recon Bot 733","Recon Bot 734","Recon Bot 735","Recon Bot 736","Recon Bot 737","Recon Bot 738","Recon Bot 739","Recon Bot 740","Recon Bot 741","Recon Bot 742","Recon Bot 743","Recon Bot 744","Recon Bot 745","Recon Bot 746","Recon Bot 747","Recon Bot 748","Recon Bot 749","Recon Bot 750","Recon Bot 751","Recon Bot 752","Recon Bot 753","Recon Bot 754","Recon Bot 755","Recon Bot 756","Recon Bot 757","Recon Bot 758","Recon Bot 759","Recon Bot 760","Recon Bot 761","Recon Bot 762","Recon Bot 763","Recon Bot 764","Recon Bot 765","Recon Bot 766","Recon Bot 767","Recon Bot 768","Recon Bot 769","Recon Bot 770","Recon Bot 771","Recon Bot 772","Recon Bot 773","Recon Bot 774","Recon Bot 775","Recon Bot 776","Recon Bot 777","Recon Bot 778","Recon Bot 779","Recon Bot 780","Recon Bot 781","Recon Bot 782","Recon Bot 783","Recon Bot 784","Recon Bot 785","Recon Bot 786","Recon Bot 787","Recon Bot 788","Recon Bot 789","Recon Bot 790","Recon Bot 791","Recon Bot 792","Recon Bot 793","Recon Bot 794","Recon Bot 795","Recon Bot 796","Recon Bot 797","Recon Bot 798","Recon Bot 799","Recon Bot 800","Recon Bot 801","Recon Bot 802","Recon Bot 803","Recon Bot 804","Recon Bot 805","Recon Bot 806","Recon Bot 807","Recon Bot 808","Recon Bot 809","Recon Bot 810","Recon Bot 811","Recon Bot 812","Recon Bot 813","Recon Bot 814","Recon Bot 815","Recon Bot 816","Recon Bot 817","Recon Bot 818","Recon Bot 819","Recon Bot 820","Recon Bot 821","Recon Bot 822","Recon Bot 823","Recon Bot 824","Recon Bot 825","Recon Bot 826","Recon Bot 827","Recon Bot 828","Recon Bot 829","Recon Bot 830","Recon Bot 831","Recon Bot 832","Recon Bot 833","Recon Bot 834","Recon Bot 835","Recon Bot 836","Recon Bot 837","Recon Bot 838","Recon Bot 839","Recon Bot 840","Recon Bot 841","Recon Bot 842","Recon Bot 843","Recon Bot 844","Recon Bot 845","Recon Bot 846","Recon Bot 847","Recon Bot 848","Recon Bot 849","Recon Bot 850","Recon Bot 851","Recon Bot 852","Recon Bot 853","Recon Bot 854","Recon Bot 855","Recon Bot 856","Recon Bot 857","Recon Bot 858","Recon Bot 859","Recon Bot 860","Recon Bot 861","Recon Bot 862","Recon Bot 863","Recon Bot 864","Recon Bot 865","Recon Bot 866","Recon Bot 867","Recon Bot 868","Recon Bot 869","Recon Bot 870","Recon Bot 871","Recon Bot 872","Recon Bot 873","Recon Bot 874","Recon Bot 875","Recon Bot 876","Recon Bot 877","Recon Bot 878","Recon Bot 879","Recon Bot 880","Recon Bot 881","Recon Bot 882","Recon Bot 883","Recon Bot 884","Recon Bot 885","Recon Bot 886","Recon Bot 887","Recon Bot 888","Recon Bot 889","Recon Bot 890","Recon Bot 891","Recon Bot 892","Recon Bot 893","Recon Bot 894","Recon Bot 895","Recon Bot 896","Recon Bot 897","Recon Bot 898","Recon Bot 899","Recon Bot 900","Recon Bot 901","Recon Bot 902","Recon Bot 903","Recon Bot 904","Recon Bot 905","Recon Bot 906","Recon Bot 907","Recon Bot 908","Recon Bot 909","Recon Bot 910","Recon Bot 911","Recon Bot 912","Recon Bot 913","Recon Bot 914","Recon Bot 915","Recon Bot 916","Recon Bot 917","Recon Bot 918","Recon Bot 919","Recon Bot 920","Recon Bot 921","Recon Bot 922","Recon Bot 923","Recon Bot 924","Recon Bot 925","Recon Bot 926","Recon Bot 927","Recon Bot 928","Recon Bot 929","Recon Bot 930","Recon Bot 931","Recon Bot 932","Recon Bot 933","Recon Bot 934","Recon Bot 935","Recon Bot 936","Recon Bot 937","Recon Bot 938","Recon Bot 939","Recon Bot 940","Recon Bot 941","Recon Bot 942","Recon Bot 943","Recon Bot 944","Recon Bot 945","Recon Bot 946","Recon Bot 947","Recon Bot 948","Recon Bot 949","Recon Bot 950","Recon Bot 951","Recon Bot 952","Recon Bot 953","Recon Bot 954","Recon Bot 955","Recon Bot 956","Recon Bot 957","Recon Bot 958","Recon Bot 959","Recon Bot 960","Recon Bot 961","Recon Bot 962","Recon Bot 963","Recon Bot 964","Recon Bot 965","Recon Bot 966","Recon Bot 967","Recon Bot 968","Recon Bot 969","Recon Bot 970","Recon Bot 971","Recon Bot 972","Recon Bot 973","Recon Bot 974","Recon Bot 975","Recon Bot 976","Recon Bot 977","Recon Bot 978","Recon Bot 979","Recon Bot 980","Recon Bot 981","Recon Bot 982","Recon Bot 983","Recon Bot 984","Recon Bot 985","Recon Bot 986","Recon Bot 987","Recon Bot 988","Recon Bot 989","Recon Bot 990","Recon Bot 991","Recon Bot 992","Recon Bot 993","Recon Bot 994","Recon Bot 995","Recon Bot 996","Recon Bot 997","Recon Bot 998","Recon Bot 999","Recon Bot 1000"
errordiff = 'errors.com.epicgames.common.throttled', 'errors.com.epicgames.friends.inviter_friendships_limit_exceeded'
__version__ = "2.5"

with open('info.json') as f:
    try:
        info = json.load(f)
    except json.decoder.JSONDecodeError as e:
        print(Fore.RED + ' [ERROR] ' + Fore.RESET + "")
        print(Fore.LIGHTRED_EX + f'\n {e}')
        exit(1)

def is_admin():
    async def predicate(ctx):
        return ctx.author.display_name in info['FullAccess']
    return commands.check(predicate)

prefix = '!','?','/','',' '

@sanic_app.route('/', methods=['GET'])
async def root(request: sanic.request.Request) -> None:
    if 'Accept' in request.headers and request.headers['Accept'] == 'application/json':
        return sanic.response.json(
            {
                "status": "online"
            }
        )

    return sanic.response.html(
        """
<html>
   <head>
      <style>
         body {
         font-family: Arial, Helvetica, sans-serif;
         position: absolute;
         left: 50%;
         top: 50%;  
         -webkit-transform: translate(-50%, -50%);
         transform: translate(-50%, -50%);
         background-repeat: no-repeat;
         background-attachment: fixed;
         background-size: cover;
         }
      </style>
   </head>
   <body>
      <center>
         <h2 id="response">
            """ + f"""Online now {name}""" + """
            <h2>
            """ + f"""Total Friends: {friend}/1000""" + """
            </h2>
            <h2>
            """ + f"""💎 Version {__version__} 💎""" + """
            </h2>
         </h2>
      </center>
   </body>
   <script>
   <script>
      var isInIframe = (parent !== window), parentUrl = null;
      var repl_url = "";
      
      if (isInIframe) {
        var currentIframeHref = new URL(document.location.href);
        repl_url = currentIframeHref.origin + decodeURIComponent(currentIframeHref.pathname);
      } else {
        repl_url = location.href;
      }
      
      console.log(repl_url)
      
      var text = document.getElementById('response');
      var xhr = new XMLHttpRequest();
      
      xhr.open("POST", "https://partybot.net/api/upload-repl-url", false);
      xhr.send(JSON.stringify({ url: repl_url }));
      
      var data = JSON.parse(xhr.responseText);
      
      if (data.message) {
          text.innerHTML = data.message
      }
      else {
          text.innerHTML = data.error
      }
      // text.innerHTML = JSON.stringify(data, null, 4)
   </script>
</html>
        """
    )


@sanic_app.route('/ping', methods=['GET'])
async def accept_ping(request: sanic.request.Request) -> None:
    return sanic.response.json(
        {
            "status": "online"
        }
    )


@sanic_app.route('/name', methods=['GET'])
async def display_name(request: sanic.request.Request) -> None:
    return sanic.response.json(
        {
            "display_name": name
        }
    )


class SekkayBot(commands.Bot):
    def __init__(self, device_id: str, account_id: str, secret: str, **kwargs) -> None:
        self.status = '📛 {party_size}/16 | /1000 Friends 📛'
        
        self.fortnite_api = FortniteAPIAsync.APIClient()
        self.loop = asyncio.get_event_loop()

        super().__init__(
            command_prefix=prefix,
            case_insensitive=True,
            auth=fortnitepy.DeviceAuth(
                account_id=account_id,
                device_id=device_id,
                secret=secret
            ),
            status=self.status,
            platform=fortnitepy.Platform('PSN'),
            **kwargs
        )

        self.session = aiohttp.ClientSession()

        self.default_skin = "CID_A_190_Athena_Commando_M_AlienAgent"
        self.default_backpack = "BID_833_TieDyeFashion"
        self.default_pickaxe = "Pickaxe_Lockjaw"
        self.banner = "otherbanner51"
        self.banner_colour = "defaultcolor22"
        self.default_level = 1000
        self.default_bp_tier = 1000

        self.sanic_app = sanic_app
        self.server = server
        self.invite_message = ''
        self.request_message = ''
        self.welcome_message =  "WELCOME {DISPLAY_NAME} !\nUse Code : 'LiLi' (#ad)\nUse Code : 'LiLi' (#ad)\nUse Code : 'LiLi' (#ad)" 

    async def set_and_update_party_prop(self, schema_key: str, new_value: Any) -> None:
        prop = {schema_key: self.party.me.meta.set_prop(schema_key, new_value)}

        await self.party.patch(updated=prop)

    async def welcome_change(self) -> None:
        await asyncio.sleep(1800)
        self.welcome_message =  "WELCOME {DISPLAY_NAME} !\nUse Code : 'POTE' (#ads)\nUse Code : 'POTE' (#ads)\nUse Code : 'POTE' (#ads)"
        await asyncio.sleep(10)
        await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
        await asyncio.sleep(1800)
        self.welcome_message =  "WELCOME {DISPLAY_NAME} !\nUse Code : 'LiLi' (#ads)\nUse Code : 'LiLi' (#ads)\nUse Code : 'LiLi' (#ads)"
        await asyncio.sleep(10)
        await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
        self.loop.create_task(self.welcome_change())

    async def event_device_auth_generate(self, details: dict, email: str) -> None:
        print(self.user.display_name)

    async def add_list(self) -> None:
        try:
            await self.add_friend('634808aa909644c590c774488cadecb8')
        except: pass    

    async def event_ready(self) -> None:
        global name
        global friend

        name = self.user.display_name
        friend = len(self.friends)

        print(crayons.green(f'Client ready as {self.user.display_name}.'))

        self.loop.create_task(self.status_change())
        self.loop.create_task(self.add_list())

        coro = self.sanic_app.create_server(
            host='0.0.0.0',
            port=8000,
            return_asyncio_server=True,
            access_log=False
        )
        self.server = await coro
        
        self.loop.create_task(self.update_settings())
        self.loop.create_task(self.check_update())
        self.loop.create_task(self.welcome_change())

        for pending in self.incoming_pending_friends:
            try:
                epic_friend = await pending.accept() 
                if isinstance(epic_friend, fortnitepy.Friend):
                    print(f"Accepted friend request from: {epic_friend.display_name}.")
                else:
                    print(f"Declined friend request from: {pending.display_name}.")
            except fortnitepy.HTTPException as epic_error:
                if epic_error.message_code in errordiff:
                    raise

                await asyncio.sleep(int(epic_error.message_vars[0] + 1))
                await pending.decline()

#///////////////////////////////////////////////////////////////////////////////////////////////////////////// CHECK/ERROR/PARTY ////////////////////////////////////////////////////////////////////////////////////////////////////////

    async def check_party_validity(self):
        await asyncio.sleep(80)
        await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
        await asyncio.sleep(80)

#///////////////////////////////////////////////////////////////////////////////////////////////////////////// PARTY/INVITE ////////////////////////////////////////////////////////////////////////////////////////////////////////            

    async def event_party_invite(self, invite: fortnitepy.ReceivedPartyInvitation) -> None:
        if invite.sender.display_name in info['FullAccess']:
            await invite.accept()
        elif invite.sender.display_name in admin:
            await invite.accept()    
        else:
            await invite.decline()
            await invite.sender.send(self.invite_message)
            await invite.sender.invite()

#///////////////////////////////////////////////////////////////////////////////////////////////////////////// CHECK/FRIENDS/ADD ////////////////////////////////////////////////////////////////////////////////////////////////////////            

#///////////////////////////////////////////////////////////////////////////////////////////////////////////// FRIENDS/ADD ////////////////////////////////////////////////////////////////////////////////////////////////////////

    async def update_settings(self) -> None:
        while True:
            async with self.session.request(
                method="GET",
                url="https://cdn.teampnglol.repl.co/default.json"
            ) as r:
                data = await r.json()

                if r.status == 200:
                    self.default_skin = data['default_skin']
                    self.default_backpack = data['default_backpack']
                    self.default_pickaxe = data['default_pickaxe']
                    self.banner = data['banner']
                    self.banner_colour = data['banner_colour']
                    self.default_level = data['default_level']
                    self.default_bp_tier = data['default_bp_tier']
                    await self.party.me.set_outfit(asset=self.default_skin)
                    await self.party.set_privacy(fortnitepy.PartyPrivacy.PRIVATE)
                    await asyncio.sleep(0.1)
                    await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            print('Load Stuff')        
            await asyncio.sleep(3600)

    async def check_update(self):
        await asyncio.sleep(1200)
        self.loop.create_task(self.update_settings())
        await asyncio.sleep(1200)
        self.loop.create_task(self.check_update())

    async def status_change(self) -> None:
        await self.set_presence('📛 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 📛')
        self.loop.create_task(self.verify())
        await asyncio.sleep(20)
        await self.party.set_privacy(fortnitepy.PartyPrivacy.PRIVATE)
        await asyncio.sleep(0.1)
        await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

    async def event_friend_request(self, request: Union[(fortnitepy.IncomingPendingFriend, fortnitepy.OutgoingPendingFriend)]) -> None:
        try:    
            await request.accept()
            self.loop.create_task(self.verify())
            await self.set_presence('📛 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 📛')
            await self.party.set_privacy(fortnitepy.PartyPrivacy.PRIVATE)
            await asyncio.sleep(0.1)
            await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
        except: pass        

    async def event_friend_add(self, friend: fortnitepy.Friend) -> None:
        try:
            await friend.send(self.request_message.replace('{DISPLAY_NAME}', friend.display_name))
            await friend.invite()
            self.loop.create_task(self.verify())
        except: pass

    async def event_friend_remove(self, friend: fortnitepy.Friend) -> None:
        try:
            await self.add_friend(friend.id)
        except: pass

    async def event_party_member_join(self, member: fortnitepy.PartyMember) -> None:
        await self.party.send(self.welcome_message.replace('{DISPLAY_NAME}', member.display_name))

        if self.default_party_member_config.cls is not fortnitepy.party.JustChattingClientPartyMember:
            await self.party.me.edit(functools.partial(self.party.me.set_outfit,self.default_skin,variants=self.party.me.create_variants(material=3)),functools.partial(self.party.me.set_backpack,self.default_backpack),functools.partial(self.party.me.set_pickaxe,self.default_pickaxe),functools.partial(self.party.me.set_banner,icon=self.banner,color=self.banner_colour,season_level=self.default_level),functools.partial(self.party.me.set_battlepass_info,has_purchased=True,level=self.default_bp_tier))

            if not self.has_friend(member.id):
                try:
                    await self.add_friend(member.id)
                except: pass  

            if member.display_name in banned_player:
                try:
                    await member.kick()
                except: pass

    async def event_party_member_leave(self, member) -> None:
        if not self.has_friend(member.id):
            try:
                await self.add_friend(member.id)
            except: pass

#///////////////////////////////////////////////////////////////////////////////////////////////////////////// PARTY/FRIENDS MESSAGE ////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    async def event_party_message(self, message) -> None:
        print(Fore.LIGHTBLUE_EX + f' [Party] ' + f'{message.author.display_name}: {message.content}')

        if not self.has_friend(message.author.id):
            try:
                await self.add_friend(message.author.id)
            except: pass

    async def event_friend_message(self, message: fortnitepy.FriendMessage) -> None:
        print(Fore.MAGENTA + f' [Friend] ' + f'{message.author.display_name}: {message.content}')

        if not message.author.display_name != 'Sekkay Bot':
            await self.party.invite(message.author.id)
        
    async def event_party_message(self, message: fortnitepy.FriendMessage) -> None:
        if message.content == 'salut':
            await self.party.send('Ca va?')
        elif message.content == 'Oui et toi':
            await self.party.send('Ca va Trkl mon gars')

#///////////////////////////////////////////////////////////////////////////////////////////////////////////// COMMANDS ////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    async def event_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, IndexError):
            pass
        elif isinstance(error, fortnitepy.HTTPException):
            pass
        elif isinstance(error, commands.CheckFailure):
            pass
        elif isinstance(error, TimeoutError):
            pass
        else:
            print(error)

#///////////////////////////////////////////////////////////////////////////////////////////////////////////// COSMETICS ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

    @commands.command(aliases=['outfit', 'character'])
    async def skin(self, ctx: fortnitepy.ext.commands.Context, *, content = None) -> None:
        if content is None:
            await ctx.send()
        elif content.lower() == 'pinkghoul':    
            await self.party.me.set_outfit(asset='CID_029_Athena_Commando_F_Halloween',variants=self.party.me.create_variants(material=3))
        elif content.lower() == 'ghoul':    
            await self.party.me.set_outfit(asset='CID_029_Athena_Commando_F_Halloween',variants=self.party.me.create_variants(material=3))     
        elif content.lower() == 'pkg':  
            await self.party.me.set_outfit(asset='CID_029_Athena_Commando_F_Halloween',variants=self.party.me.create_variants(material=3))
        elif content.lower() == 'colora':   
            await self.party.me.set_outfit(asset='CID_434_Athena_Commando_F_StealthHonor')
        elif content.lower() == 'pink ghoul':   
            await self.party.me.set_outfit(asset='CID_029_Athena_Commando_F_Halloween',variants=self.party.me.create_variants(material=3))
        elif content.lower() == 'nikeu mouk':
            await self.party.me.set_outfit(asset='CID_028_Athena_Commando_F',variants=self.party.me.create_variants(material=2))  
        elif content.lower() == 'renegade': 
            await self.party.me.set_outfit(asset='CID_028_Athena_Commando_F',variants=self.party.me.create_variants(material=2))
        elif content.lower() == 'caca':   
            await self.party.me.set_outfit(asset='CID_028_Athena_Commando_F',variants=self.party.me.create_variants(material=2))        
        elif content.lower() == 'rr':   
            await self.party.me.set_outfit(asset='CID_028_Athena_Commando_F',variants=self.party.me.create_variants(material=2))
        elif content.lower() == 'skull trooper':    
            await self.party.me.set_outfit(asset='CID_030_Athena_Commando_M_Halloween',variants=self.party.me.create_variants(clothing_color=1))
        elif content.lower() == 'skl':  
            await self.party.me.set_outfit(asset='CID_030_Athena_Commando_M_Halloween',variants=self.party.me.create_variants(clothing_color=1))
        elif content.lower() == 'honor':    
            await self.party.me.set_outfit(asset='CID_342_Athena_Commando_M_StreetRacerMetallic') 
        else:
            try:
                cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(lang="en",searchLang="en",matchMethod="contains",name=content,backendType="AthenaCharacter")
                await self.party.me.set_outfit(asset=cosmetic.id)
                await ctx.send(f'Skin set to {cosmetic.name}.')

            except FortniteAPIAsync.exceptions.NotFound:
                pass
            
    @commands.command()
    async def backpack(self, ctx: fortnitepy.ext.commands.Context, *, content: str) -> None:
        try:
            cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(lang="en",searchLang="en",matchMethod="contains",name=content,backendType="AthenaBackpack")
            await self.party.me.set_backpack(asset=cosmetic.id)
            await ctx.send(f'Backpack set to {cosmetic.name}.')

        except FortniteAPIAsync.exceptions.NotFound:
            pass
        
    @commands.command(aliases=['dance'])
    async def emote(self, ctx: fortnitepy.ext.commands.Context, *, content = None) -> None:
        if content is None:
            await ctx.send()
        elif content.lower() == 'sce':
            await self.party.me.set_emote(asset='EID_KpopDance03')
        elif content.lower() == 'Sce':
            await self.party.me.set_emote(asset='EID_KpopDance03')    
        elif content.lower() == 'scenario':
            await self.party.me.set_emote(asset='EID_KpopDance03')
        elif content.lower() == 'Scenario':
            await self.party.me.set_emote(asset='EID_KpopDance03')     
        else:
            try:
                cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(lang="en",searchLang="en",matchMethod="contains",name=content,backendType="AthenaDance")
                await self.party.me.clear_emote()
                await self.party.me.set_emote(asset=cosmetic.id)
                await ctx.send(f'Emote set to {cosmetic.name}.')

            except FortniteAPIAsync.exceptions.NotFound:
                pass    
              
    @commands.command()
    async def rdm(self, ctx: fortnitepy.ext.commands.Context, cosmetic_type: str = 'skin') -> None:
        if cosmetic_type == 'skin':
            all_outfits = await self.fortnite_api.cosmetics.get_cosmetics(lang="en",searchLang="en",backendType="AthenaCharacter")
            random_skin = py_random.choice(all_outfits).id
            await self.party.me.set_outfit(asset=random_skin,variants=self.party.me.create_variants(profile_banner='ProfileBanner'))
            await ctx.send(f'Skin randomly set to {random_skin}.')
        elif cosmetic_type == 'emote':
            all_emotes = await self.fortnite_api.cosmetics.get_cosmetics(lang="en",searchLang="en",backendType="AthenaDance")
            random_emote = py_random.choice(all_emotes).id
            await self.party.me.set_emote(asset=random_emote)
            await ctx.send(f'Emote randomly set to {random_emote.name}.')
            
    @commands.command()
    async def pickaxe(self, ctx: fortnitepy.ext.commands.Context, *, content: str) -> None:
        try:
            cosmetic = await self.fortnite_api.cosmetics.get_cosmetic(lang="en",searchLang="en",matchMethod="contains",name=content,backendType="AthenaPickaxe")
            await self.party.me.set_pickaxe(asset=cosmetic.id)
            await ctx.send(f'Pickaxe set to {cosmetic.name}.')

        except FortniteAPIAsync.exceptions.NotFound:
            pass

    @commands.command(aliases=['news'])
    @commands.cooldown(1, 10)
    async def new(self, ctx: fortnitepy.ext.commands.Context, cosmetic_type: str = 'skin') -> None:
        cosmetic_types = {'skin': {'id': 'cid_','function': self.party.me.set_outfit},'backpack': {'id': 'bid_','function': self.party.me.set_backpack},'emote': {'id': 'eid_','function': self.party.me.set_emote},}

        if cosmetic_type not in cosmetic_types:
            return await ctx.send('Invalid cosmetic type, valid types include: skin, backpack & emote.')

        new_cosmetics = await self.fortnite_api.cosmetics.get_new_cosmetics()

        for new_cosmetic in [new_id for new_id in new_cosmetics if
                             new_id.id.lower().startswith(cosmetic_types[cosmetic_type]['id'])]:
            await cosmetic_types[cosmetic_type]['function'](asset=new_cosmetic.id)

            await ctx.send(f"{cosmetic_type}s set to {new_cosmetic.name}.")

            await asyncio.sleep(3)

        await ctx.send(f'Finished equipping all new unencrypted {cosmetic_type}s.')           

    @commands.command()
    async def purpleskull(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(asset='CID_030_Athena_Commando_M_Halloween',variants=self.party.me.create_variants(clothing_color=1))
        await ctx.send(f'Skin set to Purple Skull Trooper!')
        
    @commands.command()
    async def pinkghoul(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(asset='CID_029_Athena_Commando_F_Halloween',variants=self.party.me.create_variants(material=3))
        await ctx.send('Skin set to Pink Ghoul Trooper!')
        
    @commands.command(aliases=['checkeredrenegade','raider'])
    async def renegade(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(asset='CID_028_Athena_Commando_F',variants=self.party.me.create_variants(material=2))
        await ctx.send('Skin set to Checkered Renegade!')
        
    @commands.command()
    async def aerial(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(asset='CID_017_Athena_Commando_M')
        await ctx.send('Skin set to aerial!')
        
    @commands.command()
    async def hologram(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_outfit(asset='CID_VIP_Athena_Commando_M_GalileoGondola_SG')
        await ctx.send('Skin set to Star Wars Hologram!')  

    @commands.command()
    async def cid(self, ctx: fortnitepy.ext.commands.Context, character_id: str) -> None:
        await self.party.me.set_outfit(asset=character_id,variants=self.party.me.create_variants(profile_banner='ProfileBanner'))
        await ctx.send(f'Skin set to {character_id}.')
        
    @commands.command()
    async def eid(self, ctx: fortnitepy.ext.commands.Context, emote_id: str) -> None:
        await self.party.me.clear_emote()
        await self.party.me.set_emote(asset=emote_id)
        await ctx.send(f'Emote set to {emote_id}!')
        
    @commands.command()
    async def bid(self, ctx: fortnitepy.ext.commands.Context, backpack_id: str) -> None:
        await self.party.me.set_backpack(asset=backpack_id)
        await ctx.send(f'Backbling set to {backpack_id}!')
        
    @commands.command()
    async def stop(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.clear_emote()
        await ctx.send('Stopped emoting.')
        
    @commands.command()
    async def point(self, ctx: fortnitepy.ext.commands.Context, *, content: Optional[str] = None) -> None:
        await self.party.me.clear_emote()
        await self.party.me.set_emote(asset='EID_IceKing')
        await ctx.send(f'Pickaxe set & Point it Out played.')
        

    copied_player = ""


    @commands.command()
    async def stop(self, ctx: fortnitepy.ext.commands.Context):
        global copied_player
        if copied_player != "":
            copied_player = ""
            await ctx.send(f'Stopped copying all users.')
            await self.party.me.clear_emote()
            return
        else:
            try:
                await self.party.me.clear_emote()
            except RuntimeWarning:
                pass

    @commands.command(aliases=['clone', 'copi', 'cp'])
    async def copy(self, ctx: fortnitepy.ext.commands.Context, *, epic_username = None) -> None:
        global copied_player

        if epic_username is None:
            user = await self.fetch_user(ctx.author.display_name)
            member = self.party.get_member(user.id)

        elif 'stop' in epic_username:
            copied_player = ""
            await ctx.send(f'Stopped copying all users.')
            await self.party.me.clear_emote()
            return

        elif epic_username is not None:
            try:
                user = await self.fetch_user(epic_username)
                member = self.party.get_member(user.id)
            except AttributeError:
                await ctx.send("Could not get that user.")
                return
        try:
            copied_player = member
            await self.party.me.edit_and_keep(partial(fortnitepy.ClientPartyMember.set_outfit,asset=member.outfit,variants=member.outfit_variants),partial(fortnitepy.ClientPartyMember.set_pickaxe,asset=member.pickaxe,variants=member.pickaxe_variants))
            await ctx.send(f"Now copying: {member.display_name}")
        except AttributeError:
            await ctx.send("Could not get that user.")

    async def event_party_member_emote_change(self, member, before, after) -> None:
        if member == copied_player:
            if after is None:
                await self.party.me.clear_emote()
            else:
                await self.party.me.edit_and_keep(partial(fortnitepy.ClientPartyMember.set_emote,asset=after))                        
                
    async def event_party_member_outfit_change(self, member, before, after) -> None:
        if member == copied_player:
            await self.party.me.edit_and_keep(partial(fortnitepy.ClientPartyMember.set_outfit,asset=member.outfit,variants=member.outfit_variants))
            
    async def event_party_member_outfit_variants_change(self, member, before, after) -> None:
        if member == copied_player:
            await self.party.me.edit_and_keep(partial(fortnitepy.ClientPartyMember.set_outfit,variants=member.outfit_variants))
            
#///////////////////////////////////////////////////////////////////////////////////////////////////////////// PARTY/FRIENDS/ADMIN //////////////////////////////////////////////////////////////////////////////////////////////////////

    @commands.command()
    async def add(self, ctx: fortnitepy.ext.commands.Context, *, epic_username: str) -> None:
        user = await self.fetch_user(epic_username)
        friends = self.friends

        if user.id in friends:
            await ctx.send(f'I already have {user.display_name} as a friend')
        else:
            await self.add_friend(user.id)
            await ctx.send(f'Send i friend request to {user.display_name}.')

    @is_admin()
    @commands.command()
    async def restart(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await ctx.send(f'im Restart now')
        python = sys.executable
        os.execl(python, python, *sys.argv)        

    @is_admin()
    @commands.command()
    async def set(self, ctx: fortnitepy.ext.commands.Context, nombre: int) -> None:
        await self.party.set_max_size(nombre)
        await ctx.send(f'Set party to {nombre} player can join')
        
    @commands.command()
    async def ready(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_ready(fortnitepy.ReadyState.READY)
        await ctx.send('Ready!')
    
    @commands.command(aliases=['sitin'],)
    async def unready(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_ready(fortnitepy.ReadyState.NOT_READY)
        await ctx.send('Unready!')
        
    @commands.command()
    async def level(self, ctx: fortnitepy.ext.commands.Context, banner_level: int) -> None:
        await self.party.me.set_banner(season_level=banner_level)
        await ctx.send(f'Set level to {banner_level}.')
        
    @is_admin()
    @commands.command()
    async def sitout(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.set_ready(fortnitepy.ReadyState.SITTING_OUT)
        await ctx.send('Sitting Out!')
            
    @is_admin()
    @commands.command()
    async def leave(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.party.me.leave()
        await ctx.send(f'i Leave')
        await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

    @is_admin()
    @commands.command()
    async def v(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await ctx.send(f'the version {__version__}')

    @is_admin()
    @commands.command()
    async def kick(self, ctx: fortnitepy.ext.commands.Context, *, epic_username: Optional[str] = None) -> None:
        if epic_username is None:
            user = await self.fetch_user(ctx.author.display_name)
            member = self.party.get_member(user.id)
        else:
            user = await self.fetch_user(epic_username)
            member = self.party.get_member(user.id)

        if member is None:
            await ctx.send("Failed to find that user, are you sure they're in the party?")
        else:
            try:
                if not member.display_name in info['FullAccess']:
                    await member.kick()
                    await ctx.send(f"Kicked user: {member.display_name}.")
            except fortnitepy.errors.Forbidden:
                await ctx.send(f"Failed to kick {member.display_name}, as I'm not party leader.")

    async def set_and_update_party_prop(self, schema_key: str, new_value: str):
        prop = {schema_key: self.party.me.meta.set_prop(schema_key, new_value)}

        await self.party.patch(updated=prop)

    @commands.party_only()
    @commands.command(name='- HEY',aliases=['-HEY','Youtube:','Use','Item','Notice:','This','Heyy','If'], hidden=True)
    async def kickortherbots(self, ctx: fortnitepy.ext.commands.Context, *, username = None):
        if self.party.me.leader:
            user = await self.fetch_profile(ctx.author.id)
            member = self.party.get_member(user.id)

        if not member.display_name in info['FullAccess']:
            await member.kick()
            await ctx.send("The orther Bot is Not accepted of the party")
        else:
            await ctx.send()

    @is_admin()
    @commands.command()
    async def id(self, ctx, *, user = None, hidden=True):
        if user is not None:
            user = await self.fetch_profile(user)
        
        elif user is None:
            user = await self.fetch_profile(ctx.message.author.id)
        try:
            await ctx.send(f"{user}'s Epic ID is: {user.id}")
            print(Fore.GREEN + ' [+] ' + Fore.RESET + f"{user}'s Epic ID is: " + Fore.LIGHTBLACK_EX + f'{user.id}')
        except AttributeError:
            await ctx.send("I couldn't find an Epic account with that name.")

    @is_admin()
    @commands.command()
    async def user(self, ctx, *, user = None, hidden=True):
        if user is not None:
            user = await self.fetch_profile(user)
            try:
                await ctx.send(f"The ID: {user.id} belongs to: {user.display_name}")
                print(Fore.GREEN + ' [+] ' + Fore.RESET + f'The ID: {user.id} belongs to: ' + Fore.LIGHTBLACK_EX + f'{user.display_name}')
            except AttributeError:
                await ctx.send(f"I couldn't find a user that matches that ID")
        else:
            await ctx.send(f'No ID was given. Try: {prefix}user (ID)')

    async def invitefriends(self):
        send = []
        for friend in self.friends:
            if friend.is_online():
                send.append(friend.display_name)
                await friend.invite()
                print(f'[=] {friend.display_name} was send')

        for ctz in self.friends:
            if not ctz.display_name != "Sekkay Bot":
                if ctz.is_online():
                    await ctz.send('finit de inviter')

    @is_admin()
    @commands.command()
    async def invite(self, ctx: fortnitepy.ext.commands.Context) -> None:
        try:
            self.loop.create_task(self.invitefriends())
        except Exception:
            pass       

    @commands.command(aliases=['friends'],)
    async def epicfriends2(self, ctx: fortnitepy.ext.commands.Context) -> None:
        onlineFriends = []
        offlineFriends = []

        try:
            for friend in self.friends:
                if friend.is_online():
                    onlineFriends.append(friend.display_name)
                else:
                    offlineFriends.append(friend.display_name)
            
            await ctx.send(f"Total Friends: {len(self.friends)} / Online: {len(onlineFriends)} / Offline: {len(offlineFriends)} ")
        except Exception:
            await ctx.send(f'Not work')

    @is_admin()
    @commands.command()
    async def whisper(self, ctx: fortnitepy.ext.commands.Context, message = None) -> None:
        try:
            for friend in self.friends:
                if friend.is_online():
                    await friend.send(message)

            await ctx.send(f'Send friend message to everyone')
            
        except: pass

    @commands.command()
    async def say(self, ctx: fortnitepy.ext.commands.Context, *, message = None):
        if message is not None:
            await self.party.send(message)
            await ctx.send(f'Sent "{message}" to party chat')
        else:
            await ctx.send(f'No message was given. Try: {prefix} say (message)')

    @commands.command()
    async def cousin(self, ctx: fortnitepy.ext.commands.Context):
        await ctx.send('create by cousin')

    @is_admin()
    @commands.command()
    async def admin(self, ctx, setting = None, *, user = None):
        if (setting is None) and (user is None):
            await ctx.send(f"Missing one or more arguments. Try: {prefix} admin (add, remove, list) (user)")
        elif (setting is not None) and (user is None):

            user = await self.fetch_profile(ctx.message.author.id)

            if setting.lower() == 'add':
                if user.display_name in info['FullAccess']:
                    await ctx.send("You are already an admin")

                else:
                    await ctx.send("Password?")
                    response = await self.wait_for('friend_message', timeout=20)
                    content = response.content.lower()
                    if content == password:
                        info['FullAccess'].append(user.display_name)
                        with open('info.json', 'w') as f:
                            json.dump(info, f, indent=4)
                            await ctx.send(f"Correct. Added {user.display_name} as an admin.")
                            print(Fore.GREEN + " [+] " + Fore.LIGHTGREEN_EX + user.display_name + Fore.RESET + " was added as an admin.")
                    else:
                        await ctx.send("Incorrect Password.")

            elif setting.lower() == 'remove':
                if user.display_name not in info['FullAccess']:
                    await ctx.send("You are not an admin.")
                else:
                    await ctx.send("Are you sure you want to remove yourself as an admin?")
                    response = await self.wait_for('friend_message', timeout=20)
                    content = response.content.lower()
                    if (content.lower() == 'yes') or (content.lower() == 'y'):
                        info['FullAccess'].remove(user.display_name)
                        with open('info.json', 'w') as f:
                            json.dump(info, f, indent=4)
                            await ctx.send("You were removed as an admin.")
                            print(Fore.BLUE + " [+] " + Fore.LIGHTBLUE_EX + user.display_name + Fore.RESET + " was removed as an admin.")
                    elif (content.lower() == 'no') or (content.lower() == 'n'):
                        await ctx.send("You were kept as admin.")
                    else:
                        await ctx.send("Not a correct reponse. Cancelling command.")
                    
            elif setting == 'list':
                if user.display_name in info['FullAccess']:
                    admins = []

                    for admin in info['FullAccess']:
                        user = await self.fetch_profile(admin)
                        admins.append(user.display_name)

                    await ctx.send(f"The bot has {len(admins)} admins:")

                    for admin in admins:
                        await ctx.send(admin)

                else:
                    await ctx.send("You don't have permission to this command.")

            else:
                await ctx.send(f"That is not a valid setting. Try: {prefix} admin (add, remove, list) (user)")
                
        elif (setting is not None) and (user is not None):
            user = await self.fetch_profile(user)

            if setting.lower() == 'add':
                if ctx.message.author.display_name in info['FullAccess']:
                    if user.display_name not in info['FullAccess']:
                        info['FullAccess'].append(user.display_name)
                        with open('info.json', 'w') as f:
                            json.dump(info, f, indent=4)
                            await ctx.send(f"Correct. Added {user.display_name} as an admin.")
                            print(Fore.GREEN + " [+] " + Fore.LIGHTGREEN_EX + user.display_name + Fore.RESET + " was added as an admin.")
                    else:
                        await ctx.send("That user is already an admin.")
                else:
                    await ctx.send("You don't have access to add other people as admins. Try just: !admin add")
            elif setting.lower() == 'remove':
                if ctx.message.author.display_name in info['FullAccess']:
                    if user.display_name in info['FullAccess']:
                        await ctx.send("Password?")
                        response = await self.wait_for('friend_message', timeout=20)
                        content = response.content.lower()
                        if content == password:
                            info['FullAccess'].remove(user.display_name)
                            with open('info.json', 'w') as f:
                                json.dump(info, f, indent=4)
                                await ctx.send(f"{user.display_name} was removed as an admin.")
                                print(Fore.BLUE + " [+] " + Fore.LIGHTBLUE_EX + user.display_name + Fore.RESET + " was removed as an admin.")
                        else:
                            await ctx.send("Incorrect Password.")
                    else:
                        await ctx.send("That person is not an admin.")
                else:
                    await ctx.send("You don't have permission to remove players as an admin.")
            else:
                await ctx.send(f"Not a valid setting. Try: {prefix} -admin (add, remove) (user)")

    async def verify(self):
        try:
            member_count = self.party.member_count

            if 500 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 501 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 502 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 503 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 504 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 505 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 506 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 507 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 508 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 509 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 510 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 511 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 512 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 513 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 514 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 515 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 516 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 517 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 518 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 519 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 520 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 521 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 522 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 523 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 524 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 525 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 526 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 527 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 528 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 529 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 530 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 531 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 532 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 533 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 534 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 535 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 536 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 537 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 538 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 539 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 540 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 541 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 542 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 543 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 544 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 545 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 546 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 547 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 548 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 549 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 550 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 551 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 552 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 553 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 554 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 555 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 556 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 557 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 558 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 559 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 560 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 561 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 562 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 563 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 564 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 565 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 556 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 557 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 558 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 559 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 560 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 561 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 562 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 563 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 564 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 565 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 566 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 567 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 568 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 569 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 570 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 571 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 572 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 573 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 574 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 575 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 576 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 577 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 578 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 579 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 580 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 581 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 582 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 583 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 584 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 585 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 586 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 587 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 588 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 589 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 590 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 591 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 592 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 593 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 594 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 595 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 596 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 597 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 598 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 599 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 600 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 601 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 602 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 603 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 604 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 605 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 606 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 607 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 608 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 609 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 610 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 611 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 612 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 613 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 614 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 615 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 616 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 617 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 618 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 619 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 620 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 621 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 622 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 623 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 624 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 625 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 626 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 627 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 628 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 629 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 630 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 631 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 632 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 633 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 634 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 635 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 636 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 637 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 638 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 639 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 640 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 641 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 642 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 643 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 644 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 645 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 646 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 647 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 648 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 649 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 650 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 651 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 652 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 653 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 654 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 655 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 656 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 657 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 658 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 659 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 660 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 661 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 662 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 663 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 664 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 665 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 666 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 667 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 668 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 669 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 670 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 671 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 672 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 673 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 674 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 675 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 676 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 677 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 678 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 679 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 680 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 681 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 682 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 683 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 684 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 685 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 686 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 687 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 688 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 689 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 690 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 691 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 692 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 693 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 694 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 695 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 696 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 697 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 698 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 699 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 700 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 701 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 702 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 703 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 704 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 705 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 706 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 707 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 708 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 709 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 710 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 711 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 712 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 713 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 714 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 715 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 716 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 717 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 718 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 719 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 720 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 721 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 722 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 723 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 724 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 725 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 726 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 727 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 728 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 729 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 730 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 731 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 732 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 733 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 734 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 735 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 736 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 737 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 738 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 739 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 740 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 741 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 742 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 743 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 744 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 745 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 746 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 747 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 748 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 749 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 750 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 751 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 752 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 753 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 754 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 755 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 756 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 757 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 758 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 759 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 760 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 761 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 762 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 763 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 764 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 765 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 766 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 767 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 768 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 769 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 770 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 771 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 772 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 773 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 774 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 775 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 776 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 777 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 778 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 779 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 780 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 781 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 782 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 783 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 784 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 785 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 786 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 787 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 788 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 789 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 790 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 791 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 792 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 793 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 794 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 795 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 796 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 797 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 798 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 799 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 800 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 801 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 802 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 803 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 804 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 805 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 806 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 807 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 808 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 809 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 810 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 811 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 812 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 813 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 814 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 815 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 816 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 817 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 818 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 819 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 820 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 821 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 822 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 823 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 824 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 825 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 826 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 827 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 828 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 829 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 830 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 831 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 832 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 833 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 834 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 835 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 836 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 837 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 838 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 839 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 840 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 841 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 842 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 843 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 844 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 845 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 846 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 847 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 848 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 849 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 850 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 851 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 852 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 853 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 854 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 855 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 856 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 857 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 858 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 859 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 860 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 861 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 862 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 863 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 864 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 865 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 866 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 867 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 868 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 869 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 870 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 871 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 872 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 873 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 874 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 875 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 876 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 877 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 878 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 879 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 880 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 881 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 882 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 883 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 884 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 885 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 886 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 887 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 888 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 889 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 890 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 891 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 892 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 893 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 894 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 895 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 896 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 897 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 898 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 899 in {len(self.friends)}:
                await self.set_presence('🔥 {party_size}/16 | ' + f'{len(self.friends)}/1000 Friends 🔥')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 900 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 901 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 903 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 904 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 905 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 906 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 907 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 908 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 909 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 910 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 911 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 912 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 913 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 914 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 915 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 916 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 917 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 918 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 919 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 920 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 921 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 922 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 923 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 924 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 925 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 926 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 927 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 928 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 929 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 930 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 931 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 932 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 933 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 934 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 935 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 936 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 937 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 938 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 939 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 940 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 940 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 941 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 942 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 943 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 944 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 945 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 946 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 947 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 948 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 949 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 950 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 951 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 952 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 953 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 954 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 955 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 956 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 957 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 958 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 959 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 960 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 961 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 962 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 963 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 964 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 965 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 966 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 967 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 968 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 969 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 970 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 971 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 972 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 973 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 974 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 975 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 976 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 977 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 978 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 979 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 980 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 981 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 982 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 983 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 984 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 985 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 986 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 987 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 988 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 989 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 990 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 991 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 992 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 993 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 994 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 995 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 996 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
            
            if 997 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

            if 998 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 999 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)
                
            if 1000 in {len(self.friends)}:
                await self.set_presence('✅ {party_size}/16 | ' + f'MAX/1000 Friends ✅')
                await asyncio.sleep(10)
                await self.party.set_privacy(fortnitepy.PartyPrivacy.PUBLIC)

        except: pass

    @commands.command()
    async def away(self, ctx: fortnitepy.ext.commands.Context) -> None:
        await self.set_presence(
            status=self.status,
            away=fortnitepy.AwayStatus.AWAY
        )

        await ctx.send('Status set to away.')