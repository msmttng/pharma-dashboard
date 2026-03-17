import json
import os
import re
from datetime import datetime, timezone, timedelta

INPUT_FILE = "pharma_data.json"

def generate_html(data):
    JST = timezone(timedelta(hours=9), 'JST')
    updated_at = data.get("updated_at", datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S"))
    
    collabo_items = data.get("collabo", [])
    medipal_items = data.get("medipal", [])
    alfweb_items = data.get("alfweb", [])

    def normalize_units(name):
        if not name: return ""
        def replacer_multi(match):
            num = match.group(1)
            space = match.group(2)
            unit = match.group(3).upper()
            if unit == 'MG': unit = 'mg'
            elif unit == 'ML': unit = 'mL'
            elif unit == 'KG': unit = 'kg'
            elif unit == 'UG': unit = 'μg'
            elif unit == 'MCG': unit = 'μg'
            elif unit == 'G': unit = 'g'
            return f"{num}{space}{unit}"
        
        return re.sub(r'(\d+(?:\.\d+)?)(\s*)(MG|ML|KG|UG|MCG|G)(?=[^A-Za-z]|[Xx]|$)', replacer_multi, name, flags=re.IGNORECASE)

    for items in [collabo_items, medipal_items, alfweb_items]:
        for item in items:
            if 'name' in item:
                item['name'] = normalize_units(item['name'])

    def get_badge_info(status):
        if '納品済' in status:
            return 'badge-delivered', '納品済'
        elif '出荷準備中' in status:
            return 'badge-preparing', '出荷準備中'
        elif '調達中' in status:
            return 'badge-procuring', '調達中'
        elif '入荷未定' in status or '欠品' in status:
            return 'badge-unavailable', status
        return 'badge-default', status

    def get_collabo_rows(items):
        rows = ""
        for item in items:
            status = item.get('status', '')
            badge_cls, status_str = get_badge_info(status)
            
            # EPI機能：見た目を変えずに行をクリック可能にする
            is_pending = "調達中" in status or "入荷未定" in status or "欠品" in status or "未納" in status or "未定" in status or "受注辞退" in status
            tr_attr = f''' onclick="openOrderEpi('{item.get("name", "")}')" style="cursor: pointer;" title="クリックしてEPI発注"''' if is_pending else ""
            
            remarks_text = item.get("remarks", "")
            if remarks_text:
                remarks_text = remarks_text.replace("限定出荷品 (出荷調整品)　", "限定出荷品 (出荷調整品)<br>")
                remarks_text = remarks_text.replace("限定出荷品 (出荷調整品) ", "限定出荷品 (出荷調整品)<br>")
            
            remarks_html = f'<div class="remarks-tag">⚠ {remarks_text}</div>' if remarks_text else ''
            date_html = f'<div class="receipt-date">受付 {item.get("date")}</div>' if item.get('date') else ''
            
            rows += f"""
                        <tr{tr_attr}>
                            <td><div class="maker-name">{item.get('maker', '')}</div><div class="product-name">{item.get('name', '')}</div><div class="product-code">JAN: {item.get('code', '')}</div>{remarks_html}</td>
                            <td class="status-cell"><div class="status-badge {badge_cls}"><span class="badge-dot"></span>{status_str}</div>{date_html}</td>
                            <td class="qty-cell"><div class="qty-num">{item.get('order_qty', '')}</div><div class="qty-label">発注</div><div class="qty-sub">納品予定 {item.get('deliv_qty', '')}</div></td>
                        </tr>"""
        return rows

    def get_medipal_rows(items):
        rows = ""
        for item in items:
            is_danger = "調整" in item.get('remarks', '') or "未定" in item.get('remarks', '')
            status_text = "入荷未定" if is_danger else "通常"
            badge_cls = "badge-unavailable" if is_danger else "badge-default"
            
            # EPI機能：見た目を変えずに行をクリック可能にする
            is_pending = "入荷未定" in status_text or "調整" in item.get('remarks', '')
            tr_attr = f''' onclick="openOrderEpi('{item.get("name", "")}')" style="cursor: pointer;" title="クリックしてEPI発注"''' if is_pending else ""
            
            rem = item.get('remarks', '')
            if rem:
                rem = rem.replace("限定出荷品 (出荷調整品)　", "限定出荷品 (出荷調整品)<br>")
                rem = rem.replace("限定出荷品 (出荷調整品) ", "限定出荷品 (出荷調整品)<br>")
            
            remarks_html = f'<div class="receipt-date">{rem}</div>' if rem else ''
            
            qty = item.get('order_qty', '')
            qty_num = f'<div class="qty-num">{qty}</div>' if qty else '<div class="qty-num">-</div>'
            qty_cell = f'<td class="qty-cell">{qty_num}</td>'

            rows += f"""
                        <tr{tr_attr}>
                            <td><div class="maker-name">{item.get('maker', '')}</div><div class="product-name">{item.get('name', '')}</div><div class="product-code">JAN: {item.get('code', '')}</div></td>
                            <td class="status-cell"><div class="status-badge {badge_cls}"><span class="badge-dot"></span>{status_text}</div>{remarks_html}</td>
                            {qty_cell}
                        </tr>"""
        return rows

    def get_alfweb_rows(items):
        rows = ""
        for item in items:
            # EPI機能：見た目を変えずに行をクリック可能にする
            tr_attr = f''' onclick="openOrderEpi('{item.get("name", "")}')" style="cursor: pointer;" title="クリックしてEPI発注"'''
            rows += f"""
                        <tr{tr_attr}>
                            <td><div class="maker-name">{item.get('maker', '')}</div><div class="product-name">{item.get('name', '')}</div></td>
                            <td class="status-cell"><div class="status-badge badge-unavailable"><span class="badge-dot"></span>入荷未定</div><div class="receipt-date">更新 {item.get('date', '')}</div></td>
                            <td class="qty-cell"><div class="qty-num">{item.get('order_qty', '')}</div></td>
                        </tr>"""
        return rows

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>医薬品調達情報 統合ダッシュボード</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;600;700&family=Syne:wght@600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg:           #f0f2f7;
            --bg-card:      #ffffff;
            --border:       #e4e7ef;
            --border-mid:   #d1d5e8;

            --text-primary:   #0f1120;
            --text-secondary: #404668;
            --text-muted:     #717899;
            --text-code:      #5c6490;

            /* System accents */
            --collabo:      #1a6fd4;
            --collabo-soft: #e3eefa;
            --collabo-mid:  #93c0f4;
            --medipal:      #0e9e72;
            --medipal-soft: #e0f5ee;
            --medipal-mid:  #7dd4b8;
            --alfweb:       #2563be;
            --alfweb-soft:  #ddeeff;
            --alfweb-mid:   #80b4e8;
            --alfweb-accent: #0e9e72;

            /* Status */
            --s-delivered:    #0e9e72;
            --s-delivered-bg: #e0f5ee;
            --s-preparing:    #1a6fd4;
            --s-preparing-bg: #e3eefa;
            --s-procuring:    #c07000;
            --s-procuring-bg: #fff3d6;
            --s-unavailable:    #c0392b;
            --s-unavailable-bg: #fdecea;
            --s-normal:     #7880a8;
            --s-normal-bg:  #f0f2f7;

            --radius:    14px;
            --radius-sm: 8px;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: 'Noto Sans JP', sans-serif;
            font-weight: 500;
            background: var(--bg);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.6;
        }}

        /* ─── Subtle dot grid background ─── */
        body::before {{
            content: '';
            position: fixed;
            inset: 0;
            background-image: radial-gradient(circle, #c8cce0 1px, transparent 1px);
            background-size: 28px 28px;
            opacity: 0.45;
            pointer-events: none;
            z-index: 0;
        }}

        /* ─── Header ─── */
        .header {{
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(240,242,247,0.88);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
            border-bottom: 1px solid var(--border);
        }}

        .header-inner {{
            max-width: 1500px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            height: 60px;
            padding: 0 1.5rem;
        }}

        .header-left {{
            display: flex;
            align-items: center;
            gap: 0.85rem;
        }}

        .header-logo {{
            width: 34px;
            height: 34px;
            background: linear-gradient(135deg, var(--collabo), #0e9e72);
            border-radius: 9px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 17px;
            flex-shrink: 0;
            box-shadow: 0 2px 8px rgba(26,111,212,0.25);
        }}

        .header-title {{
            font-family: 'Syne', sans-serif;
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.01em;
        }}

        .header-subtitle {{
            font-size: 0.7rem;
            color: var(--text-muted);
            letter-spacing: 0.03em;
        }}

        .updated-badge {{
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.73rem;
            color: var(--text-secondary);
            background: white;
            border: 1px solid var(--border);
            padding: 0.28rem 0.75rem;
            border-radius: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }}

        .updated-dot {{
            width: 6px;
            height: 6px;
            background: var(--alfweb);
            border-radius: 50%;
            box-shadow: 0 0 0 2px var(--alfweb-soft);
            animation: pulse 2.2s infinite;
        }}

        @keyframes pulse {{
            0%, 100% {{ box-shadow: 0 0 0 2px var(--alfweb-soft); }}
            50%       {{ box-shadow: 0 0 0 4px var(--alfweb-soft); }}
        }}

        /* ─── Filter bar ─── */
        .filter-bar {{
            background: rgba(240,242,247,0.88);
            backdrop-filter: blur(18px);
            border-bottom: 1px solid var(--border);
            padding: 0.55rem 1.5rem;
        }}

        .filter-bar-inner {{
            max-width: 1500px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            gap: 0.45rem;
        }}

        .filter-label {{
            font-size: 0.7rem;
            color: var(--text-muted);
            letter-spacing: 0.08em;
            text-transform: uppercase;
            font-weight: 500;
            margin-right: 0.2rem;
        }}

        .tab-btn {{
            display: flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.3rem 0.85rem;
            border-radius: 20px;
            border: 1px solid var(--border);
            cursor: pointer;
            font-family: inherit;
            font-size: 0.77rem;
            font-weight: 500;
            transition: all 0.15s ease;
            background: white;
            color: var(--text-secondary);
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}

        .tab-btn:hover:not(.active) {{
            border-color: var(--border-mid);
            color: var(--text-primary);
            background: white;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        }}

        .tab-btn.active {{
            background: var(--collabo);
            border-color: var(--collabo);
            color: white;
            box-shadow: 0 2px 8px rgba(26,111,212,0.3);
        }}

        /* ─── Summary strip ─── */
        .summary-bar {{
            max-width: 1500px;
            margin: 1.25rem auto 0;
            padding: 0 1.5rem;
            display: flex;
            gap: 0.65rem;
            flex-wrap: wrap;
        }}

        .summary-chip {{
            display: flex;
            align-items: center;
            gap: 0.65rem;
            padding: 0.5rem 1rem;
            border-radius: var(--radius-sm);
            background: white;
            border: 1px solid var(--border);
            box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        }}

        .chip-swatch {{
            width: 8px;
            height: 28px;
            border-radius: 4px;
            flex-shrink: 0;
        }}

        .chip-collabo .chip-swatch {{ background: var(--collabo); }}
        .chip-medipal .chip-swatch {{ background: var(--medipal); }}
        .chip-alfweb  .chip-swatch {{ background: linear-gradient(to bottom, var(--alfweb), var(--alfweb-accent)); }}
        .chip-danger  .chip-swatch {{ background: var(--s-unavailable); }}

        .chip-num {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.25rem;
            font-weight: 600;
            line-height: 1;
        }}

        .chip-collabo .chip-num {{ color: var(--collabo); }}
        .chip-medipal .chip-num {{ color: var(--medipal); }}
        .chip-alfweb  .chip-num {{ color: var(--alfweb); }}
        .chip-danger  .chip-num {{ color: var(--s-unavailable); }}

        .chip-label {{
            font-size: 0.72rem;
            font-weight: 600;
            color: var(--text-secondary);
            line-height: 1.3;
        }}

        .chip-name {{
            font-size: 0.78rem;
            font-weight: 600;
            color: var(--text-primary);
            line-height: 1.3;
        }}

        /* ─── Main grid ─── */
        .main-content {{
            max-width: 1500px;
            margin: 1.1rem auto 2.5rem;
            padding: 0 1.5rem;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 1.1rem;
            position: relative;
            z-index: 1;
        }}

        /* ─── Card ─── */
        .card {{
            background: var(--bg-card);
            border-radius: var(--radius);
            border: 1px solid var(--border);
            box-shadow: 0 2px 10px rgba(0,0,0,0.055), 0 1px 2px rgba(0,0,0,0.04);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: box-shadow 0.2s, transform 0.2s;
        }}

        .card:hover {{
            box-shadow: 0 6px 24px rgba(0,0,0,0.09), 0 1px 4px rgba(0,0,0,0.05);
            transform: translateY(-1px);
        }}

        .card-header {{
            padding: 0.9rem 1.2rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            border-bottom: 1px solid var(--border);
        }}

        .card-collabo {{ background: linear-gradient(to right, var(--collabo-soft), white); }}
        .card-medipal {{ background: linear-gradient(to right, var(--medipal-soft), white); }}
        .card-alfweb  {{ background: linear-gradient(to right, #ddeeff, #edfaf5, white); }}

        .card-accent-bar {{
            width: 4px;
            height: 30px;
            border-radius: 3px;
            flex-shrink: 0;
        }}

        .card-collabo .card-accent-bar {{ background: var(--collabo); }}
        .card-medipal .card-accent-bar {{ background: var(--medipal); }}
        .card-alfweb  .card-accent-bar {{ background: linear-gradient(to bottom, var(--alfweb), var(--alfweb-accent)); }}

        .card-header-info {{ flex: 1; }}

        .card-sys {{
            font-size: 0.66rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin-bottom: 1px;
        }}

        .card-collabo .card-sys {{ color: var(--collabo); }}
        .card-medipal .card-sys {{ color: var(--medipal); }}
        .card-alfweb  .card-sys {{ color: var(--alfweb); }}

        .card-title {{
            font-family: 'Syne', sans-serif;
            font-size: 0.9rem;
            font-weight: 700;
            color: var(--text-primary);
        }}

        .item-count-block {{ text-align: right; }}

        .item-count {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.4rem;
            font-weight: 500;
            line-height: 1;
        }}

        .card-collabo .item-count {{ color: var(--collabo); }}
        .card-medipal .item-count {{ color: var(--medipal); }}
        .card-alfweb  .item-count {{ color: var(--alfweb); }}

        .item-count-label {{
            font-size: 0.6rem;
            color: var(--text-muted);
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }}

        /* ─── Table ─── */
        .table-container {{
            overflow-x: auto;
            max-height: 1000px; /* 1.5x larger for big monitors */
            overflow-y: auto;
            scrollbar-width: thin;
            scrollbar-color: var(--border-mid) transparent;
        }}

        .table-container::-webkit-scrollbar {{ width: 4px; }}
        .table-container::-webkit-scrollbar-track {{ background: transparent; }}
        .table-container::-webkit-scrollbar-thumb {{ background: var(--border-mid); border-radius: 4px; }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.82rem;
        }}

        thead {{ position: sticky; top: 0; z-index: 5; }}

        th {{
            background: #f8f9fc;
            padding: 0.55rem 1rem;
            font-size: 0.65rem;
            font-weight: 700;
            color: var(--text-primary);
            border-bottom: 1px solid var(--border);
            text-align: left;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            white-space: nowrap;
        }}

        td {{
            padding: 0.78rem 1rem;
            border-bottom: 1px solid #f0f2f7;
            vertical-align: middle;
        }}

        tr:last-child td {{ border-bottom: none; }}

        tr {{ transition: background 0.1s; }}
        tr:hover td {{ background: #f7f8fc; }}

        /* ─── Product cell ─── */
        .maker-name {{
            font-size: 0.66rem;
            font-weight: 700;
            color: var(--text-secondary);
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-bottom: 0.2rem;
        }}

        .product-name {{
            font-size: 0.82rem;
            font-weight: 600;
            color: var(--text-primary);
            line-height: 1.45;
        }}

        .product-code {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.64rem;
            font-weight: 600;
            color: var(--text-secondary);
            margin-top: 0.18rem;
        }}

        .remarks-tag {{
            display: inline-flex;
            align-items: flex-start;
            gap: 0.25rem;
            margin-top: 0.35rem;
            font-size: 0.65rem;
            font-weight: 600;
            color: #92600a;
            background: #fff7e0;
            border: 1px solid #f0d080;
            padding: 0.18rem 0.5rem;
            border-radius: 4px;
            line-height: 1.4;
        }}

        /* ─── Status badges ─── */
        .status-cell {{ white-space: nowrap; min-width: 108px; }}

        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            padding: 0.22rem 0.65rem;
            border-radius: 20px;
            font-size: 0.71rem;
            font-weight: 600;
            letter-spacing: 0.02em;
        }}

        .badge-dot {{
            width: 5px;
            height: 5px;
            border-radius: 50%;
            flex-shrink: 0;
        }}

        .badge-delivered {{
            background: var(--s-delivered-bg);
            color: var(--s-delivered);
            border: 1px solid #a8e8d4;
        }}
        .badge-delivered .badge-dot {{ background: var(--s-delivered); }}

        .badge-preparing {{
            background: var(--s-preparing-bg);
            color: var(--s-preparing);
            border: 1px solid #a0ccf0;
        }}
        .badge-preparing .badge-dot {{ background: var(--s-preparing); animation: bdot 1.6s infinite; }}

        .badge-procuring {{
            background: var(--s-procuring-bg);
            color: var(--s-procuring);
            border: 1px solid #f0cc70;
        }}
        .badge-procuring .badge-dot {{ background: var(--s-procuring); animation: bdot 1.2s infinite; }}

        .badge-unavailable {{
            background: var(--s-unavailable-bg);
            color: var(--s-unavailable);
            border: 1px solid #f0b0a8;
        }}
        .badge-unavailable .badge-dot {{ background: var(--s-unavailable); }}

        .badge-default {{
            background: var(--s-normal-bg);
            color: var(--s-normal);
            border: 1px solid var(--border);
        }}
        .badge-default .badge-dot {{ background: var(--s-normal); }}

        @keyframes bdot {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50%       {{ opacity: 0.4; transform: scale(0.7); }}
        }}

        .receipt-date {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.65rem;
            font-weight: 600;
            color: var(--text-secondary);
            margin-top: 0.28rem;
        }}

        /* ─── Qty cell ─── */
        .qty-cell {{ text-align: center; min-width: 58px; }}

        .qty-num {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-primary);
            line-height: 1;
        }}

        .qty-label {{ font-size: 0.61rem; font-weight: 600; color: var(--text-secondary); margin-top: 2px; }}
        .qty-sub   {{ font-size: 0.67rem; font-weight: 600; color: var(--text-secondary); margin-top: 2px; }}

        /* ─── Scroll top ─── */
        .scroll-top {{
            position: fixed;
            bottom: 1.5rem;
            right: 1.5rem;
            width: 38px;
            height: 38px;
            background: white;
            border: 1px solid var(--border-mid);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            color: var(--text-secondary);
            font-size: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: all 0.2s;
            opacity: 0;
            pointer-events: none;
            z-index: 200;
        }}

        .scroll-top.visible {{ opacity: 1; pointer-events: auto; }}

        .scroll-top:hover {{
            background: var(--collabo);
            border-color: var(--collabo);
            color: white;
            box-shadow: 0 4px 14px rgba(26,111,212,0.3);
        }}

        @media (max-width: 640px) {{
            .main-content {{ grid-template-columns: 1fr; }}
            .summary-bar  {{ gap: 0.5rem; }}
        }}
    </style>
</head>
<body>

    <!-- Header -->
    <header class="header">
        <div class="header-inner">
            <div class="header-left">
                <div class="header-logo">💊</div>
                <div>
                    <div class="header-title">医薬品調達情報 統合ダッシュボード</div>
                    <div class="header-subtitle">Pharmaceutical Procurement Dashboard</div>
                </div>
            </div>
            <div class="updated-badge">
                <span class="updated-dot"></span>
                <span>{updated_at}</span>
            </div>
        </div>
    </header>

    <!-- Filter bar -->
    <div class="filter-bar">
        <div class="filter-bar-inner">
            <span class="filter-label">表示</span>
            <button id="btn-all" class="tab-btn active" onclick="filterItems('all')">☰ すべて表示</button>
            <button id="btn-pending" class="tab-btn" onclick="filterItems('pending')">⚠ 未納・未定のみ</button>
        </div>
    </div>

    <!-- Summary -->
    <div class="summary-bar">
        <div class="summary-chip chip-collabo">
            <div class="chip-swatch"></div>
            <div>
                <div class="chip-num">{len(collabo_items)}</div>
                <div class="chip-label">件</div>
            </div>
            <div class="chip-name">Collabo Portal</div>
        </div>
        <div class="summary-chip chip-medipal">
            <div class="chip-swatch"></div>
            <div>
                <div class="chip-num">{len(medipal_items)}</div>
                <div class="chip-label">件</div>
            </div>
            <div class="chip-name">MEDIPAL</div>
        </div>
        <div class="summary-chip chip-alfweb">
            <div class="chip-swatch"></div>
            <div>
                <div class="chip-num">{len(alfweb_items)}</div>
                <div class="chip-label">件</div>
            </div>
            <div class="chip-name">ALF-Web</div>
        </div>
        <div class="summary-chip chip-danger" style="margin-left:auto;">
            <div class="chip-swatch"></div>
            <div>
                <div class="chip-num" id="unavail-count">—</div>
                <div class="chip-label">件</div>
            </div>
            <div class="chip-name">入荷未定</div>
        </div>
    </div>

    <!-- Main -->
    <div class="main-content">

        <!-- ── Collabo Portal ── -->
        <div class="card">
            <div class="card-header card-collabo">
                <div class="card-accent-bar"></div>
                <div class="card-header-info">
                    <div class="card-sys">System A</div>
                    <div class="card-title">Collabo Portal</div>
                </div>
                <div class="item-count-block">
                    <div class="item-count">{len(collabo_items)}</div>
                    <div class="item-count-label">items</div>
                </div>
            </div>
            <div class="table-container">
                <table>
                    <thead><tr><th>品名 / メーカー</th><th>ステータス</th><th style="text-align:center;">数量</th></tr></thead>
                    <tbody>
                    {get_collabo_rows(collabo_items)}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- ── MEDIPAL ── -->
        <div class="card">
            <div class="card-header card-medipal">
                <div class="card-accent-bar"></div>
                <div class="card-header-info">
                    <div class="card-sys">System B</div>
                    <div class="card-title">MEDIPAL</div>
                </div>
                <div class="item-count-block">
                    <div class="item-count">{len(medipal_items)}</div>
                    <div class="item-count-label">items</div>
                </div>
            </div>
            <div class="table-container">
                <table>
                    <thead><tr><th>品名 / メーカー</th><th>状況</th><th style="text-align:center;">数量</th></tr></thead>
                    <tbody>
                    {get_medipal_rows(medipal_items)}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- ── ALF-Web ── -->
        <div class="card">
            <div class="card-header card-alfweb">
                <div class="card-accent-bar"></div>
                <div class="card-header-info">
                    <div class="card-sys">System C</div>
                    <div class="card-title">ALF-Web</div>
                </div>
                <div class="item-count-block">
                    <div class="item-count">{len(alfweb_items)}</div>
                    <div class="item-count-label">items</div>
                </div>
            </div>
            <div class="table-container">
                <table>
                    <thead><tr><th>品名 / メーカー</th><th>状況</th><th style="text-align:center;">数量</th></tr></thead>
                    <tbody>
                    {get_alfweb_rows(alfweb_items)}
                    </tbody>
                </table>
            </div>
        </div>

    </div>

    <button class="scroll-top" id="scrollTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">↑</button>

    <script>
        function filterItems(mode) {{
            document.querySelectorAll('tbody tr').forEach(row => {{
                if (mode === 'all') {{ row.style.display = ''; return; }}
                const b = row.querySelector('.status-badge');
                if (!b) {{ row.style.display = 'none'; return; }}
                const t = b.textContent.trim();
                const isPending = t.includes('調達中') || t.includes('入荷未定') || t.includes('受注辞退') || t.includes('欠品') || t.includes('未納') || t.includes('未定');
                row.style.display = (isPending && !t.includes('出荷準備中')) ? '' : 'none';
            }});
            document.getElementById('btn-all').classList.toggle('active', mode === 'all');
            document.getElementById('btn-pending').classList.toggle('active', mode === 'pending');
        }}

        function countUnavailable() {{
            document.getElementById('unavail-count').textContent =
                document.querySelectorAll('.badge-unavailable, .badge-procuring').length;
        }}

        window.addEventListener('scroll', () => {{
            document.getElementById('scrollTop').classList.toggle('visible', scrollY > 280);
        }});

        const openOrderEpi = async (itemName) => {{
            if (!itemName) return;
            
            // 1. (先)や(後)などの接頭辞を削除
            let searchKeyword = itemName.replace(/^\\([前後]\\)\\s*/, '');
            
            // 2. PTPやバラなどの包装形態以降を削除
            searchKeyword = searchKeyword.replace(/\\s+(?:PTP|ﾊﾞﾗ)\\s*.*$/i, '');
            
            // 3. 末尾の数量・単位の連続を削除
            searchKeyword = searchKeyword.replace(/(?:\\s+\\d+(?:\\.\\d+)?(?:mg|g|mL|ml|T|管|カプセル|カプ|錠|包|瓶|本|ﾎﾝ|枚|ﾏｲ|キット|シリンジ|V)?(?:\\s*[×xX*]\\s*\\d+)?)+$/i, '');
            
            // 4. 前後の余分な空白を削除
            searchKeyword = searchKeyword.trim();
            
            try {{
                if (navigator.clipboard && navigator.clipboard.writeText) {{
                    await navigator.clipboard.writeText(searchKeyword);
                }} else {{
                    const textArea = document.createElement("textarea");
                    textArea.value = searchKeyword;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand("copy");
                    document.body.removeChild(textArea);
                }}
                setTimeout(() => window.open('https://www.order-epi.com/order/', '_blank'), 100);
            }} catch (err) {{
                console.error('クリップボードのコピーに失敗しました', err);
            }}
        }};

        countUnavailable();
    </script>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    with open("dashboard.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    print("Generated: index.html")
    print("Generated: dashboard.html")

if __name__ == "__main__":
    if os.path.exists(INPUT_FILE):
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        generate_html(data)
    else:
        print(f"File not found: {{INPUT_FILE}}")