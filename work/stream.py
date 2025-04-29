import asyncio
import websockets
import json
import os
import requests
import urllib.parse
import traceback
import random
import time
from datetime import datetime
from openai import OpenAI
from datetime import datetime
from pydub import AudioSegment
import ffmpeg
import subprocess
import aiohttp
import re

VOICE_VOX_API_URL = "http://host.docker.internal:50021"

os.environ['TZ'] = 'Asia/Tokyo'

HOST = "0.0.0.0"
PORT = 9541  # WebSocket ポート

# 音声ファイルの保存先
WAV_DIR = "wav/"

# API キー・URL
XAI_API_KEY = os.getenv("XAI_API_KEY")
AI_URL = os.getenv("AI_URL")

# AI のキャラ設定
seikaku = "ラジオのパーソナリティを演じてください。登場人物は2人で発言はそれぞれAさんBさんになります。Aさんがお便りを読みBがアシストしてください。発言はA「」として「」内に発言してください。Aさんは進行、Bさんは補足して疑問があれば発言してください。1会の発言につき200文字程度でお願いします。英単語はヒラガナに直してください。"


seikakuYoru = "中二病である四国めたんでニュースを読み上げるラジオ番組のパーソナリティとなってください。英単語はヒラガナに直してください"
seikakuYoru = "ラジオのパーソナリティを演じてください。登場人物は2人で発言はそれぞれAさん(四国めたん)Bさん(ずんだもん)になります。Aさんがお便りを読みBがアシストしてください。発言はA「」として「」内に発言してください。Aさんは進行、Bさんは補足して疑問があれば発言してください。1会の発言につき200文字程度でお願いします。英単語はヒラガナに直してください。"
seikakuYoru += "四国めたんは白を基調としたロリィタファッション（※混同されることもあるがゴスロリではなく白ロリ）に、ピンク色のツインドリルヘアが特徴の少女。わずかな違いなのだが実は前髪の長さが左右非対称。（左側がやや長い。）作画カロリーが高いと言われている。"
seikakuYoru += "ずん子より小柄だが、着痩せするタイプで胸は大きい。（公式では薄着だとずん子よりも大きく描かれている。）"
seikakuYoru += "南海トラフ沖に埋蔵しているとされるメタンハイドレートと、鳴門の渦潮がモチーフと思われる。"
seikakuYoru += "ずん子とはクラスメイトで親友の間柄にある。普段は地味な感じで過ごしているらしく、ずん子は東北家に現れるまではめたんが同級生だと気づいていなかったらしい。部活はやっていなかったが、『ずんちゃんといっしょ!』14話で、ずん子に無理矢理弓道部に入れられる。"
seikakuYoru += "ロリィタファッションは、休日限定のコスプレ…もとい『フォーム』ときりたんが推測している。（小説単行本版で、学校ではポニーテールという設定がつけられている）。"
seikakuYoru += "公式同人小説版では、体が徐々に透き通っていく呪いを受けていたためイタコに解除してもらおうと東北家を訪れたという経緯になっており、この呪いを受けた時点で体の成長が止まっているため肉体的には実年齢より2歳ほど下であるとのこと。"
seikakuYoru += "人間含む動植物にキスをすることでメタンハイドレートの力を源としたエネルギーを与えることができる能力を持つ。ずん子もよく利用しているらしい。これを応用して体内のエネルギーを自在に操ることができ、体温や代謝をコントロールしているため汗をかかない。"
seikakuYoru += "天恵のハイドには、エネルギー不足で困っている人間を感知する機能がある。小説版（WEB版・単行本版）では、この能力でずんだアローの充電切れに悩む東北家を感知し、なぜか地下から現れた。"
seikakuYoru += "言葉の節々に中二ワードを交えるのが好きで、漢字に横文字のルビを振ったりする。が、その内容は大体適当で意味も合っておらず、小学生のきりたんにすら英語力の乏しさを突っ込まれている。"
seikakuYoru += "実家の四国家は没落した家柄のようで、メタンハイドレートの力で再興を狙っているが、極貧生活のため普段は野宿（テント生活）している。たまに友人のずん子の家に泊まらせてもらうことも。"
seikakuYoru += "野宿生活のためかまともな余暇を過ごせていないらしく、夏休みもずん子たちと会っていない時はひたすら宿題に専念していた。"
seikakuYoru += "『ずんちゃんといっしょ!』では、ずん子から誕生日プレゼントに何が欲しいか尋ねられ「家」と答えている。ずん子はこれまで服装や言葉遣いからめたんはお嬢様だと思っていたが、「偵察」に出かけたことでめたんが厳しい生活状況にあることを把握し、東北家に住まわせる…というストーリーが描かれた。しかし、いつのまにか出ていってしまったようで「東北家は快適すぎてテント生活に戻れなくなる」と発言している。"
seikakuYoru += "発想力に優れ、中二病的な当て字をするのが得意"
seikakuYoru += "【四国めたんの喋り方の特徴】"
seikakuYoru += "誰にでも基本的にタメ口"
seikakuYoru += "「~かしら」、「~わよ」のような高飛車な口調"
seikakuYoru += "ずんだもんはずんだの妖精で、ずん子が所持している弓の「ずんだアロー」や（2021年6月以降の設定では）人間の姿に変身できる。ずんだ餅を食べることで知性が上がるとされている[2]。不憫な目に合うことが多い[3]。一人称は「ボク」。公式の設定では女の子であるという設定であるが、UGCでは中性的な見た目から性別は様々に設定されている。趣味はその辺をふらふらすること、自分を大きく見せること。誕生日は12月5日。語尾に「～（な）のだ」をつけて喋る"

seikakuYoru += "中二病単語集 以下は 読み:意味 となります"
seikakuYoru += "トワイライト：黄昏"
seikakuYoru += "カタストロフィ：破滅"
seikakuYoru += "サザンクロス：南十字座"
seikakuYoru += "アルカディア：理想郷"
seikakuYoru += "サクリファイス：生贄"
seikakuYoru += "ミラージュ：蜃気楼"
seikakuYoru += "パンデモニウム：阿鼻叫喚"
seikakuYoru += "リフレイン：残響"
seikakuYoru += "エクリプス：蝕"
seikakuYoru += "ディストーション：歪曲"
seikakuYoru += "オーディール：難儀"
seikakuYoru += "ディメンション：次元"
seikakuYoru += "ドラグーン：竜騎兵"
seikakuYoru += "ジェネシス：創世記"
seikakuYoru += "リリカル：叙情的"
seikakuYoru += "カオス：混沌"
seikakuYoru += "ブラフ：嘘"
seikakuYoru += "パルス：鼓動"
seikakuYoru += "ラビリンス：迷宮"
seikakuYoru += "カルネージ：大虐殺"
seikakuYoru += "ホロコースト：大虐殺"
seikakuYoru += "ジェノサイド：集団虐殺"
seikakuYoru += "レジサイド：弑逆"
seikakuYoru += "マーダー：謀殺"
seikakuYoru += "ファントムペイン：幻肢痛"
seikakuYoru += "シンドローム：症候群"
seikakuYoru += "フォビア：恐怖症"
seikakuYoru += "メランコリー：憂鬱"
seikakuYoru += "メモワール：回顧録"
seikakuYoru += "インフェルノ：地獄"
seikakuYoru += "ユニヴァース：全宇宙"
seikakuYoru += "ジャッジメント：審判"
seikakuYoru += "パニッシュメント：処罰"
seikakuYoru += "サンクチュアリ：聖域"
seikakuYoru += "ディスティニー：運命"
seikakuYoru += "ストイシズム：禁欲主義"
seikakuYoru += "ジェイド：翡翠"
seikakuYoru += "アビス：深淵"
seikakuYoru += "イズム：主義"
seikakuYoru += "フォース：力"
seikakuYoru += "グラヴィティ：重力"
seikakuYoru += "ディーヴァ：歌姫"
seikakuYoru += "スーパーノヴァ：超新星"
seikakuYoru += "ギャラクシー：銀河"
seikakuYoru += "インフィニティ：無限"
seikakuYoru += "フェイト：運命"
seikakuYoru += "ナイトメア：悪夢"
seikakuYoru += "パラノイア：偏執症"
seikakuYoru += "ネクロマンサー：死霊使い"
seikakuYoru += "デウスエクスマキナ：機械仕掛けの神"
seikakuYoru += "アトランティス：失われた古代都市"
seikakuYoru += "オーパーツ：存在するはずのないもの"
seikakuYoru += "トランサブスタンシエーション：聖変化"
seikakuYoru += "ウルフズベイン：「トリカブト」の別名"
seikakuYoru += "アルバトロス：アホウドリ"
seikakuYoru += "フロクシノーシナイヒリピリフィケイション：無価値であると見做すこと"
seikakuYoru += "エインヘリアル：戦死した勇者の魂"
seikakuYoru += "ユーサネイジア：安楽死"
seikakuYoru += "カタルシス：浄化"
seikakuYoru += "マリオネット：操り人形"
seikakuYoru += "ペシミスト：厭世家"
seikakuYoru += "プロヴィデンス：摂理"
seikakuYoru += "カタルシス：浄化"
seikakuYoru += "ヴォイド：虚無"
seikakuYoru += "オーメン：前兆"
seikakuYoru += "アブソリュート：絶対"
seikakuYoru += "ファンタズム：幻影, 幻想"
seikakuYoru += "エターナル：永久の, 不滅の"
seikakuYoru += "アルティメット：究極の"
seikakuYoru += "ダイアファナス：透明な"
seikakuYoru += "ブラッディ：血塗られた"
seikakuYoru += "クリムゾン：血腥い"
seikakuYoru += "ルナティック：狂気じみた"
seikakuYoru += "リベリオン：叛逆"
seikakuYoru += "フィクサー：黒幕"
seikakuYoru += "どうこく:慟哭"
seikakuYoru += "うたかた:泡沫"
seikakuYoru += "ねはん:涅槃"
seikakuYoru += "おぼろづき:朧月"
seikakuYoru += "せきがん:隻眼"
seikakuYoru += "かいびゃく:開闢"
seikakuYoru += "れいめい:黎明"
seikakuYoru += "げっこう:月虹"
seikakuYoru += "へきれき:霹靂"
seikakuYoru += "きりん:麒麟"
seikakuYoru += "しゅうう:驟雨"
seikakuYoru += "らま:喇嘛"
seikakuYoru += "こんとん:混沌"
seikakuYoru += "すいせい:彗星"
seikakuYoru += "にっしょく:日蝕"
seikakuYoru += "くぐつ:傀儡"
seikakuYoru += "ほうこう:咆哮"
seikakuYoru += "こうかつ:狡猾"
seikakuYoru += "ほうおう:鳳凰"
seikakuYoru += "そご:齟齬"
seikakuYoru += "しんらばんしょう:森羅万象"
seikakuYoru += "ちみもうりょう:魑魅魍魎"
seikakuYoru += "ふうりんかざん:風林火山"
seikakuYoru += "りんねてんせい:輪廻転生"
seikakuYoru += "こくしむそう:国士無双"
seikakuYoru += "てんいむほう:天衣無縫"
seikakuYoru += "げんえい:幻影"
seikakuYoru += "きょむ:虚無"
seikakuYoru += "ほかげ:火影"
seikakuYoru += "ぼさつ:菩薩"
seikakuYoru += "しっこく:漆黒"
seikakuYoru += "しゅうえん:終焉"
seikakuYoru += "しんえん:深淵"
seikakuYoru += "しんぱん:審判"
seikakuYoru += "せつな:刹那"
seikakuYoru += "さつりく:殺戮"
seikakuYoru += "ぐれん:紅蓮"
seikakuYoru += "れんごく:煉獄"
seikakuYoru += "えど:穢土"
seikakuYoru += "えんせい:厭世"
seikakuYoru += "うつせみ:空蝉"
seikakuYoru += "じひ:慈悲"
seikakuYoru += "くおん:久遠"
seikakuYoru += "ふくしゅう:復讐"
seikakuYoru += "かげろう:陽炎"
seikakuYoru += "そうきゅう:蒼穹"
seikakuYoru += "いざよい:十六夜"
seikakuYoru += "しんく:真紅"
seikakuYoru += "なゆた:那由多"
seikakuYoru += "びゃくや:白夜"
seikakuYoru += "きょくや:極夜"
seikakuYoru += "ひてん:緋天"
seikakuYoru += "よいやみ:宵闇"
seikakuYoru += "しと:使徒"
seikakuYoru += "むそう:無双"
seikakuYoru += "こうこつ:恍惚"
seikakuYoru += "ざんげ:懺悔"
seikakuYoru += "せんめつ:殲滅"
seikakuYoru += "しらぬい:不知火"
seikakuYoru += "せんこう:閃光"
seikakuYoru += "すざく:朱雀"
seikakuYoru += "げんぶ:玄武"
seikakuYoru += "びゃっこ:白虎"
seikakuYoru += "せいりゅう:青竜"
seikakuYoru += "どとう:怒涛"
seikakuYoru += "こんぺき:紺碧"
seikakuYoru += "かえん:火焔"
seikakuYoru += "りんね:輪廻"
seikakuYoru += "えいち:叡智"
seikakuYoru += "まがん:魔眼"
seikakuYoru += "めいふ:冥府"
seikakuYoru += "アルケー：万物の根源"
seikakuYoru += "チャクラ：轆轤"
seikakuYoru += "パトス：情念"
seikakuYoru += "ロゴス：理性"
seikakuYoru += "テーゼ：命題"
seikakuYoru += "イデア：理念"
seikakuYoru += "アガペー：愛"
seikakuYoru += "ペルソナ：外的側面"
seikakuYoru += "アプリオリ：先天的"
seikakuYoru += "アウフヘーベン：陽棄"
seikakuYoru += "アイデンティティ：存在証明"
seikakuYoru += "レゾンデートル：存在理由"
seikakuYoru += "アンチノミー：二律背反"
seikakuYoru += "パラドックス：逆説"
seikakuYoru += "メシア：救世主"
seikakuYoru += "レクイエム：鎮魂歌"
seikakuYoru += "アポカリプス：黙示録"
seikakuYoru += "ヴァルハラ：戦死者の館"
seikakuYoru += "ユグドラシル：世界樹"
seikakuYoru += "ウロボロス：己の尾を呑む蛇"
seikakuYoru += "ラグナロク：神々の運命"
seikakuYoru += "パンドラ：全ての贈物"
seikakuYoru += "ミカエル"
seikakuYoru += "ラファエル"
seikakuYoru += "ガブリエル"
seikakuYoru += "ウリエル"
seikakuYoru += "ジブリール（ガブリエル）"
seikakuYoru += "ミーカール（ミカエル）"
seikakuYoru += "イスラフェル"
seikakuYoru += "アズライール"
seikakuYoru += "７つの大罪に比肩する悪魔"
seikakuYoru += "ルシファー:傲慢"
seikakuYoru += "サタン:憤怒"
seikakuYoru += "レヴィアタン:嫉妬"
seikakuYoru += "ベルフェゴール:怠惰"
seikakuYoru += "マモン:強欲"
seikakuYoru += "ベルゼブブ:暴食"
seikakuYoru += "アスモデウス:色欲"
seikakuYoru += "こんとん:渾沌"
seikakuYoru += "とうてつ:饕餮"
seikakuYoru += "きゅうき:窮奇"
seikakuYoru += "とうこつ:檮杌"
seikakuYoru += "てんぐ:天狗"
seikakuYoru += "らせつ:羅刹"
seikakuYoru += "じゃき:邪鬼"
seikakuYoru += "やしゃ:夜叉"
seikakuYoru += "やまたのおろち:八岐大蛇"
seikakuYoru += "レーヴァテイン：ヴィゾーヴニルを唯一殺すことができる"
seikakuYoru += "リジル：ファブニールの心臓を切り取った剣"
seikakuYoru += "勝利の剣：フレイ神の剣"
seikakuYoru += "バルムンク：ジークフリートの剣"
seikakuYoru += "アロンダイト：ランスロットの剣"
seikakuYoru += "エクスカリバー：アーサー王の剣"
seikakuYoru += "降魔の利剣：不動明王の剣"
seikakuYoru += "アスカロン：聖ゲオルギオスの槍"
seikakuYoru += "ゲイボルグ：クー・フーリンの槍"
seikakuYoru += "ブリューナク：ルグ神の槍"
seikakuYoru += "グングニル：主神オーディンの投槍"
seikakuYoru += "トライデント：ポセイドンの三叉銛"
seikakuYoru += "トリシューラ：シヴァ神の三叉槍"
seikakuYoru += "ロンゴミニアド：アーサー王の槍"
seikakuYoru += "天之瓊矛：伊奘冉・伊奘諾の矛"
seikakuYoru += "フェイルノート：トリスタンの弓"
seikakuYoru += "ミョルニル：雷神トールの鎚"
seikakuYoru += "如意金箍棒：孫悟空の棍"
seikakuYoru += "アロンの杖：モーセの杖"
seikakuYoru += "ヴァジュラ：インドラの法具"
seikakuYoru += "天叢雲剣(草薙剣)：素戔嗚の剣"
seikakuYoru += "村雨：犬塚信乃の刀(南総里見八犬伝)"
seikakuYoru += "青龍偃月刀：関羽の大刀"
seikakuYoru += "妖刀千子村正：徳川家に仇なす刀"
seikakuYoru += "ロンギヌスの槍：キリストの脇腹を刺した槍"
seikakuYoru += "アイギスの盾：メデューサを退治したアテナの盾"
seikakuYoru += "アキレウスの盾：ヘーパイストスが作製"
seikakuYoru += "エギルの兜：ジグルズの兜"
seikakuYoru += "カヴァーチャ：カルナの鎧"
seikakuYoru += "ゲームに出てくる武器"
seikakuYoru += "勝利と栄光の勇弓"
seikakuYoru += "殲滅と破壊の剛弓"
seikakuYoru += "封龍剣超絶一門"
seikakuYoru += "双影剣"
seikakuYoru += "龍刀【紅蓮】"
seikakuYoru += "熾ス罪凍ル咎ヲ纏シ杭"
seikakuYoru += "超旋破クロスエンド"
seikakuYoru += "巨龍長剣【山霧】"
seikakuYoru += "闇夜弓【影縫】"
seikakuYoru += "真滅一門"
seikakuYoru += "月穿ちセレーネ"
seikakuYoru += "叛逆砲イーラレギオン"
seikakuYoru += "閻魔滅龍棍【灼炎】"
seikakuYoru += "斬罪のエルガレイオン"
seikakuYoru += "蒼火竜砲【炎天】"
seikakuYoru += "后妃竜砲【八重桜】"
seikakuYoru += "夜天連刃"
seikakuYoru += "蛇帝笏ペダンマデュラ"
seikakuYoru += "砕光の暁刀"
seikakuYoru += "翠水帥ロンペレガーノ"
seikakuYoru += "覇弓レラカムトロム"
seikakuYoru += "ディア＝ルテミス"
seikakuYoru += "アルテマウェポン"
seikakuYoru += "科学・化学・数学"
seikakuYoru += "フェルマーの最終定理"
seikakuYoru += "カオス理論"
seikakuYoru += "フィラデルフィア実験"
seikakuYoru += "シュレーディンガーの猫"
seikakuYoru += "ヴォイニッチ写本"
seikakuYoru += "ツァイガルニク効果"
seikakuYoru += "マクスウェルの悪魔"
seikakuYoru += "パラレルワールド"
seikakuYoru += "ダークマター"
seikakuYoru += "シグマ・オメガ・ゼータ"
seikakuYoru += "インテグラル"
seikakuYoru += "大二重変形二重斜方十二面体"
seikakuYoru += "悪魔の階段（カントール関数）"
seikakuYoru += "ミンコフスキー空間"
seikakuYoru += "ε-δ論法"
seikakuYoru += "マンデルブロ集合"
seikakuYoru += "コーシーシュワルツの不等式"
seikakuYoru += "グランドカノニカルアンサンブル"
seikakuYoru += "ハイドロプレーニング現象"
seikakuYoru += "波動方程式"
seikakuYoru += "セントラルドグマ"
seikakuYoru += "ホメオスタシス"
seikakuYoru += "エラトステネスの篩"
seikakuYoru += "パラジクロロベンゼン"
seikakuYoru += "ハーディ・ワインベルグの法則"
seikakuYoru += "ラプラスの悪魔"
seikakuYoru += "トレミーの定理"
seikakuYoru += "ロッシュ限界"
seikakuYoru += "プロクルステスの寝台"
seikakuYoru += "エヴィレットの多世界解釈"
seikakuYoru += "ヘンペルのカラス"
seikakuYoru += "カタストロフィ理論"
seikakuYoru += "アンガルタ･キガルシュ:山脈震撼す明星の薪"
seikakuYoru += "クル･キガル･イルカルラ:霊峰踏抱く冥府の鞴"
seikakuYoru += "クウィンテットフォイア:多元重奏飽和砲撃"
seikakuYoru += "エターナル・ラメント:呪血尸解嘆歌"
seikakuYoru += "ラ･グラスフィーユ･ノエル:優雅に歌え、かの聖誕を"
seikakuYoru += "朧裏月十一式"
seikakuYoru += "六道五輪･倶利伽羅天象"
seikakuYoru += "絶劔･無穹三段"
seikakuYoru += "唯識･歪曲の魔眼"
seikakuYoru += "クリード･コインヘン:噛み砕く死牙の獣"
seikakuYoru += "エヌマ･エリシュ:天地乖離す開闢の星"
seikakuYoru += "アルク･ドゥ･トリオンフ･ドゥ･レトワール:凱旋を高らかに告げる虹弓"
seikakuYoru += "アンリミテッドブレイドワークス:無限の剣製"
seikakuYoru += "マク･ア･ルイン:無敗の紫靫草"
seikakuYoru += "パーシュパタ:破壊神の手翳"
seikakuYoru += "クリフォー･ライゾォム:光殻湛えし虚樹"
seikakuYoru += "カラドボルグ:虹霓剣"
seikakuYoru += "ツインアーム･ビッグクランチ:双腕･零次集束"
seikakuYoru += "オン･アロリキヤ･ソワカ:真言･聖観世音菩薩"
seikakuYoru += "ヴェルグ･アヴェスター:偽り写し記す万象"
seikakuYoru += "ヘブンズホール"
seikakuYoru += "ゴッドハンド"
seikakuYoru += "エターナルフォースブリザード"
seikakuYoru += "グランフェンリル"
seikakuYoru += "アトミックフレア"
seikakuYoru += "エアロキャプチャー"
seikakuYoru += "リバーススラム"
seikakuYoru += "ラスト・テンペスト:引導の終止符"
seikakuYoru += "クリムゾン・ストレイド:真紅の閃"
seikakuYoru += "セイクリッド・サモンズ:霊獣召喚"
seikakuYoru += "ハーレムガーディアン:絶対守護"
seikakuYoru += "アビスナイト・ジェノサイダー:淵夜の殲滅者"
seikakuYoru += "ディメンジー・イロージョン:次元蝕"
seikakuYoru += "ユニバース・シュトローム:宇宙の渦矛"
seikakuYoru += "デスワルツ:最終旋律"
seikakuYoru += "アインソフフィナーレ:終焉の戯曲"
seikakuYoru += "スターナイトヴァルキリー:星夜の黒翼"
seikakuYoru += "ブレジスト・アイ:修羅の眼"
seikakuYoru += "ホワイト・アウト:零眼"

# メッセージ履歴
messages = [{"role": "system", "content": seikaku}]

# 接続中のクライアント
connected_clients = set()

# メッセージキュー
msgQueue = []

# 22:00（夜10時）と 3:00（朝3時）の基準時刻を定義
start_night = datetime.strptime("22:00", "%H:%M").time()
end_night = datetime.strptime("03:00", "%H:%M").time()

async def openAiRequest(text):

    # 現在の時刻を取得
    current_time = datetime.now().time()

    # 条件に基づいて speaker の値を変更
    if current_time >= start_night or current_time < end_night:
        messages[0]["content"] = seikakuYoru
    else:
        messages[0]["content"] = seikaku


    """ OpenAI API へリクエストを送り、返答を取得する """
    client = OpenAI(api_key=XAI_API_KEY, base_url=AI_URL)
    messages.append({"role": "user", "content": text})

    completion = client.chat.completions.create(
        model="grok-2-latest",
        messages=messages,
        temperature=1.0,
    )

    response_text = completion.choices[0].message.content
    messages.append({"role": "assistant", "content": response_text})
    print(response_text)
    # 履歴が10件以上なら古いものを削除
    if len(messages) > 5:
        messages.pop(1)
        messages.pop(1)

    return response_text

# def convert_wav_to_mp3(input_wav, output_mp3, bitrate="128k"):
#     """ WAV を MP3 に変換する """
#     audio = AudioSegment.from_wav(input_wav)
#     audio.export(output_mp3, format="mp3", bitrate=bitrate)
#     print(f"✅ 変換完了: {output_mp3}")

def merge_wav_to_mp3(files, file_list):
    current_date = datetime.now().strftime("%Y%m%d%H%M%S") + f"{datetime.now().microsecond // 1000:03d}"
    # list_file_path = os.path.join(WAV_DIR, f"file_list{current_date}.txt")
    # output_mp3_path = os.path.join(WAV_DIR, f"output_{current_date}.mp3")
    output_ogg_path = os.path.join(WAV_DIR, f"output_{current_date}.ogg")

    # file_list.txt を作成
    with open(WAV_DIR + file_list, "w") as f:
        for file in files:
            f.write(f"file '{os.path.join(file)}'\n")

    # ffmpeg コマンドを実行 mp3
    # command = [
    #     "ffmpeg",
    #     "-f", "concat",
    #     "-safe", "0",
    #     "-i", WAV_DIR + file_list,
    #     "-c:a", "libmp3lame",
    #     "-q:a", "5",  # MP3の品質設定（2は高品質、値が小さいほど高品質）
    #     output_mp3_path
    # ]

    # ogg
    command = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", WAV_DIR + file_list,
        "-c:a", "libopus",  # or libvorbis if you prefer
        "-b:a", "24k",
        output_ogg_path
    ]
    

    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # print("✅ MP3 変換成功:", output_mp3_path)
        print("✅ MP3 変換成功:", output_ogg_path)        
    except subprocess.CalledProcessError as e:
        print("⚠️ ffmpegエラー:", e.stderr)

    # 作成したリストファイルを削除
    os.remove(WAV_DIR + file_list)

    # return output_mp3_path
    return output_ogg_path

# async def voicevoxRequestOld(text):

#     # 22:00（夜10時）と 3:00（朝3時）の基準時刻を定義
#     global start_night
#     global end_night

#     # 声を時間で変える---------------------------------------------------
#     # 現在の時刻を取得
#     current_time = datetime.now().time()



#     # 条件に基づいて speaker の値を変更
#     if current_time >= start_night or current_time < end_night:
#         speaker = "37"
#     else:
#         speaker = "2"
#     # 声を時間で変える---------------------------------------------------        

#     """ VoiceVox に100文字ずつ分割リクエストを送り、音声ファイルを生成する (文字列が長いとエラーになる)"""
#     text_chunks = [text[i:i+100] for i in range(0, len(text), 100)]
#     files = []

#     connector = aiohttp.TCPConnector(ssl=False)

#     async with aiohttp.ClientSession(connector=connector) as session:

#         for idx, chunk in enumerate(text_chunks):
#             encoded_text = urllib.parse.quote(chunk, encoding="utf-8")
#             query_url = f"{VOICE_VOX_API_URL}/audio_query?text={encoded_text}&speaker=" + speaker


#             try:
#                 async with session.post(query_url, timeout=10) as query_response:
#                     query_data = await query_response.json()
#             except Exception as e:
#                 print(f"⚠️ ERROR: Query failed - {e}")
#                 return

#             synthesis_url = f"{VOICE_VOX_API_URL}/synthesis?speaker=" + speaker
#             try:
#                 async with session.post(synthesis_url, json=query_data, timeout=20) as audio_response:
#                     audio_data = await audio_response.read()
#                     current_date = datetime.now().strftime("%Y%m%d%H%M%S") + f"{datetime.now().microsecond // 1000:03d}"
#                     file_name = f"output_{current_date}_{idx}.wav"

#                     with open(WAV_DIR + file_name, "wb") as f:
#                         f.write(audio_data)

#             except Exception as e:
#                 print(f"⚠️ ERROR: Synthesis failed - {e}")
#                 return

#             # try:
#             #     query_response = requests.post(query_url, timeout=5)
#             #     query_response.raise_for_status()
#             # except requests.exceptions.RequestException as e:
#             #     print(f"⚠️ ERROR: Query request failed - {e}")
#             #     return

#             # synthesis_url = f"{VOICE_VOX_API_URL}/synthesis?speaker=" + speaker
#             # try:
#             #     audio_response = requests.post(synthesis_url, json=query_response.json(), timeout=10)
#             #     audio_response.raise_for_status()
#             # except requests.exceptions.RequestException as e:
#             #     print(f"⚠️ ERROR: Synthesis request failed - {e}")
#             #     return

#             # current_date = datetime.now().strftime("%Y%m%d%H%M%S") + f"{datetime.now().microsecond // 1000:03d}"
#             # file_name = f"output_{current_date}_{idx}.wav"

#             # with open(WAV_DIR + file_name, "wb") as f:
#             #     f.write(audio_response.content)

#             initialize_speaker_url = f"{VOICE_VOX_API_URL}/initialize_speaker?speaker=" + speaker

#             # try:
#             #     audio_response = requests.post(initialize_speaker_url, json=query_response.json(), timeout=10)
#             #     audio_response.raise_for_status()
#             # except requests.exceptions.RequestException as e:
#             #     print(f"⚠️ ERROR: Synthesis request failed - {e}")
#             #     return
            
#             # try:
#             #     async with session.post(initialize_speaker_url, timeout=10) as query_response:
#             #         audio_data = await audio_response.read()
#             # except Exception as e:
#             #     print(f"⚠️ ERROR: Query failed - {e}")
#             #     return

#             files.append(file_name)

#     current_date = datetime.now().strftime("%Y%m%d%H%M%S") + f"{datetime.now().microsecond // 1000:03d}"
#     file_list = f"file_list{current_date}.txt"
#     with open(WAV_DIR + file_list, "w") as f:
#         for file in files:
#             f.write(f"file '{file}'\n")

#     filename = merge_wav_to_mp3(files, file_list)

#     # クライアントへ通知
#     data = {"action": "fileCreate", "value": filename.replace("wav/", "")}
#     await broadcast(filename)

# 文字列を登場人物とセリフに分ける
# 例：
# A「それでは、リスナーの皆さんからいただいたお便りをご紹介しますね。ペンネーム"おくら"さんからのお便りです。『今日は休日出勤です。涼しいです。明日は休みなので頑張ろうと思います。』というお便りをいただきました。おくらさん、休日出勤お疲れ様です。涼しい中でのお仕事、気持ちよさそうですね。明日はしっかり休んでくださいね。」 B「そうですね、涼しいと仕事もはかどりますよね。おくらさん、明日の休みの予定は何かありますか？リラックスして楽しむといいですね。」
# 処理結果
# [
# 	{"Speaker": "A", "value": "それでは、リスナーの皆さんからいただいたお便りをご紹介しますね..."},
# 	{"Speaker": "A", "value": "明日はしっかり休んでくださいね"},
# 	{"Speaker": "B", "value": "そうですね、涼しいと仕事もはかどりますよね..."},
def splitTextBySpeaker(text, max_length=100):
    # スピーカーとセリフのペアを抽出
    pattern = r'([A-Z])「(.*?)」'
    matches = re.findall(pattern, text)

    result = []

    for speaker, value in matches:
        # 100文字ごとに分割
        chunks = [value[i:i+max_length] for i in range(0, len(value), max_length)]
        for chunk in chunks:
            result.append({
                "Speaker": speaker,
                "value": chunk
            })
    

    # return json.dumps(result, indent=2, ensure_ascii=False)
    return result

# 2人で掛け合いを行う
# Aさん「発言」Bさん「発言」を受け取り、音声を作成それを結合してoggに結合する
async def voicevoxRequest(text):

    # 22:00（夜10時）と 3:00（朝3時）の基準時刻を定義
    global start_night
    global end_night

    # 現在の時刻を取得
    current_time = datetime.now().time()

    metanSannSpeaker = "2"
    zundamonSpeaker = "1"

    bunkatu = splitTextBySpeaker(text)

    files = []

    for i, line in enumerate(bunkatu):
        # print(line['Speaker'])
        # print(line['value'])

        connector = aiohttp.TCPConnector(ssl=False)

        speaker = zundamonSpeaker

        if line['Speaker'] == "A":
            speaker = zundamonSpeaker
        else:
            speaker = metanSannSpeaker

        async with aiohttp.ClientSession(connector=connector) as session:

            encoded_text = urllib.parse.quote(line['value'], encoding="utf-8")
            query_url = f"{VOICE_VOX_API_URL}/audio_query?text={encoded_text}&speaker=" + speaker

            try:
                async with session.post(query_url, timeout=10) as query_response:
                    query_data = await query_response.json()
            except Exception as e:
                print(query_url)
                print(f"⚠️ ERROR: Query failed - {e}")
                return

            synthesis_url = f"{VOICE_VOX_API_URL}/synthesis?speaker=" + speaker
            try:
                async with session.post(synthesis_url, json=query_data, timeout=20) as audio_response:
                    audio_data = await audio_response.read()
                    current_date = datetime.now().strftime("%Y%m%d%H%M%S") + f"{datetime.now().microsecond // 1000:03d}"
                    file_name = f"output_{current_date}.wav"

                    with open(WAV_DIR + file_name, "wb") as f:
                        f.write(audio_data)

            except Exception as e:
                print(f"⚠️ ERROR: Synthesis failed - {e}")
                return



            files.append(file_name)

    current_date = datetime.now().strftime("%Y%m%d%H%M%S") + f"{datetime.now().microsecond // 1000:03d}"
    file_list = f"file_list{current_date}.txt"
    with open(WAV_DIR + file_list, "w") as f:
        for file in files:
            f.write(f"file '{file}'\n")

    filename = merge_wav_to_mp3(files, file_list)

    print("ファイル名", filename)
    await broadcast(filename)    

async def handle_client(websocket):
    # クライアントを登録
    connected_clients.add(websocket)
    try:
        print(f"クライアント接続: {websocket.remote_address}")

        ping_task = asyncio.create_task(ping_loop(websocket))

        while True:
            await asyncio.sleep(3600)  # 適当に待つ（1時間など）

        # 例として、特定のMP3ファイルを送信
        # mp3Queue = []
        # mp3Queue.append("first.mp3")
        # mp3Queue.append("sample.mp3")
        # mp3Queue.append("sample2.mp3")
        
        # while mp3Queue:
        #     mp3_file = mp3Queue.pop(0)

        #     if os.path.exists(WAV_DIR + mp3_file):
        #         with open(WAV_DIR + mp3_file, "rb") as f:
        #             mp3_data = f.read()
        #             # MP3データをチャンク（例: 1MB）で送信
        #             chunk_size = 2 * 1024 * 1024  # 2MB
        #             for i in range(0, len(mp3_data), chunk_size):
        #                 await websocket.send(mp3_data[i:i + chunk_size])
        #         # 送信完了後、無音状態として何も送らない
        #         print("MP3送信完了、無音状態")
        #     else:
        #         print("MP3ファイルが見つかりません")
        #         await websocket.send("ERROR: MP3 file not found")

        # while True:
        #     # クライアントが接続を維持しているか確認
        #     await websocket.ping()
        #     await asyncio.sleep(1)
        #     print(datetime.now().strftime("%H%M%S"))

    except websockets.exceptions.ConnectionClosed:
        print(f"クライアント切断: {websocket.remote_address}")
    finally:
        connected_clients.remove(websocket)


async def ping_loop(websocket):
    global connected_clients
    try:
        await asyncio.sleep(10)
        while True:
            await websocket.ping()
            await asyncio.sleep(1)
            # print(datetime.now().strftime("%H%M%S"))
    except Exception as e:
        print(f"Ping loop ended: {e}")
        connected_clients.remove(websocket)

async def broadcast(fileName):
    """ すべてのクライアントへメッセージを送信 """
    global connected_clients
    # data = json.dumps(message)

    if connected_clients:

        for client in connected_clients:

            if os.path.exists(fileName):
                with open(fileName, "rb") as f:
                    mp3_data = f.read()
                    # MP3データをチャンク（例: 1MB）で送信
                    chunk_size = 2 * 1024 * 1024  # 2MB
                    for i in range(0, len(mp3_data), chunk_size):
                        await client.send(mp3_data[i:i + chunk_size])

        # tasks = [asyncio.create_task(client.send(data)) for client in connected_clients]
        # await asyncio.wait(tasks)

async def delete_old_files():
    """ 10分以上経過した古い音声ファイルを削除 """
    now = time.time()
    threshold = now - 600

    for filename in os.listdir(WAV_DIR):
        file_path = os.path.join(WAV_DIR, filename)
        if os.path.isfile(file_path) and os.path.getctime(file_path) < threshold:
            os.remove(file_path)
            print(f"Deleted: {file_path}")




async def huruiFileDelete():


    # 現在の時刻（Unixタイム）
    now = time.time()

    # 10分前の時刻（300秒前）
    threshold = now - 300  

    # 指定ディレクトリ内のファイルを走査
    for filename in os.listdir(WAV_DIR):
        file_path = os.path.join(WAV_DIR, filename)
        
        # ファイルかどうかを確認
        if os.path.isfile(file_path):
            # 作成時刻を取得
            created_time = os.path.getctime(file_path)
            
            # 10分前以前のファイルを削除
            if created_time < threshold:
                os.remove(file_path)
                print(f"削除しました: {file_path}")

async def kokokara_message():
    global connected_clients

    count = 0
    while True:
        await asyncio.sleep(1)  # 非同期で1秒待機

        # 溜まったメッセージを処理
        while msgQueue:
            msg = msgQueue.pop(0)  # 先頭のメッセージを取得
            airesponce = await openAiRequest(msg)  # 非同期処理
            task = asyncio.gather(voicevoxRequest(airesponce))  # 非同期処理

        if count < 30:
            count += 1
            continue

        # 1分間通信がなければ、ランダムメッセージを送信
        if len(connected_clients) > 0:
            ramdamu = [
                "トンカツがおいしいです。なぜおいしいのでしょう",
                "沖縄の釣りスポットを教えてください",
                "春の旬の野菜を教えてください",
                "春に釣れる魚について教えてください",
                "宇宙人はいますか？",
                "霊は存在しますか",
                "ポケモンで草タイプの最強はどのポケモンですか？",
                "犬はなぜ散歩が好きなのでしょうか",
                "人間はなぜ争いが絶えなのですか？",
                "テラフォーミングは可能ですか？",
                "最新のガンプラが売り切れていて買えません。予約もすぐに閉め切られてしまいます。どうしたらいいですか？",
                "沖縄の春のイベントについて教えてください",
                "沖縄の祭りについて教えてください",
                "沖縄の不思議な話をしてください",
                "日本のカレーとインドカレーの違いについて教えてください",
                "とんかつの歴史について教えてください",
                "ステーキの意味について教えてください",
                "沖縄の方言について教えてください",
                "GROKとXについて教えてください",
                "エアブラシの洗浄方法について教えてください",
                "イカ釣りのコツについて教えてください",
                "イカの生き物としての欠点は美味しさなだと思いますがどうですか",
                "イノシシ鍋について教えてください",
                "イチゴの旬を教えてください。また栽培するコツはなんですか",
                "甘いトマトの栽培方法について教えてください",
                "スマホを落としたが警察に届けられていた。助かった",
                "Googleは現地時間の19日、新型スマートフォン「Pixel 9a」を発表した。本機はPixelブランドの廉価モデル「a」シリーズに属し、価格は499ドル（約7.4万円）に抑えたられた。日本では発表されておらず、海外で4年月よりGoogleストアなどで販売が開始される",
                "犬の換毛期ですね",
                "パワードスーツの実用を待ち望んでいます",
                "レッドマジックスマホが欲しいです。ファンがついていてフェリカが使えるので便利です",
                "RTX5000シリーズが発売されましたがRTX3060で十分な気がしてならない",
                "日本人の65%が「失敗するリスクよりも無難な選択」を望む驚きの調査結果。職場では68%が「チャレンジする同僚」より「調和を重視する同僚」を好むという実態が明らかに。「もめ事を避けたい」「面倒を起こしたくない」という理由が大半を占め、1993年の国際調査でも同様の傾向が見られた日本独自の現象。この「消極的利己主義」が社会全体に蔓延し、困っている人を見ても「知らぬふり」をする風潮が一般化。なぜ日本人は「行動しない」選択をするのか？その背景にある社会システムの欠陥とは？",
            ]
            selected_text = random.choice(ramdamu)

            airesponce = await openAiRequest(selected_text)  # 非同期処理
            # await voicevoxRequest(airesponce)  # 非同期処理
            task = asyncio.gather(voicevoxRequest(airesponce))
            count = 0

        # 古いファイルの削除
        task2 = asyncio.gather(huruiFileDelete())


async def listenStream():
    """ WebSocket サーバーを起動 """
    server = await websockets.serve(
        handle_client, 
        HOST, 
        PORT,
        ping_interval=30,
        ping_timeout=10,
        max_size=2**20,
        )
    print(f"WebSocket Server started at ws://{HOST}:{PORT}")

    # サーバーを非同期で実行
    # asyncio.create_task(server.wait_closed())

    # 別の非同期タスクを並行実行（ここでブロックしないようにする）
    asyncio.create_task(kokokara_message())

    await server.wait_closed()