# --- JAL NEOBANK 計算用ヘルパー関数 ---

def _calculate_neobank_yen_miles(balance_in_man_jpy):
    """円普通預金の残高（万円）から、通常会員の月間獲得マイルを計算する"""
    balance = balance_in_man_jpy * 10000
    if balance >= 10_000_000:
        return 160
    if balance >= 5_000_000:
        return 80
    if balance >= 3_000_000:
        return 50
    if balance >= 1_000_000:
        return 20
    return 0

def _calculate_neobank_fx_miles(balance_in_man_jpy):
    """外貨普通預金の円換算残高（万円）から、通常会員の月間獲得マイルを計算する"""
    balance = balance_in_man_jpy * 10000
    if balance >= 100_000_000:
        return 20000
    if balance >= 90_000_000:
        return 10000 
    if balance >= 80_000_000:
        return 9000
    if balance >= 70_000_000:
        return 8000
    if balance >= 60_000_000:
        return 7000
    if balance >= 50_000_000:
        return 6000
    if balance >= 40_000_000:
        return 5000
    if balance >= 30_000_000:
        return 4000
    if balance >= 20_000_000:
        return 3000
    if balance >= 10_000_000:
        return 2000
    if balance >= 9_000_000:
        return 1000
    if balance >= 8_000_000:
        return 900
    if balance >= 7_000_000:
        return 800
    if balance >= 6_000_000:
        return 700
    if balance >= 5_000_000:
        return 600
    if balance >= 1_000_000:
        return 200
    if balance >= 500_000:
        return 100
    if balance >= 250_000:
        return 50
    if balance >= 100_000:
        return 20
    if balance >= 10_000:
        return 5
    return 0


# --- LSP計算メインロジック ---
def calculate_lsp(inputs):
    """
    年間のLSP獲得量を計算し、結果を文字列として返します。
    """
    TARGET_LSP = inputs['target_lsp']
    JPY_PER_JAL_CARD_MILE = 100

    total_lsp = 0
    breakdown = {}

    # 1. 搭乗ポイント
    flight_lsp = (inputs['annual_domestic_flights'] * 5) + ((inputs['annual_international_miles'] // 1000) * 5)
    if flight_lsp > 0:
        breakdown['搭乗'] = flight_lsp
    total_lsp += flight_lsp

    # 2. JALカード決済ポイント
    total_card_spending = inputs['annual_jal_card_spending_jpy']
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
    
    # 5. JAL NEOBANKポイント (★詳細計算ロジック)
    neobank_lsp = 0
    is_premium = inputs['is_neobank_premium'] == 1
    
    # 残高からマイル獲得資格を判定
    yen_miles = _calculate_neobank_yen_miles(inputs['yen_balance_man_jpy'])
    fx_miles = _calculate_neobank_fx_miles(inputs['fx_balance_man_jpy'])
    
    earns_from_yen = yen_miles > 0
    earns_from_fx = fx_miles > 0
    
    # 年間を通じて残高を維持した場合、LSP積算は2回 (半期ごと)
    lsp_periods = 2
    
    # 円普通預金によるLSP
    if earns_from_yen:
        # 通常1P/半期、プレミアムなら+2P
        points_per_period = 3 if is_premium else 1
        neobank_lsp += points_per_period * lsp_periods
        
    # 外貨普通預金によるLSP
    if earns_from_fx:
        # 通常2P/半期、プレミアムなら+4P
        points_per_period = 6 if is_premium else 2
        neobank_lsp += points_per_period * lsp_periods
    
    # 半期ボーナスによるLSP (プレミアム会員かつ、どちらかでマイル獲得がある場合)
    if is_premium and (earns_from_yen or earns_from_fx):
        # 1P/半期
        neobank_lsp += 1 * lsp_periods

    if neobank_lsp > 0:
        breakdown['JAL NEOBANK'] = neobank_lsp
    total_lsp += neobank_lsp

    # 6. ジャルパックポイント
    jalpak_lsp = (inputs['jalpak_domestic_tours'] * 3) + (inputs['jalpak_overseas_tours'] * 10)
    if jalpak_lsp > 0:
        breakdown['ジャルパック利用'] = jalpak_lsp
    total_lsp += jalpak_lsp

    # 7. サブスク系サービス
    subscription_lsp = (inputs['jal_wellness_months'] + inputs['jal_denki_months'] +
                        inputs['jal_hikari_months'] + inputs['jal_mobile_months'])
    if subscription_lsp > 0:
        breakdown['サブスクリプションサービス'] = subscription_lsp
    total_lsp += subscription_lsp

    # 8. JALふるさと納税
    furusato_lsp = inputs['annual_furusato_nozei_jpy'] // 10000
    if furusato_lsp > 0:
        breakdown['JALふるさと納税'] = furusato_lsp
    total_lsp += furusato_lsp

    # --- 結果を文字列として生成 ---
    result_lines = []
    result_lines.append("--- 年間LSP獲得シミュレーション結果 ---")
    result_lines.append(f"\nJALカード年間決済総額: {total_card_spending:,} 円")
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
    
    input_prompts = {
        'target_lsp': ('目標LSP', '目標設定', 1500),

        'annual_domestic_flights': ('国内線の年間搭乗回数（片道）', '1. 搭乗', 0),
        'annual_international_miles': ('国際線の年間搭乗区間マイル（合計）', '1. 搭乗', 0),

        'annual_jal_card_spending_jpy': ('JALカードの年間決済額（円） ※航空券代を含む', '2. 金融・決済', 0),
        'annual_jal_pay_miles': ('JAL Payで年間獲得するマイル数', '2. 金融・決済', 0),

        'annual_jal_mall_miles': ('JAL Mallで年間獲得するマイル数', '3. ショッピング', 0),

        # JAL NEOBANKの質問を詳細化
        'is_neobank_premium': ('JAL NEOBANKプレミアムに加入 (1=はい, 0=いいえ)', '4. JAL NEOBANK', 0),
        'yen_balance_man_jpy': ('円普通預金の平均残高（万円）', '4. JAL NEOBANK', 0),
        'fx_balance_man_jpy': ('外貨預金の平均残高（円換算・万円）', '4. JAL NEOBANK', 0),

        'jalpak_domestic_tours': ('ジャルパック国内ツアーの年間利用回数', '5. トラベル', 0),
        'jalpak_overseas_tours': ('ジャルパック海外ツアーの年間利用回数', '5. トラベル', 0),

        'jal_wellness_months': ('JAL Wellness & Travelの年間利用月数 (0-12)', '6. 生活・インフラ', 0),
        'jal_denki_months': ('JALでんきの年間利用月数 (0-12)', '6. 生活・インフラ', 0),
        'jal_hikari_months': ('JAL光の年間利用月数 (0-12)', '6. 生活・インフラ', 0),
        'jal_mobile_months': ('JALモバイルの年間利用月数 (0-12)', '6. 生活・インフラ', 0),
        'annual_furusato_nozei_jpy': ('JALふるさと納税の年間寄附額（円）', '6. 生活・インフラ', 0),
    }

    user_inputs = {}
    
    print("--- JAL Life Status ポイント(LSP) 年間獲得シミュレーター ---")
    print("各項目に数値を入力してください。")
    print("何も入力せずにEnterキーを押すと、デフォルト値が使用されます。\n")

    for key, (prompt_text, category, default) in input_prompts.items():
        prompt_with_default = f"[{category}] {prompt_text} (デフォルト: {default}): "
        
        while True:
            user_input_str = input(prompt_with_default)
            if not user_input_str:
                value = default
                break
            
            try:
                value = int(user_input_str)
                if key == 'is_neobank_premium' and value not in [0, 1]:
                    print(">>> エラー: 0 (いいえ) または 1 (はい) を入力してください。")
                    continue
                elif value < 0:
                    print(">>> エラー: 0以上の数値を入力してください。")
                    continue
                break
            except ValueError:
                print(">>> エラー: 半角数字で数値を入力してください。")

        user_inputs[key] = value

    result_message = calculate_lsp(user_inputs)

    print("\n" + "="*50)
    print(result_message)
    print("="*50)


# --- メイン処理の実行 ---
if __name__ == "__main__":
    run_simulator_cli()