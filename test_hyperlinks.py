#!/usr/bin/env python3
"""Test kliknutelných hyperlinků v Excelu"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from openpyxl.styles import Alignment, Font

def test_excel_hyperlinks():
    """Vytvoří testovací Excel s kliknutelnými odkazy"""

    output_dir = Path(__file__).parent / "data"
    output_dir.mkdir(exist_ok=True)

    # Testovací data s URL
    test_data = [
        {
            'Jméno': 'Test Makléř 1',
            'Telefon': '+420 123 456 789',
            'Email': 'makler1@test.cz',
            'Odkazy': 'https://www.sreality.cz/detail/prodej/byt/2+kk/praha/123456\nhttps://www.sreality.cz/detail/prodej/byt/3+1/praha/789012'
        },
        {
            'Jméno': 'Test Makléř 2',
            'Telefon': '+420 987 654 321',
            'Email': 'makler2@test.cz',
            'Odkazy': 'https://www.sreality.cz/detail/prodej/dum/brno/456789'
        },
        {
            'Jméno': 'Test Makléř 3',
            'Telefon': '+420 555 111 222',
            'Email': 'makler3@test.cz',
            'Odkazy': 'N/A'
        }
    ]

    df = pd.DataFrame(test_data)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = output_dir / f"test_hyperlinks_{timestamp}.xlsx"

    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Test')
        worksheet = writer.sheets['Test']

        # Najdi index sloupce "Odkazy"
        odkazy_col_idx = None
        for idx, col in enumerate(df.columns):
            if col == 'Odkazy':
                odkazy_col_idx = idx
                break

        # Nastav šířku sloupců
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(lambda x: len(str(x).split('\n')[0])).max(),
                len(col)
            ) + 2

            if col == 'Odkazy':
                max_length = min(max_length, 80)
            else:
                max_length = min(max_length, 30)

            worksheet.column_dimensions[chr(65 + idx)].width = max_length

        # Projdi všechny řádky a přidej hyperlinky
        for row_idx, row in enumerate(worksheet.iter_rows(min_row=2), start=2):
            for cell_idx, cell in enumerate(row):
                cell.alignment = Alignment(wrap_text=True, vertical='top')

                # Pokud je to sloupec "Odkazy" a obsahuje URL
                if odkazy_col_idx is not None and cell_idx == odkazy_col_idx:
                    cell_value = str(cell.value) if cell.value else ""
                    if cell_value and cell_value != 'N/A':
                        # Rozdělí více odkazů na samostatné řádky
                        urls = [url.strip() for url in cell_value.split('\n') if url.strip()]
                        if urls:
                            # Pro první odkaz nastav hyperlink
                            first_url = urls[0]
                            if first_url.startswith('http'):
                                cell.hyperlink = first_url
                                cell.value = first_url
                                cell.font = Font(color="0563C1", underline="single")

                            # Pokud je víc odkazů, zůstanou jako text na dalších řádcích
                            if len(urls) > 1:
                                all_urls_text = '\n'.join(urls)
                                cell.value = all_urls_text

    print(f"✅ Testovací Excel vytvořen: {filepath}")
    print("\n📋 Obsah:")
    print(f"   - 3 řádky testovacích dat")
    print(f"   - Sloupec 'Odkazy' obsahuje kliknutelné hyperlinky")
    print(f"   - První makléř má 2 odkazy (první je kliknutelný)")
    print(f"   - Druhý makléř má 1 kliknutelný odkaz")
    print(f"   - Třetí makléř má 'N/A' (bez odkazu)")
    print(f"\n💡 Otevři soubor v Excelu a zkontroluj, že odkazy jsou modré a kliknutelné!")

    return str(filepath)

if __name__ == "__main__":
    test_excel_hyperlinks()
