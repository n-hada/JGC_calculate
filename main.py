# --- 計算ロジック ---
def calculate_lsp(inputs):
    """
    年間のLSP獲得量を計算し、結果を文字列として返します。
    
    Args:
        inputs (dict): ユーザーが入力した値を含む辞書
        
    Returns:
        str: 表示用のシミュレーション結果文字列
    """

    # --- 計算設定 ---
    TARGET_LSP = inputs['target_lsp']
    JPY_PER_JAL_CARD_MILE = 200  # JALカードの1マイル獲得に必要な円

    total_lsp = 0
    breakdown = {}

    # 1. 搭乗ポイント
    flight_lsp = (inputs['annual_domestic_flights'] * 5) + ((inputs['annual_international_miles'] // 1000) * 5)
    if flight_lsp > 0:
        breakdown['搭乗'] = flight_lsp
    total_lsp += flight_lsp

    # 2. JALカード決済ポイント (★航空券代を加算して計算)
    flight_costs = inputs['annual_domestic_flights'] * inputs['cost_per_domestic_flight_jpy']
    total_card_spending = inputs['annual_jal_card_spending_jpy'] + flight_costs

    miles_from_card = total_card_spending // JPY_PER_JAL_CARD_MILE
    card_lsp = (miles_from_card // 2000) * 5
    if card_lsp > 0:
        breakdown['JALカード決済'] = card_lsp
    total_lsp += card_lsp

    # 3. JAL Payポイント
    jal_pay_lsp = inputs['annual_jal_pay_miles'] // 500
    if jal_pay_lsp > 0:
        breakdown['JAL Pay利用'] = jal_pay_lsp
    total_lsp += jal_pay_lsp

    # 4. JAL Mallポイント
    jal_mall_lsp = inputs['annual_jal_mall_miles'] // 100
    if jal_mall_lsp > 0:
        breakdown['JAL Mall利用'] = jal_mall_lsp
    total_lsp += jal_mall_lsp

    # 5. ジャルパックポイント (2025/7/1以降のルール)
    jalpak_lsp = (inputs['jalpak_domestic_tours'] * 3) + (inputs['jalpak_overseas_tours'] * 10)
    if jalpak_lsp > 0:
        breakdown['ジャルパック利用'] = jalpak_lsp
    total_lsp += jalpak_lsp

    # 6. サブスク系サービス
    subscription_lsp = (inputs['jal_wellness_months'] +
                        inputs['jal_denki_months'] +
                        inputs['jal_hikari_months'] +
                        inputs['jal_mobile_months'])
    if subscription_lsp > 0:
        breakdown['サブスクリプションサービス'] = subscription_lsp
    total_lsp += subscription_lsp

    # 7. JALふるさと納税
    furusato_lsp = inputs['annual_furusato_nozei_jpy'] // 10000
    if furusato_lsp > 0:
        breakdown['JALふるさと納税'] = furusato_lsp
    total_lsp += furusato_lsp

    # --- 結果を文字列として生成 ---
    result_lines = []
    result_lines.append("--- 年間LSP獲得シミュレーション結果 ---")
    result_lines.append(f"\n航空券代を含むJALカード年間決済総額: {total_card_spending:,} 円")
    result_lines.append(f"年間の合計獲得LSP: {total_lsp} LSP")
    
    result_lines.append("\n【内訳】")
    if not breakdown:
        result_lines.append("LSPを獲得できる活動がありません。")
    else:
        for service, points in sorted(breakdown.items()):
            result_lines.append(f"- {service}: {points} LSP")

    result_lines.append("\n--- 目標達成までの期間 ---")
    if total_lsp > 0:
        years_to_reach_target = TARGET_LSP / total_lsp
        result_lines.append(f"目標の {TARGET_LSP} LSP に到達するまで…")
        result_lines.append(f"約 {years_to_reach_target:.1f} 年")
    else:
        result_lines.append("このペースでは目標を達成できません。")

    return "\n".join(result_lines)


# --- CUIで入力を受け付ける関数 ---
def run_simulator_cli():
    """ターミナルでユーザーから入力を受け取り、シミュレーションを実行する"""
    
    # 入力項目とプロンプト、デフォルト値の定義
    input_prompts = {
        # 'key': ('プロンプトのテキスト', 'カテゴリ名', default_value)
        'target_lsp': ('目標LSP', '目標設定', 1500),

        # 1. 搭乗でためる
        'annual_domestic_flights': ('国内線の年間搭乗回数（片道）', '1. 搭乗', 0),
        'cost_per_domestic_flight_jpy': ('国内線1搭乗あたりの平均運賃（円）', '1. 搭乗', 0),
        'annual_international_miles': ('国際線の年間搭乗区間マイル（合計）', '1. 搭乗', 0),

        # 2. 金融・決済
        'annual_jal_card_spending_jpy': ('JALカードの年間決済額（円） ※航空券代を除く', '2. 金融・決済',  0),
        'annual_jal_pay_miles': ('JAL Payで年間獲得するマイル数', '2. 金融・決済', 0),

        # 3. ショッピング
        'annual_jal_mall_miles': ('JAL Mallで年間獲得するマイル数', '3. ショッピング', 0),

        # 4. トラベル (2025/7/1以降)
        'jalpak_domestic_tours': ('ジャルパック国内ツアーの年間利用回数', '4. トラベル', 0),
        'jalpak_overseas_tours': ('ジャルパック海外ツアーの年間利用回数', '4. トラベル', 0),

        # 5. 生活・インフラ
        'jal_wellness_months': ('JAL Wellness & Travelの年間利用月数 (0-12)', '5. 生活・インフラ', 0),
        'jal_denki_months': ('JALでんきの年間利用月数 (0-12)', '5. 生活・インフラ', 0),
        'jal_hikari_months': ('JAL光の年間利用月数 (0-12)', '5. 生活・インフラ', 0),
        'jal_mobile_months': ('JALモバイルの年間利用月数 (0-12)', '5. 生活・インフラ', 0),
        'annual_furusato_nozei_jpy': ('JALふるさと納税の年間寄附額（円）', '5. 生活・インフラ', 0),
    }

    user_inputs = {}
    
    print("--- JAL Life Status ポイント(LSP) 年間獲得シミュレーター ---")
    print("各項目に数値を入力してください。")
    print("何も入力せずにEnterキーを押すと、デフォルト値が使用されます。\n")

    for key, (prompt_text, category, default) in input_prompts.items():
        # ユーザーに分かりやすくカテゴリ名と質問を表示
        prompt_with_default = f"[{category}] {prompt_text} (デフォルト: {default}): "
        
        # ユーザーが有効な数値を入力するまでループ
        while True:
            user_input_str = input(prompt_with_default)
            # Enterのみの場合はデフォルト値を使用
            if not user_input_str:
                value = default
                break
            
            # 入力された文字列が数値かチェック
            try:
                value = int(user_input_str)
                if value < 0:
                    print(">>> エラー: 0以上の数値を入力してください。")
                    continue
                break
            except ValueError:
                print(">>> エラー: 半角数字で数値を入力してください。")

        user_inputs[key] = value

    # 計算を実行
    result_message = calculate_lsp(user_inputs)

    # 結果をターミナルに表示
    print("\n" + "="*50)
    print(result_message)
    print("="*50)


# --- メイン処理の実行 ---
if __name__ == "__main__":
    run_simulator_cli()