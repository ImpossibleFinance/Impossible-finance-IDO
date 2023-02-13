
##### KPIs

def main_kpis(full_data):
    total_unique_users = full_data['from'].nunique()
    total_usd_purchased = full_data['USD_amount'].sum()
    total_unique_purchase_txs = len(full_data)
    unique_IDOS = full_data['launchpad'].nunique()
    unique_sale_type = full_data['sale_type'].nunique()

    #last_ido_data = full_data[full_data['launchpad'] == (full_data['launchpad'].unique())[len(full_data['launchpad'].unique()) - 1]]
    #last_ido_unique_users = last_ido_data['from'].nunique()
    #last_ido_usd_purchased = last_ido_data['USD_amount'].sum()
    #last_ido_name = last_ido_data['launchpad'].unique()

    return total_unique_users, total_usd_purchased, unique_IDOS, total_unique_purchase_txs, unique_sale_type#, last_ido_unique_users, last_ido_usd_purchased, last_ido_name