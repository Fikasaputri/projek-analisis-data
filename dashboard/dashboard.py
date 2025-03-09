import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

# load data
all_df = pd.read_csv("dashboard/all_data_prs.csv")


# konversi tipe data
all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"])
all_df["order_delivered_customer_date"] = pd.to_datetime(all_df["order_delivered_customer_date"])


min_date = all_df["order_purchase_timestamp"].min().date()
max_date = all_df["order_purchase_timestamp"].max().date()

start_date, end_date = st.date_input(
    label="Rentang Waktu",
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

# filtering data berdasarkan rentang waktu

main_df = all_df[(all_df["order_purchase_timestamp"] >= pd.to_datetime(start_date))&
                 (all_df["order_purchase_timestamp"] <= pd.to_datetime(end_date))
                 ].copy()

with st.sidebar:
    st.image("dashboard/Screenshot 2025-03-08 234803.png", width=200)
  

# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe

def create_yearly_orders_df(df):
    return df.resample('Y', on='order_purchase_timestamp').size().reset_index(name="total_orders")

def create_category_orders_df(df):
    return df.groupby("product_category_name")["order_id"].count().reset_index(name="total_orders").sort_values(by="total_orders", ascending=False)

def create_shipping_time_df(df):
    return round((df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.days.mean(), 2)

def create_payment_distribution_df(df):
    return df["payment_type"].value_counts().to_frame(name="count").reset_index().rename(columns={"index": "payment_type"})

def create_review_shipping_relation_df(df):
    df_filtered = df.dropna(subset=["review_score", "order_delivered_customer_date", "order_purchase_timestamp"]).copy()
    df_filtered["shipping_score"] = (df_filtered["order_delivered_customer_date"] - df_filtered["order_purchase_timestamp"]).dt.days
    return df_filtered.groupby("review_score")["shipping_score"].mean().reset_index()
                                       
    

# buat dataframe untuk visualisasi 
yearly_orders_df = create_yearly_orders_df(main_df)
category_orders_df = create_category_orders_df(main_df)
avg_shipping_time = create_shipping_time_df(main_df)
payment_distribution_df = create_payment_distribution_df(main_df)
review_shipping_df = create_review_shipping_relation_df(main_df)  

# header dashboard
st.header('Brazilian E-Commerce BR')
st.subheader('Analisis Data E-Commerce')

# tren jumlah pesanan dari tahun ke tahun
st.subheader("Tren Jumlah Pesanan dari Tahun ke Tahun")

fig, ax = plt.subplots(figsize=(10, 5))
sns.lineplot(data=yearly_orders_df, x="order_purchase_timestamp", y="total_orders", marker="o", ax=ax)
ax.set_xlabel("Tahun")
ax.set_ylabel("Jumlah Pesanan")
st.pyplot(fig)

# kategori produk yang paling sering dipesan
st.subheader("Kategori Produk Paling Sering di Pesan")

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=category_orders_df.head(10), y="product_category_name", x="total_orders", palette="Blues", ax=ax)
ax.set_xlabel("Jumlah Pesanan")
ax.set_ylabel("Kategori Produk")
st.pyplot(fig)
             
# rata-rata waktu pengiriman
st.subheader("Rata-rata Waktu Pengiriman")

st.metric("Rata-Rata Waktu Pengiriman", value=f"{avg_shipping_time} hari")

# Distribusi metode pembayaran
st.subheader("Distribusi Metode Pembayaran")

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=payment_distribution_df, x="payment_type", y="count", palette="Purples_r", ax=ax)
ax.set_xlabel("Metode Pembayaran")
ax.set_ylabel("Jumlah Transaksi")
st.pyplot(fig)

# hubungan antara review
st.subheader("Hubungan Review Score dan Waktu Pengiriman")

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=review_shipping_df, x="review_score", y="shipping_score", palette="coolwarm", ax=ax)
ax.set_xlabel("Review_Score")
ax.set_ylabel("Waktu Pengiriman (Hari)")
st.pyplot(fig)

st.caption("© 2025 ~ fksp")
