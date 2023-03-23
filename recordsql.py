import streamlit as st
import time
import pandas as pd
from datetime import datetime
import mysql.connector


with st.sidebar:
    st.title("Records by Lambda")
    option = st.radio("Select desired action from options below",options=["Update DB", "Fetch from DB"])

header = ["ID", "Date", "Time", "Amount", "Type"]

date_array = f"{datetime.today()}".split()
date = date_array[0]
time_split = date_array[1].split(":")
time_split[-1] = f"{float(time_split[-1]):.0f}"
time_ = ":".join(time_split)


@st.cache_resource
def init_connection():
    return mysql.connector.connect(**st.secrets["mysql"])

conn = init_connection()


if option == "Update DB":
    with st.form("Input form"):
        amount = st.number_input("Enter the transaction amount here", format="%.2f", step=1.)
        trxn_type = st.selectbox("Enter transacion type below", options=["Debit", "Credit"])
        submit = st.form_submit_button("Update records")
 

    @st.cache_data(ttl=600)
    def run_query(query, record: tuple):
        with conn.cursor(buffered=True) as cur:
            cur.execute(query, record)
            conn.commit()
        

    # Create table if it doesn't exitst:
    def create_table():
        with conn.cursor(buffered=True) as create_con:
            create_con.execute("""
        CREATE TABLE IF NOT EXISTS record_table
        (
         ID INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
         a_date DATE,
         a_time TIME,
         amount FLOAT,
         trxn_type VARCHAR(7)
         );
        """)
            

    # writing into, query
    if submit:
        with st.spinner("Sending, updating database"):
            time.sleep(2)    
            st.success("Database succesfully updated")
        create_table()
        write  = run_query("""
        INSERT INTO record_table
        VALUES (ID,%s, %s, %s, %s);
        """, record=(date, time_, amount, trxn_type))

    with st.expander("Want to delete last few entry(ies)"):
        del_lim = st.number_input("Enter number of last entry(ies) to delete", min_value=1, step=1)

        with st.spinner("Deleting..."):
            time.sleep(2)
            if st.button(f"Delete last {del_lim} entry(ies)"):
                with conn.cursor(buffered=True) as del_conn:
                    del_conn.execute("""
                    DELETE FROM record_table
                    ORDER BY ID DESC
                    LIMIT %s;
                    """, (del_lim, ))
                    conn.commit()
                    st.error("Row(s) deleted")

 

else:
    limits = st.selectbox("Select 'All' to download all, or 'Choose' to enter a custom number", options=["All", "Choose"])
    if limits == "Choose":
        limit = st.number_input("How many rows (entries) do you want to download?", format="%i", min_value=1, step=1)
        limit_tup = (limit,)


    def fetch_from_table():
        with conn.cursor(buffered=True) as fetch_con:
            if limits == "All":
                fetch_con.execute("""SELECT * FROM record_table""")
            else:
                fetch_con.execute("""
                     SELECT * FROM record_table LIMIT %s;
                                    """, limit_tup)
        return fetch_con.fetchall()
    

    if st.button("FETCH"):
        with st.spinner("Fetching Data from DB"):
            time.sleep(2)
        rows = fetch_from_table()

    
        def convert_time(arg):
            td = arg
            total_seconds = td.total_seconds()

            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            time_str = "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))
            return time_str
        

        array = []
        for row in rows:
            row = list(row)
            row[2] = convert_time(row[2])
            array.append(row)

            
        df = pd.DataFrame(array, columns=header)


        def convert_df(df_name):
            return df_name.to_csv().encode("utf-8")
        
    
        download_bt = st.download_button(
                label="Download the fetched Record(s)",
                data=convert_df(df),
                file_name="record.csv",
                key="download-csv")
        

        st.markdown("### Displaying only up to the last five entries of the database")
        
        st.table(df.tail())

st.experimental_singleton.clear()