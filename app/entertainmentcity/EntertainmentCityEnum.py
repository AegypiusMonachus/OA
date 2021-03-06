from enum import Enum, unique

class ECTypeEnum(Enum):
    Live = 1002
    Yoplay = 1004
    Slot = 1004
    Hunter = 1006
    Sport = 1005
    
    
    
@unique
#注单流水号(唯一)
class billNoEnum(Enum):
    AG = 'BillNo'  #AG真人
    PT = 'GameCode'
    KAIYUAN = 'GameID'
    
    
KAIYUANEnum = {
 '620':'德州扑克'
,'720':'二八杠'
,'830':'抢庄牛牛'
,'220':'炸金花'
,'860':'三公'
,'900':'压庄龙虎'
,'600':'21点'
,'870':'通比牛牛'
,'890':'看牌抢庄牛牛'
,'740':'二人麻将'
,'730':'抢庄牌九'
,'650':'血流成河'
,'1950':'万人炸金花'
,'230':'急速炸金花'
,'240':'抢庄牌九'
,'630':'十三水'
,'610':'斗地主'
,'910':'百家乐'
,'920':'森林舞会'
,'930':'百人牛牛'
,'1350':'幸运转盘'
,'1940':'金鲨银鲨'
,'1960':'奔驰宝马'}
    
#注单流水号(唯一)
AGEnum = {'BAC':'百家乐'
,'CBAC':'包桌百家乐'
,'LINK':'多台'
,'DT':'龙虎'
,'SHB':'骰宝'
,'ROU':'轮盘'
,'FT':'番摊'
,'LBAC':'竞咪百家乐'
,'ULPK':'终极德州扑克'
,'SBAC':'保险百家乐'
,'NN':'牛牛'
,'BJ':'21点'
,'ZJH':'炸金花'
,'BF':'斗牛'
,'1':'庄0.95'
,'2':'闲1.00'
,'3':'和8.00'
,'4':'庄对11.00'
,'5':'闲对11.00'
,'6':'大0.50'
,'7':'小1.50'
,'8':'莊保險请参考游戏规则'
,'9':'閑保險请参考游戏规则'
,'12':'庄龙宝请参考游戏规则'
,'13':'闲龙宝请参考游戏规则'
,'14':'超级六12.00'
,'15':'任意对子5.00'
,'16':'完美对子25.00'
,'21':'龙1.00'
,'22':'虎1.00'
,'23':'和（龙虎）8.00'
,'41':'大(big)1'
,'42':'小(small)1'
,'43':'单(single)1'
,'44':'双(double)1'
,'45':'全围(allwei)24'
,'46':'围1(wei1)150'
,'47':'围2(wei2)150'
,'48':'围3(wei3)150'
,'49':'围4(wei4)150'
,'50':'围5(wei5)150'
,'51':'围6(wei6)150'
,'52':'单点1'
,'53':'单点2'
,'54':'单点3'
,'55':'单点4'
,'56':'单点5'
,'57':'单点6'
,'58':'对子1(double1)8'
,'59':'对子2(double2)8'
,'60':'对子3(double3)8'
,'61':'对子4(double4)8'
,'62':'对子5(double5)8'
,'63':'对子6(double6)8'
,'64':'组合12(combine12)5'
,'65':'组合13(combine13)5'
,'66':'组合14(combine14)5'
,'67':'组合15(combine15)5'
,'68':'组合16(combine16)5'
,'69':'组合23(combine23)5'
,'70':'组合24(combine24)5'
,'71':'组合25(combine25)5'
,'72':'组合26(combine26)5'
,'73':'组合34(combine34)5'
,'74':'组合35(combine35)5'
,'75':'组合36(combine36)5'
,'76':'组合45(combine45)5'
,'77':'组合46(combine46)5'
,'78':'组合56(combine56)5'
,'79':'和值4(sum4)50'
,'80':'和值5(sum5)18'
,'81':'和值6(sum6)14'
,'82':'和值7(sum7)12'
,'83':'和值8(sum8)8'
,'84':'和值9(sum9)6'
,'85':'和值10(sum10)6'
,'86':'和值11(sum11)6'
,'87':'和值12(sum12)6'
,'88':'和值13(sum13)8'
,'89':'和值14(sum14)12'
,'90':'和值15(sum15)14'
,'91':'和值16(sum16)18'
,'92':'和值17(sum17)50'
,'101':'直接注1:35'
,'102':'分注1:17'
,'103':'街注1:11'
,'104':'三數1:11'
,'105':'4個號碼1:8'
,'106':'角注1:8'
,'107':'列注(列1)1:2'
,'108':'列注(列2)1:2'
,'109':'列注(列3)1:2'
,'110':'線注1:5'
,'111':'打一1:2'
,'112':'打二1:2'
,'113':'打三1:2'
,'114':'紅1:1'
,'115':'黑1:1'
,'116':'大1:1'
,'117':'小1:1'
,'118':'單1:1'
,'119':'雙1:1'
,'180':'底注+盲注'
,'181':'一倍加注'
,'182':'二倍加注'
,'183':'三倍加注'
,'184':'四倍加注'
,'207':'莊1平倍'
,'208':'莊1翻倍'
,'209':'莊2平倍'
,'210':'莊2翻倍'
,'211':'閑1平倍'
,'212':'閒1翻倍'
,'213':'閒2平倍'
,'214':'閒2翻倍'
,'215':'閒3平倍'
,'216':'閒3翻倍'
,'217':'莊3平倍'
,'218':'莊3翻倍'
,'220':'底注'
,'221':'分牌'
,'222':'保險'
,'223':'分牌保險'
,'224':'加注'
,'225':'分牌加注'
,'226':'完美對子'
,'227':'21+3'
,'228':'旁注'
,'229':'旁注分牌'
,'230':'旁注保險'
,'231':'旁注分牌保險'
,'232':'旁注加注'
,'260':'龍'
,'261':'鳳'
,'262':'對8以上'
,'263':'同花'
,'264':'順子'
,'265':'豹子'
,'266':'同花順'
,'270':'黑牛'
,'271':'紅牛'
,'272':'和'
,'273':'牛一'
,'274':'牛二'
,'275':'牛三'
,'276':'牛四'
,'277':'牛五'
,'278':'牛六'
,'279':'牛七'
,'280':'牛八'
,'281':'牛九'
,'282':'牛牛'
,'283':'雙牛牛'
,'284':'銀牛/金牛/炸彈牛/五小牛'

,'WH40': '皇家戏台'
,'WH44': '蒸汽战争'
,'SB58': '魅惑魔女'
,'WH36': '橫行霸道'
,'WH42': '古惑仔'
,'WH55': '神奇宠物'
,'SB57': '魔龙'
,'WH19': '财宝塔罗'
,'WH28': '埃及宝藏'
,'WH23': '封神演义'
,'WH27': '和风剧院'
,'WH30': '点石成金'
,'WH02': '圣女贞德'
,'WH07': '五狮进宝'
,'WH12': '发财熊猫'
,'WH38': '十二生肖'
,'WH35': '招财锦鲤'
,'WH18': '白雪公主'
,'WH20': '葫芦兄弟'
,'WH34': '内衣橄榄球'
,'WH32': '贪玩蓝月'
,'SB55': '多宝鱼虾蟹'
,'WC01': '跳跳乐'
,'WH21': '永恒之吻'
,'WH22': '恐怖嘉年华'
,'WH24': '僵尸来袭'
,'WH29': '狂野女巫'
,'SV41': '富贵金鸡'
,'WH17': '嫦娥奔月'
,'WA01': '钻石女王'
,'SC05': '百搭777'
,'WH06': '亚瑟王'
,'WH10': '爱丽丝大冒险'
,'WH11': '战火风云'
,'WH04': '穆夏女神'
,'EP02': '龙虎'
,'WH03': '冠军足球'
,'SB51': '王者传说'
,'EP03': '骰宝'
,'WH01': '阿里巴巴'
,'SB47': '神奇宝石'
,'SB50': 'XIN哥来了'
,'SB49': '金龙珠'
,'SB45': '猛龙传奇'
,'SC03': '金拉霸'
,'SX02': '街头烈战'
,'XG10': '龙舟竞渡'
,'XG11': '中秋佳节'
,'XG12': '韩风劲舞'
,'XG13': '美女大格斗'
,'XG16': '黄金对垒'
,'FRU': '水果拉霸'
,'PKBJ': '杰克高手(大版视频扑克)'
,'SLM1': '美女沙排'
,'SLM2': '运财羊'
,'SLM3': '武圣传'
,'TGLW': '极速幸运轮'
,'SB01': '太空漫游'
,'SB02': '复古花园'
,'SB03': '关东煮'
,'SB04': '牧场咖啡'
,'SB05': '甜一甜屋'
,'XG09': '大豪客'
,'XG01': '龙珠'
,'XG02': '幸运8'
,'XG03': '闪亮女郎'
,'XG04': '金鱼'
,'XG05': '中国新年'
,'XG06': '海盗王'
,'XG07': '鲜果狂热'
,'XG08': '小熊猫'
,'SB06': '日本武士'
,'SB07': '象棋老虎机'
,'SB08': '麻将老虎机'
,'SB09': '西洋棋老虎机'
,'SB10': '开心农场'
,'SB11': '夏日营地'
,'SB12': '海底漫游'
,'SB13': '鬼马小丑'
,'SB14': '机动乐园'
,'SB15': '惊吓鬼屋'
,'SB16': '疯狂马戏团'
,'SB17': '海洋剧场'
,'SB18': '水上乐园'
,'SB19': '空中战争'
,'SB20': '摇滚狂迷'
,'SB21': '越野机车'
,'SB22': '埃及奥秘'
,'SB23': '欢乐时光'
,'SB24': '侏罗纪'
,'SB25': '土地神'
,'SB26': '布袋和尚'
,'SB27': '正财神'
,'SB28': '武财神'
,'SB29': '偏财神'
,'AV01': '性感女仆'
,'SB30': '灵猴献瑞'
,'PKBD': '百搭二王'
,'PKBB': '红利百搭'
,'SB31': '天空守护者'
,'SB32': '齐天大圣'
,'SB33': '糖果碰碰乐'
,'SB34': '冰河世界'
,'FRU2': '水果拉霸2'
,'SB35': '欧洲列强争霸'
,'SB36': '捕鱼王者'
,'SB37': '上海百乐门'
,'SB38': '竞技狂热'
,'SL1': '巴西世界杯'
,'SL2': '疯狂水果店'
,'SL3': '3D 水族馆'
,'PK_J': '视频扑克(杰克高手)'
,'SL4': '极速赛车'

,'YPLA': 'yoplay大厅'
,'YFD': '森林舞会'
,'YBEN': '奔驰宝马'
,'YHR': '極速赛马'
,'YGS': '猜猜乐'
,'YFR': '水果拉霸'
,'YDZ': '德州牛仔'
,'YBIR': '飞禽走兽'
,'YFP': '水果派对'
,'YMFD': '森林舞会多人版'
,'YMFR': '水果拉霸多人版'
,'YMBN': '百人牛牛'
,'YGFS': '多宝水果拉霸'
,'YJFS': '彩金水果拉霸'
,'YMBI': '飞禽走兽多人版'
,'YMBA': '牛牛对战'
,'YMBZ': '奔驰宝马多人版'
,'YMAC': '动物狂欢'
,'YMJW': '西游争霸'
,'YMJH': '翻倍炸金花'
,'YMBF': '刺激战场'
,'YMSG': '斗三公'
,'YMJJ': '红黑梅方'
,'YJTW': '彩金宝藏世界'
,'YMD2': '疯狂德州'
,'YJBZ': '彩金奔驰宝马'
,'YMSL': '海陆争霸'
,'YMDD': '百人推筒子'
,'YMKM': '功夫万条筒'
,'YMDL': '双喜炸金花'
,'YMPL': '凤凰传奇'
,'YMBJ': '全民21点'
,'YMLD': '福星推筒子'
,'YMGG': 'YP刮刮卡'
,'YMFW': '财富转盘'
,'YMBS': '射龙门'
,'YMEF': '11选5'}


# 注单流水号（唯一）
PTEnum = {
  'tclsc': '三小丑刮刮乐'
, 'treasq': '八宝一后'
, 'hb': '夜间外出 | 一夜奇遇'
, 'ashadv': '仙境冒险'
, 'aogs': '神的时代'
, 'ftsis': '神灵时代 : 命运姐妹'
, 'athn': '神的时代 : 智慧女神'
, 'gts50': '热力宝石'
, 'furf': '神的时代 : 雷霆4神'
, 'zeus': '神的时代 : 奥林匹斯之国王'
, 'hrcls': '神的时代 : 奥林匹斯之王子'
, 'ashamw': '狂野亚马逊'
, 'arc': '弓兵 | 弓箭手'
, 'art': '北极宝藏'
, 'asfa': '亚洲幻想'
, 'gtsatq': '亚特兰蒂斯女王'
, 'bs': '白狮'
, 'bl': '海滨嘉年华'
, 'bt': '百慕大三角 | 百慕达三角洲'
, 'bob': '熊之舞'
, 'ashbob': '杰克与魔豆'
, 'bfb': '水牛闪电'
, 'ct': '船长的宝藏'
, 'ctp2': '超级船长的宝藏 | 船长的宝藏PRO'
, 'gtscb': '现金魔块 | 金库'
, 'cashfi': '深海大赢家'
, 'ctiv': '拉斯维加斯的猫 | 猫赌神'
, 'catqk': '猫女王'
, 'chao': '超级888'
, 'chl': '樱桃之恋 | 樱花之恋'
, 'ashcpl': '宝物箱中寻'
, 'cm': '中国厨房'
, 'scs': '经典老虎机刮刮乐'
, 'gtscnb': '警察与土匪'
, 'gtscbl': '牛仔和外星人'
, 'c7': '疯狂之七 | 疯狂7'
, 'gtsdrdv': '大胆的戴夫和荷鲁斯之眼 | 胆大戴夫和拉之眼'
, 'dt': '沙漠宝藏'
, 'dt2': '沙漠宝藏2 | 沙漠宝藏II'
, 'dnr': '海豚礁'
, 'dlm': '情圣博士 | 恋爱专家'
, 'gtsdgk': '龙之王国'
, 'eas': '惊喜复活节 | 复活节大惊喜'
, 'egspin': '埃及旋转'
, 'esmk': '埃斯梅拉达'
, 'rodl': '独家轮盘赌'
, 'ashfta': '白雪公主'
, 'fcgz': '翡翠公主'
, 'gtsflzt': '飞龙在天'
, 'fkmj': '疯狂麻将'
, 'ftg': '五虎将'
, 'gtsfc': '足球狂欢节'
, 'fbr': '终极足球 | 足球规则'
, 'fow': '惊异之林 | 森林的奇迹'
, 'frtf': '幸运5 | 五个海盗'
, 'fday1': '幸运日'
, 'frtln': '幸运狮子'
, 'fxf': '诙谐财富 | 狐狸的宝藏'
, 'foy': '青春之泉'
, 'fdt': '戴图理的神奇七 | 弗兰克.戴图理 : 神奇7'
, 'fdtjg': '戴图理的神奇七大奖 | 弗兰克.戴图理 : 神奇7奖池版'
, 'fmn1': '水果狂 | 狂热水果'
, 'ashfmf': '满月财富'
, 'fff': '酷炫水果农场 | 水果农场'
, 'fnfrj': '趣味水果'
, 'fm': '古怪猴子'
, 'ges': '艺伎故事'
, 'gesjp': '艺伎故事彩池游戏 | 艺伎故事奖池版'
, 'gemq': '宝石女王 | 宝石皇后'
, 'glr': '角斗士'
, 'glrj': '角斗士彩池游戏 | 角斗士累积奖池'
, 'grel': '金色召集'
, 'glg': '黄金版游戏 | 黄金游戏'
, 'gos': '黄金之旅 | 黄金巡回赛'
, 'bib': '湛蓝深海'
, 'hlf': '万圣节财富'
, 'hlf2': '万圣节财富2'
, 'haocs': '好事成双'
, 'hh': '鬼屋'
, 'ashhotj': '丛林心脏 | 丛林之心'
, 'heavru': '武则天'
, 'hk': '高速公路之王 | 高速之王'
, 'gtshwkp': '超级高速公路之王 | 高速之王PRO'
, 'hotktv': '火热KTV'
, 'gtsir': '浮冰流 | 极地冒险'
, 'aztec': '印加帝国头奖 | 印加大奖'
, 'gtsirl': '爱尔兰运气'
, 'jpgt1': '奖金巨人'
, 'gtsje': '玉皇大帝'
, 'gtsjxb': '吉祥8'
, 'jqw': '金钱蛙'
, 'gtsjhw': '约翰韦恩'
, 'kkg': '无敌金刚 | 金刚-世界的第八大奇迹'
, 'lndg': '金土地'
, 'ght_a': '烈焰钻石'
, 'kfp': '六福兽'
, '7bal': '真人7座百家乐'
, 'chel': '真人娱乐场扑克 | 真人德州扑克'
, 'rofl': '实况法式轮盘赌 | 真人法式轮盘'
, 'plba': '累积真人百家乐'
, 'sbl': '真人骰子'
, 'vbal': 'VIP百家乐'
, 'longlong': '龙龙龙'
, 'lm': '疯狂乐透'
, 'gts51': '幸运熊猫'
, 'ms': '魔幻吃角子老虎 | 魔幻老虎机'
, 'mgstk': '神奇的栈'
, 'gtsmrln': '玛丽莲梦露'
, 'bal': '迷你百家乐 | 真人百家乐'
, 'mfrt': '财富小姐'
, 'ashlob': '布莱恩的生活'
, 'mcb': 'Cash back先生 | 返利先生'
, 'nk': '海王星王国'
, 'nian': '年年有余'
, 'nc_bal': '无抽水真人迷你百家乐'
, 'pmn': '黑豹之月 | 豹月'
, 'pl': '舞线'
, 'pgv': '企鹅假期'
, 'pst': '法老王的秘密'
, 'paw': '小猪与狼'
, 'pnp': '粉红豹'
, 'gtspor': '非常幸运 | 巨额财富'
, 'photk1': '热紫 | 紫红水果屋'
, 'qop': '金字塔女王'
, 'qnw': '权杖女王'
, 'ririjc1': '日日进财'
, 'ririshc88': '日日生財'
, 'rky': '洛基传奇 | 洛奇'
, 'gtsrng': '罗马与荣耀 | 荣耀罗马'
, 'rol': '真人轮盘赌 | 轮盘'
, 'gtsru': '财富魔方 | 魔方财富'
, 'sfh': '非洲炎热'
, 'gtssmbr': '激情桑巴'
, 'ssp': '圣诞奇迹 | 圣诞老人的惊喜'
, 'savcas': '大草原现金'
, 'samz': '亚马逊的秘密'
, 'shmst': '夏洛克的秘密 | 神秘夏洛克'
, 'sling': '四灵'
, 'sx': '四象'
, 'sis': '沉默的武士'
, 'sisjp': '沉默的武士彩池游戏 | 沉默的武士奖池版'
, 'sib': '银子弹'
, 'ashsbd': '辛巴达的黄金之旅'
, 'spud': '黄金农场'
, 'sol': '好运连胜 | 好运来'
, 'sugla': '糖果大陆'
, 'gtsswk': '孙悟空'
, 'slion': '超级狮子'
, 'cnpr': '甜蜜派对'
, 'tpd2': '泰国天堂'
, 'thtk': '泰寺 | 泰国神庙'
, 'gtsgme': '大明帝国'
, 'gtsjzc': '爵士俱乐部'
, 'lvb': '爱之船'
, 'mmy': '木乃伊迷城 | 神鬼传奇'
, 'donq': '堂吉诃德的财富 | 富有的唐吉可德'
, 'tmqd': '三剑客和女王 | 三剑客和女王的钻石'
, 'titimama': '跳跳猫猫'
, 'ashtmd': '交易时刻'
, 'topg': '壮志凌云'
, 'ttc': '顶级王牌 - 明星 | 顶级王牌 - 明星'
, 'ta': '三个朋友 | 三个朋友老虎机'
, 'trpmnk': '三倍猴子'
, 'trl': '真爱'
, 'ub': '丛林巫师 | U咖布咖'
, 'er': '开心假期'
, 'vcstd_3': '豪华的开心假期 | 开心假期加强版'
, 'gts52': '疯狂维京海盗 | 狂躁的海盗'
, 'warg': '黄金武士'
, 'whk': '白狮王 | 怀特王'
, 'gtswg': '赌徒 | 狂野赌徒'
, 'ashwgaa': '疯狂赌徒2 : 北极探险'
, 'wis': '我心狂野 | 狂野精灵'
, 'gtswng': '黄金翅膀 | 纯金翅膀'
, 'wlg': '舞龙'
, 'wlgjp': '舞龙彩池游戏 | 舞龙奖池版'
, 'wlcsh': '五路财神'
, 'zcjb': '招财进宝'
, 'zcjbjp': '招财进宝彩池游戏 | 招财进宝彩池'
, 'zctz': '招财童子'
, 'aogrol': '真人轮盘'}
    
    
    