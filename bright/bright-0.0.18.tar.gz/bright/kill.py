import asyncio
import json
from bright import _post, _get
from bright import ftime


async def get_data_list_post(n, t):
    now = ftime.get_timestamp()
    noise = [
        {
            "url": "http://www.gdzp.org/index.php/customer",
            "data": {
                "name": n,
                "phone": t,
                "code": "SMS_137674624",
                "web": "中鹏服务保障悬浮条"
            }
        },
        {
            "url": "https://msg.huangqi1688.com/message/mess_sms.php",
            "data": {
                "mess_tel": t,
                "mess_ip": "192.168.0.1"
            }
        },
        {
            "url": "https://jzapi.baidu.com/fengming-c/clue-audit/risk/lp-submit/expose?reqid=4b534c47-639f-4a22-13c0-{}".format(
                now),
            "data": {"clueJoinId": "210907163269879710", "userId": 23807488,
                     "solutionId": 12545375, "solutionType": "form",
                     "lpInfo": {"appId": 269, "siteId": 56875435, "pageId": 79945541,
                                "lpUrl": "https://isite.baidu.com/site/wjzu5lhq/6bd5da5b-5a64-4f25-85b0-69f6e5781bd2?fid=nHTvnHnLnHfknHcLnW0LPH6drj-xnWcdg1R&ch=4&bfid=fbuFw0cK5yTK02GeT5f00rD0KfD0wh_KPT0qO0m000jzaWNTZf0000f0gf0DkXjwVHjy_PjfspUAtq2ddPo5Ltg6YUg5VTv1roHzdrz3LeE8dQ3_8PStJPaMkE5iVIAM1e02H65u&bd_vid=10807462079945742208"},
                     "clueInfo": {
                         "formControls": [{"name": "公司", "value": "123123", "type": "input"},
                                          {"name": "公司规模（员工数量）", "value": "20000",
                                           "type": "input"},
                                          {"name": "联系人姓名", "value": "{}".format(n),
                                           "type": "name"},
                                          {"name": "联系人电话", "value": "{}".format(t),
                                           "type": "phone"},
                                          {"name": "联系人职位", "value": "主管", "type": "input"},
                                          {"name": "您上线平台的计划时间表是？", "value": "有意向考察相关项目",
                                           "type": "linkage"}],
                         "captcha": {"type": "no", "phoneNo": "{}".format(t)}}, "clientInfo": {},
                     "adInfo": {
                         "referrer": "https://www.baidu.com/baidu.php?url=af0000KpxzUee8Wyt0g6LUMZlzykSydR-NvFahNdRZ1UrY188Vkemva5gmR7YZkpfTwsuOD91UNnlauPYWh8YSncahMPpvzbSqRy960bGyd1MqoqbFrc_Pjk7ukFJ7aVIsIIKGZvuAnbFc3Epo5p2u0OHSDHC7_yN6zKYWg8Pt2NdFnDBuYIO0LwWBnJ5QLvWnT3KdU0o2amvGuVEdZArcMdN1tY.7Y_NR2Ar5Od66xAS6MzEukmDfwECF63nEj6LRpEuKYLLUohIdSxT1Yqhx_d4Pvxu8E_1qrOgYGLXrz8SeFLd3hcELOY5CBOxBOg7SOoemEL3xdkxVvxoOPSOYLHuTOw7SLjIJoOdqmphr1oxoknpetZd3QcxOK8YxCxSa1FSCMqjIo__hSNMO6dO216J4xOKSUqa1vxYUPP--hg9uOUOQS9OcdvyyypePy814IEO0ztZO7SO-YTE4_885ZO_Sv9en-dL4MUEdYPgHOv5qMN8O3EY5CohISOsLHT5Zqpx5uISxWze51xWfOvE1nOkrL1L5O3EEex3-pUnMeOH8s2N9h9mzNeS1cC.U1Yd0ZDqkXjwVfKspynqn0KsTv-MUWdBuHRkmWK9uWcdrjRzmH7hmvDYrynkmvDvPjI9uWnvm6KY5Tg6YUR0pyYqnWcd0ATqUvwlnfKdpHdBmy-bIfKspyfqP0KWpyfqrHn0UgfqnH0krNtknjDLg1csPWc0pvbqn0KzIjY1rjm0mhbqnHR3g1csP7tznHIxPH010AdW5HD3PWndPjRkP1uxnHbknj0Lnjbvn7tznHR3nHn4Pj03PsKkTA-b5H00TyPGujYs0ZFMIA7M5H00mycqn7ts0ANzu1Ys0ZKs5H00UMus5H08nj0snj0snj00Ugws5H00uAwETjYs0ZFJ5H00uANv5gKW0AuY5H00TA6qn0KET1Ys0AFL5HDs0A4Y5H00TLCq0A71gv-bm1dsTzdMXh410A-bm1dcHbc0TA9YXHY0IA7zuvNY5Hm1g1Kxn10s0ZwdT1YYnWDdrHmvnjRsPWRzPH0snH030ZF-TgfqnHm1nH0sPWckP1D1r0K1pyfquWfLnjIBmyDsnj0kPWT1u0KWTvYqfYDvrH0krjD3nYR1wHRYfsK9m1Yk0ZwdIjYk0ZK85H00TydY5H00Tyd15H00XMfqn0KVmdqhThqV5HKxn7ts0Aw9UMNBuNqsUA78pyw15HKxn7ts0ZK9I7qhUA7M5H00uAPGujYs0ANYpyfqQHD0mgPsmvnqn0KdTA-8mvnqn0KkUymqn0KhmLNY5H00pgPWUjYs0A7buhk9u1Y30Akhm1Ys0AwWmvfq0Zwzmyw-5HmLnjbsnfKBuA-b5H6YPW-KPRuKPHF7rDD3fYuKwWnLn1-awjRzrHKjrDc40AqW5HD0mMfqn0KEmgwL5H00ULfqn0KETMKY5H0WnanWnansc10Wna3snj0snj0Wnansc10WQinsQW0snj0snankQW0snjDsn0K3TLwd5Hc1rj0LPj630Z7xIWYsQWRzg108njKxna3sn7tsQWmkg108nHNxna34nNtsQWcsg100mMPxTZFEuA-b5H00ThqGuhk9u1Ys0APv5fKGTdqWTADqn0KWTjYs0AN1IjYs0APzm1Yknj0YP0&us=newvui&xst=mWY3Pjm4fHNAfHRzwH9KrDPAfRm1P1n4fbfdnWbsf19arf715HDLPWD1P1DYnHDzP1csP1R3PH64g1czPNtY0gTqkXjwVf7k5Tg6YURKIHYzn16sP1f3r07Y5HDvn1DsnjmznHTKUgDqn0cs0BYKmv6quhPxTAnKUZRqn07WUWdBmy-bIfDknW64nj0kP1cv&cegduid=nWn3njTYrj6&solutionId=4876832&word=&ck=6994.48.80.428.243.300.141.342&shh=www.baidu.com&sht=baidu&wd=&bc=110101"}}
        },
        {
            "url": "http://data.gzxhce.com/plus/Formto3jj.php",
            "data":{
                "name": n,
                "mobile": t,
                "fromurl": "http://www.gzxhdn.cn/?bd03-PC-ZJ&jzl_kwd=301602377836&jzl_ctv=51611543028&jzl_ch=11&jzl_act=34194620&jzl_cpg=162834395&jzl_adp=6048669482&jzl_sty=0&jzl_dv=1&bd_vid=11133531195366162649"
            }
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
            "url":"https://jzapi.baidu.com/rest/form/c/sessions"
                  "/6c6b88902d0e4022800f69f690adee9e/submissions?reqid=4b534c47-cdca-4c95-02f5"
                  "-{}".format(now),
            "data":{
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
            "url": "https://jzapi.baidu.com/rest/form/c/sessions/00fe4d961f1c4378a9bf2d7bfbf297bd/submissions?reqid=4b534c47-7f9f-4ac4-da5a-{}".format(now),
            "data":{
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

    ]

    return noise


async def get_data_list_get(n, t):
    now = ftime.get_timestamp()
    noise = [
        {
            "url": "https://www6.53kf.com/client/clientOutDetain.php?company_id=72140474&guest_id=93642297009&style=1&style_id=106186477&out_id=5605&device=pc&uid=4acca789c84b0963f32484a6fd1a97c3&referer=https%3A%2F%2Fstudy.hxsd.com%2Fgames%2Feduzt%2Fcgzhy20190816%2F%3F%26campaign%3D%26baidupc%26sz%26ty%26bj-hxsd01%26gx%26keywordid%3D88887005%26%26jzl_kwd%3D219608971481%26jzl_ctv%3D45970231406%26jzl_ch%3D11%26jzl_act%3D10097141%26jzl_cpg%3D143734624%26jzl_adp%3D5399665096%26jzl_sty%3D0%26jzl_dv%3D1%26sdclkid%3DAL2s152iArD6A5epALFl%26bd_vid%3D10532010867702222457&keyword=https%3A%2F%2Fwww.baidu.com%2Fbaidu.php%3Furl%3Daf0000KpxzUee8WytaWpTTjzSxn_0_e-RKeJdG_u6S_jtk5xt4vOyIjOIEHiSZuvmOoxixnJekKqFzHbdpB7U4-uIztib3ja3h5edIxkFN23Re8pELrWP51Pzgd7DzjpKgD7A_DyTEDoocjdu-h8aDPxDChoBa6vWhjEfMMNDcJB92Jnv_S2FQC2GNdyLbpfQT0cn8sI3v8r00mS3Yo3YOv-2vCv.Db_iwYn7vWzJlcebfphI2m3DLmrA9KjJ3pVAizExu_olmrOy7MHWuxJBmlL_3_ArZoZsqpAWox-1dIDId-xgNYIXdrW6IPIBmvUPh1k__LIX8g9CtEUsgnu2qOHu_LSPxu_ol4XAWzsY5CmePvOk_zTpSz1Gl4XAWzsdnNdqTEjw4ympj7I-hOkoe2S8g9Ct_r5RkgvTxZWvIrH_l4XAWz_LmvPLZxElXMIuElX8g9Ct_IjfkudztPZ-8S9BEoZIjweTHZVOgbWoLuZSvU4I5VLFkSLqxdCJN9h9mo3eQQ70.U1Yk0ZDqkXjwVfKspynqn0KsTv-MUWYYPvc1mW-WP10kryFhPjNWnvmLuHPbPvfYmHPBP1-9rfKY5TM8vqo73PAd0A-V5HczPfKM5yqbXWD0Iybqmh7GuZR0TA-b5Hf0mv-b5Hb10AdY5HDsnH-xnH0kPdtznjmz0AVG5H00TMfqn16v0AFG5HDdPNtkPH9xnW0Yg1ckPdtdnjn0UynqnH6vnWbdPj03P-tkrH04njf1nHT3g1czrj6zPH03Pjf10Z7spyfqn0Kkmv-b5H00ThIYmyTqn0K9mWYsg100ugFM5HD0TZ0qn0K8IM0qna3snj0snj0sn0KVIZ0qn0KbuAqs5HD0ThCqn0KbugmqTAn0uMfqn0KspjYs0Aq15H00mMTqnH00UMfqn0K1XWY0mgPxpywW5gK1QyIlUMn0pywW5R9rf6KspZw45fKYmgFMugfqPWPxn7tkPHD0IZN15HD3nW0LnjbvnjRznHDsnWmkn1RY0ZF-TgfqnHm1nH0sPWckP1D1r0K1pyfquWfLnjIBmyDsnj0kPWT1u0KWTvYqfYDvrH0krjD3nYR1wHRYfsK9m1Yk0ZK85H00TydY5H00Tyd15H00uANYgvPsmHYs0ZGY5H00UyPxuMFEUHYsg1Kxn0Kbmy4dmhNxTAk9Uh-bT1Ysg1Kxn0Ksmgwxuhk9u1Ys0AwWpyfqn0K-IA-b5iYk0A71TAPW5H00IgKGUhPW5H00Tydh5H00uhPdIjYs0A-1mvsqn0K9uAu_myTqnfK_uhnqn0KbmvPb5fKYTh7buHYvP10dnjf0mhwGujY3Pjm4fHNAfHRzwH9KrDPAfRm1P1n4fbfdnWbsf19arfKEm1Yk0AFY5H00Uv7YI1Ys0AqY5HD0ULFsIjYzc10WnHbWnznLPHRsn1mzP1DWn1Rsnj0Wn1Rsnj08nj0snj0sc1nWnznsc1D3c108nj0snH0sc108P16kPW0s0Z91IZRqnH0srHTkPjD0TNqv5H08n1Kxna3sn7tsQW0sg108PWNxna3sPdtsQWbLg108njKxnHc30AF1gLKzUvwGujYs0ZFEpyu_myTqnfKWIWY0pgPxmLK95H00mL0qn0K-TLfqn0KWThnqn16knWn%26us%3Dnewvui%26xst%3DmWY3Pjm4fHNAfHRzwH9KrDPAfRm1P1n4fbfdnWbsf19arf715HDLPWD1P1DYnHDzP1csP1R3PH64g1czPNts0gTqzXeUv_g6YURKTHL73PAd0gRqnH0srHTkPjDKIjYkPWnknj0vnWDL0ydk5H0an0cV0yPC5yuWgLKW0ykd5H0Kmv3qmh7GuZRKnHn4rHR1P1Dk%26word%3D%26ck%3D4478.3.85.274.152.300.141.271%26shh%3Dwww.baidu.com%26sht%3Dbaidu%26wd%3D%26bc%3D110101&talktitle=CG%E7%BB%BC%E5%90%88+%7C+%E7%81%AB%E6%98%9F%E6%97%B6%E4%BB%A3%E6%95%99%E8%82%B2+%E4%B8%AD%E5%9B%BD%E8%89%BA%E6%9C%AF%E6%95%99%E8%82%B2%E9%AB%98%E7%AB%AF%E5%93%81%E7%89%8C&out_type=4&action=click&prize_name=&mobile={}&code=&callback=out_detain_callback_{}".format(
                t, now),
            "headers": "text/html; charset=UTF-8"
        },
        {
            "url": "http://www14c1.53kf.com/impl/rpc_callback_phone.php?from=api&company_id"
                   "=72204003&guest_id=10928337502000&style=1&from_page=https%3A%2F%2Fwww.baidu.com%2Fbaidu.php%3Furl%3Daf0000KpxzUee8WytAUB9iG8DN4YrbxdHedSMs0KqyiD7nltNSdCAZygAiDIdIRPiU7fcgbi0jBs9AMejC5gVmf7-Z0lk2Cc6ejc3shlHsmFBB8OLu4lW_X6fThi4--wvC5Bgyymw2st5V9IjvN2dpEN5srQuNL1nyHTukNSMZ0H8O4VJOY-1F8lk0NTON_8m-ZQXnxni2iYsqw7gBZEnnJItLgf.7D_a59JsntPHYLmDfuQn-MPi_nYQZHklIhwf.U1Yz0ZDqkXjwVfKspynqn0KsTv-MUWdhnW6Ln1R3PWmdPWcdPjT4rAf3nWm3ryDknjD3PHFBr0KY5T5L_evq1P5qkXjwVfKGUHYznWR0u1dEuZCk0ZNG5yF9pywd0ZKGujYY0APGujY4nsKVIjYknjD4g1DsnHIxnW0vn6KopHYs0ZFY5Hn3P6KBpHYkPHNxnHR3g1csP7tznHIxPH010AdW5HD3n1ndn1T3P19xnHbknHfvn1TvnNtzPjnsPHnvnHf1nsKkTA-b5H00TyPGujYs0ZFMIA7M5H00mycqn7ts0ANzu1Ys0ZKs5H00UMus5H08nj0snj0snj00Ugws5H00uAwETjYs0ZFJ5H00uANv5gKW0AuY5H00TA6qn0KET1Ys0AFL5HDs0A4Y5H00TLCq0A71gv-bm1dsTzdMXh410A-bm1dcHbc0TA9YXHY0IA7zuvNY5Hnkg1nkP7tknHD0IZN15HDznjf4PW6krj0dnWbvrHcsPW6v0ZF-TgfqnHm1nH0sPWckP1D1r0K1pyfquWfLnjIBmyDsnj0kPWT1u0KWTvYqfYDvrH0krjD3nYR1wHRYfsK9m1Yk0ZK85H00TydY5H00Tyd15H00uANYgvPsmHYs0ZGY5H00UyPxuMFEUHYsg1Kxn0Kbmy4dmhNxTAk9Uh-bT1Ysg1Kxn0Ksmgwxuhk9u1Ys0AwWpyfqn0K-IA-b5iYk0A71TAPW5H00IgKGUhPW5H00Tydh5H00uhPdIjYs0A-1mvsqn0K9uAu_myTqnfK_uhnqn0KbmvPb5fKYTh7buHYs0AFbpyfqrjfvrRDdwbDdnbR3fH9jwb7An1T1rRFDPHc4nDn3fWb0UvnqnfKBIjY10Aq9IZTqn0KEIjYk0AqzTZfqnBnsc1DLc1nWP1RzPjndPj64c1cknj0sc1cknj0sQW0snj0snankc1nWnanVc108nj0snH0sc1D8njf3nj0s0Z91IZRqnW6Lnj0dPHD0TNqv5H08PWuxna3sn7tsQW0sg108PWNxna3sr7tsQW6Lg108nW9xn0KBTdqsThqbpyfqn0KzUv-hUA7M5Hf0mLmq0A-1gvPsmHYs0APs5H00ugPY5H00mLFW5HD1nW6%26us%3Dnewvui%26xst%3DmWY3Pjm4fHNAfHRzwH9KrDPAfRm1P1n4fbfdnWbsf19arf715HDLPWD1P1DYnHDzP1csP1R3PH64g1czPNtk0gTqsOX1EULnYOL73PAd0gDqkXjwVf7d5Hc3P10sPHRk0gfqnHm1nH0sPWckPs7VTHYs0W0aQf7Wpjdhmdqsms7_IHYs0yP85yF9pywd0HDznWDsrjRLPWc%26word%3D%26ck%3D1365.17.120.390.290.300.141.786%26shh%3Dwww.baidu.com%26sht%3Dbaidu%26wd%3D%26bc%3D110101&talk_page=http%3A%2F%2Fwww.szhuazhiedu.com%2F2020.html%3Fbd_vid%3D11269317978045014641&land_page=http%253A%252F%252Fwww.szhuazhiedu.com%252F2020.html%253Fbd_vid%253D11269317978045014641&call={}&id6d=10337911,10396889&worker_id=".format(
                t)
        },
        {
            "url": "https://dft.zoosnet.net/lr/sendnote160711.aspx?tel={}&ccode=&id=DFT98123122&sid=aec12325f90c4e728e3fbc7480ce318e&cid=aec12325f90c4e728e3fbc7480ce318e&lng=cn&p=http%3A//www.blackcgart.cn/&e=&un=&ud=&on=&d={}".format(
                t, now),

        },
    ]

    return noise


async def send(name=None, tel=None):
    if not (name or tel):
        return "请输入：n t"
    headers = {"Content-Type": "application/json"}
    _noise = await get_data_list_get(name, tel)
    for index, no in enumerate(_noise):
        print(index)
        url = no.get("url")
        try:
            await _get.send(url, headers=headers if not no.get("headers") else no.get("headers"))
        except Exception as e:
            print(e)

    noise = await get_data_list_post(name, tel)
    for index, no in enumerate(noise):
        print(index) 
        url = no.get("url")
        data = no.get("data")
        try:
            await _post.send(url, json.dumps(data), headers=headers)
        except Exception as e:
            print(e)
    print('You have killed {} {} {} times!'.format(name, tel, len(noise) + len(_noise)))


def run_async(future):
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(future)
    return res


if __name__ == '__main__':
    run_async(send("宠宠", 13405004978))
