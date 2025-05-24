import os
import requests

'''開発用のテスト的なコードです'''


url = "https://api.x.ai/v1/chat/completions"
# headers = {
#     "Content-Type": "application/json",
#     "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}"
# }
# payload = {
#     "messages": [
#         {
#             "role": "user",
#             "content": "昨日の株式市場はどうでしたか？"
#         }
#     ],
#     "search_parameters": {
#         "mode": "auto"
#     },
#     "model": "grok-3-latest"
# }

# response = requests.post(url, headers=headers, json=payload)
# print(response.json())

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

messages = [{"role": "system", "content": seikakuYoru}]

def openAiRequest(text):
    # # 現在の時刻を取得
    # current_time = datetime.now().time()

    # # 条件に基づいて speaker の値を変更
    # if current_time >= start_night or current_time < end_night:
    #     messages[0]["content"] = seikakuYoru
    # else:
    #     messages[0]["content"] = seikaku



    m = {"role": "user", "content": text}

    messages.append(m)

    """ OpenAI API へリクエストを送り、返答を取得する """
    # client = OpenAI(api_key=XAI_API_KEY, base_url=AI_URL)
    # messages.append({"role": "user", "content": text})

    # completion = client.chat.completions.create(
    #     model="grok-2-latest",
    #     messages=messages,
    #     temperature=1.0,
    # )

    # response_text = completion.choices[0].message.content

    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}"
    }

    payload = {
        "messages": messages,
        "search_parameters": {
            "mode": "auto"
        },
        "model": "grok-3-latest"
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"APIリクエストが失敗しました: {response.status_code}, {response.text}")

    res = response.json()

    try:
        res = response.json()
        print("JSONレスポンス:", res)
        print(res['choices'][0]['message']['content'])

    except requests.exceptions.JSONDecodeError as e:
        print(f"JSONデコードエラー: {e}")
        print(f"レスポンス内容: {response.text}")
        return None


openAiRequest('ドラクエの日が待ち遠しいです。ドラクエウォークのイベントが楽しみです')