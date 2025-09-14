# Import Libraries
# for connection
from azure.identity import InteractiveBrowserCredential
from itertools import chain, repeat
import struct
import pyodbc

# for viz
import pandas as pd

# for app
import streamlit as st
import datetime
from datetime import date

# for getting after from clause
import re

# C:\Users\shakt\anaconda3\python.exe app.py




# define connection


# initializing variables
# connection_string = ""
# attrs = {}
# logged_in = False
#st.session_state.logged_in = logged_in  # Store login state in session state
#st.session_state.connection_string = connection_string  # Store connection string in session state  
#st.session_state.attrs = attrs  # Store attributes in session state

# sign in
def sign_in():
    #global connection_string, attrs, logged_in  # Declare as global
    # Authenticate using browser (same as SSMS MFA)
    credential = InteractiveBrowserCredential()
    token = credential.get_token("https://database.windows.net//.default")

    # Encode token for ODBC
    token_bytes = bytes(token.token, "UTF-8")
    encoded = bytes(chain.from_iterable(zip(token_bytes, repeat(0))))
    packed_token = struct.pack("<i", len(encoded)) + encoded
    attrs = {1256: packed_token}  # SQL_COPT_SS_ACCESS_TOKEN

    # Define connection string
    server = "vv2iwx4oxwaebpogsiees6rd6q-3y5wf3jqtzmelnjb6zdd2nks2i.datawarehouse.fabric.microsoft.com"  # Replace with your actual server name
    database = "Food Waste Management"

    connection_string = f"""
    Driver={{ODBC Driver 17 for SQL Server}};
    Server={server};
    Database={database};
    Encrypt=Yes;
    TrustServerCertificate=No;
    """
    logged_in = True
    st.session_state.logged_in = logged_in  # Store login state in session state
    st.session_state.connection_string = connection_string  # Store connection string in session state
    st.session_state.attrs = attrs  # Store attributes in session state

    # getting user name
    import jwt  # PyJWT
    #from azure.identity import InteractiveBrowserCredential

    # Authenticate and get token for Microsoft Graph
    #credential = InteractiveBrowserCredential()
    graph_token = credential.get_token("https://graph.microsoft.com/.default")

    # Decode JWT token to extract claims
    decoded = jwt.decode(graph_token.token, options={"verify_signature": False})
    upn = decoded.get("upn") or decoded.get("preferred_username")
    st.session_state.upn = upn  # Store user in session state


def show_data(query_func):
    query1, df = query_func()
    #print(f"Query: {query}")
    #print(df)
    st.write(query1.upper())
    st.dataframe(df)


def user():
    connection_string = st.session_state.connection_string
    attrs = st.session_state.attrs
    conn = pyodbc.connect(connection_string, attrs_before=attrs)
    cursor = conn.cursor()

    # Example query
    query = "SELECT SYSTEM_USER AS CurrentUser;"
    cursor.execute(query)
    rows = cursor.fetchall()
    # fetch user name
    st.session_state.user = rows[0][0]
    #print(f"Current User: {st.session_state.user}")
    columns = [column[0] for column in cursor.description]
    df = pd.DataFrame.from_records(rows, columns=columns)
    #print(df)
    cursor.close()
    conn.close()
    return query, df

def db_info():
    connection_string = st.session_state.connection_string
    attrs = st.session_state.attrs
    conn = pyodbc.connect(connection_string, attrs_before=attrs)
    cursor = conn.cursor()

    # Example query
    query = "SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME in (SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE')"
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df = pd.DataFrame.from_records(rows, columns=columns)
    #print(df)
    cursor.close()
    conn.close()
    return query, df


def accessible():
    connection_string = st.session_state.connection_string
    attrs = st.session_state.attrs
    conn = pyodbc.connect(connection_string, attrs_before=attrs)
    cursor = conn.cursor()

    # Example query
    query = "SELECT s.name AS schema_name, t.name AS table_name FROM sys.tables t JOIN sys.schemas s ON t.schema_id = s.schema_id WHERE HAS_PERMS_BY_NAME(QUOTENAME(s.name) + '.' + QUOTENAME(t.name), 'OBJECT', 'SELECT') = 1 ORDER BY schema_name, table_name;"
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df = pd.DataFrame.from_records(rows, columns=columns)
    #print(df)
    cursor.close()
    conn.close()
    return query, df

def query_db(query_string):
    connection_string = st.session_state.connection_string
    attrs = st.session_state.attrs
    conn = pyodbc.connect(connection_string, attrs_before=attrs)
    cursor = conn.cursor()

    # Example query
    #query = "SELECT SYSTEM_USER AS CurrentUser;"
    query_string = filter(query_string)  # Apply filter if needed
    #cursor.execute(query_string)
    try:
        cursor.execute(query_string)
    except Exception as e:
        st.error("Query failed to execute.")
        st.error(f"Query string was: {query_string}")
        st.error(f"Error: {str(e)}")

    rows = cursor.fetchall()
    # fetch user name
    #st.session_state.user = rows[0][0]
    #print(f"Current User: {st.session_state.user}")
    columns = [column[0] for column in cursor.description]
    df = pd.DataFrame.from_records(rows, columns=columns)
    #print(df)
    cursor.close()
    conn.close()
    return query_string , df






def query_to_list(query_string):
    connection_string = st.session_state.connection_string
    attrs = st.session_state.attrs
    conn = pyodbc.connect(connection_string, attrs_before=attrs)
    cursor = conn.cursor()

    cursor.execute(query_string)
    rows = cursor.fetchall()
    #columns = [column[0] for column in cursor.description]
    #df = pd.DataFrame(rows)
    # Convert to list
    result_list = [row[0] for row in rows] #df.values.flatten().tolist()  # Flatten the DataFrame to a single list
    
    cursor.close()
    conn.close()
    
    return result_list

def single_query(query_string):
    connection_string = st.session_state.connection_string
    attrs = st.session_state.attrs
    conn = pyodbc.connect(connection_string, attrs_before=attrs)
    cursor = conn.cursor()

    cursor.execute(query_string)
    row = cursor.fetchone()
    
    # if row:
    #     result_dict = dict(zip([column[0] for column in cursor.description], row))
    # else:
    #     result_dict = None
    
    cursor.close()
    conn.close()
    
    return row[0] if row else None  # Return the first column of the first row, or None if no rows found


def manage_food_listings():
    # Placeholder for food listings management functionality
    st.title("Manage Food Listings")
    st.write("This section will allow you to manage food listings, including adding, updating, and deleting listings.")
    # Implement management functionality here
    # ...existing code...

    tab1, tab2, tab3 = st.tabs(["Insert Records", "Update Records", "Delete Records"])

    with tab1:
        #st.write("Tab 1")
            form = st.form("ADD Food")
            #food_id = st.number_input("Food ID", min_value=1)
            food_id = single_query("SELECT ISNULL(MAX(Food_ID), 0) + 1 FROM Food_Listings")
            #st.write(f"Next Food ID: {food_id}")
            form.food_name = st.selectbox("Food Type", query_to_list("SELECT DISTINCT Food_Name FROM Food_Listings")) #st.text_input("Food Name")
            form.quantity = st.number_input("Quantity", min_value=1)
            form.expiry = st.date_input("Expiry Date", min_value=date.today().strftime("%Y-%m-%d"))
            #provider_id = st.number_input("Provider ID", min_value=1)
            form.provider_name = st.selectbox("Provider Name", query_to_list("SELECT Name FROM Providers"))
            provider_id = single_query("SELECT Provider_ID FROM Providers WHERE Name = '{}'".format(form.provider_name))
            form.provider_type = st.selectbox("Provider Type", query_to_list("SELECT DISTINCT Provider_Type FROM Food_Listings")) #st.text_input("Provider Type")
            form.location = st.selectbox("Location", query_to_list("SELECT DISTINCT Location FROM Food_Listings")) #st.text_input("City / Location")
            form.food_type = st.selectbox("Food Type", query_to_list("SELECT DISTINCT Food_Type FROM Food_Listings"))
            form.meal_type = st.selectbox("Meal Type", query_to_list("SELECT DISTINCT Meal_Type FROM Food_Listings"))
            submit = form.form_submit_button("Add Food")
            # submit = st.button("Add Food")
            if submit:
                conn = pyodbc.connect(st.session_state.connection_string, attrs_before=st.session_state.attrs)
                cursor = conn.cursor()
                try:
                    query_insert = "BEGIN TRY BEGIN TRANSACTION; INSERT INTO Food_Listings (Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?); COMMIT TRANSACTION; END TRY BEGIN CATCH ROLLBACK TRANSACTION; DECLARE @ErrorMessage NVARCHAR(4000); DECLARE @ErrorSeverity INT; DECLARE @ErrorState INT; SELECT @ErrorMessage = ERROR_MESSAGE(), @ErrorSeverity = ERROR_SEVERITY(), @ErrorState = ERROR_STATE(); RAISERROR (@ErrorMessage, @ErrorSeverity, @ErrorState); END CATCH;"
                    params = (food_id, form.food_name, form.quantity, form.expiry, provider_id, form.provider_type, form.location, form.food_type, form.meal_type)
                    # Execute the SQL query with parameters
                    cursor.execute(

                        # SQL query to insert a new food listing
                        query_insert,
                        params
                    )
                    conn.commit()  # Commit the transaction

                    #st.success(f"✅ Food item added successfully with ID {food_id} !")
                    
                    # Get number of rows affected
                    rows_affected = cursor.rowcount

                    query_with_placeholders = query_insert.replace("?", "{}")
                    formatted_query = query_with_placeholders.format(*params)
                    

                    st.success(f"✅ Food item added successfully with ID {food_id} — {rows_affected} row(s) affected.")
                    st.success("Query executed successfully: " + formatted_query)
                    food_id = single_query("SELECT ISNULL(MAX(Food_ID), 0) + 1 FROM Food_Listings")  # Update food_id for next entry


                except Exception as e:
                    # Rollback in case the SQL transaction fails
                    cursor.execute("ROLLBACK TRANSACTION;")
                    st.error(f"❌ Query failed and transaction rolled back: {e}")

                finally:
                    conn.close()
            



    with tab2:
        st.markdown("Update only: **Quantity**, **Expiry_Date**, **Meal_Type**, or **Food_Type**")
        food_id = st.number_input("Enter Food ID to Update", min_value=1)
        field = st.selectbox("Field to Update", ["Quantity", "Expiry_Date", "Meal_Type", "Food_Type"])
        if field == "Quantity":
            new_value = st.number_input("New Quantity", min_value=1)
            query_update = f"UPDATE Food_Listings SET Quantity = ? WHERE Food_ID = ?"
            params = (new_value, food_id)
        elif field == "Expiry_Date":
            new_value = st.date_input("New Expiry Date", min_value=date.today().strftime("%Y-%m-%d"))
            query_update = f"UPDATE Food_Listings SET Expiry_Date = ? WHERE Food_ID = ?"
            params = (new_value, food_id)
        elif field == "Meal_Type":
            new_value = st.selectbox("New Meal Type", query_to_list("SELECT DISTINCT Meal_Type FROM Food_Listings"))
            query_update = f"UPDATE Food_Listings SET Meal_Type = ? WHERE Food_ID = ?"
            params = (new_value, food_id)
        elif field == "Food_Type":
            new_value = st.selectbox("New Food Type", query_to_list("SELECT DISTINCT Food_Type FROM Food_Listings"))
            query_update = f"UPDATE Food_Listings SET Food_Type = ? WHERE Food_ID = ?"
            params = (new_value, food_id)

        if st.button("Update Food"):
            conn = pyodbc.connect(st.session_state.connection_string, attrs_before=st.session_state.attrs)
            cursor = conn.cursor()
            try:
                transaction_query1 = "BEGIN TRY BEGIN TRANSACTION; "
                transaction_query2 = " COMMIT TRANSACTION; END TRY BEGIN CATCH ROLLBACK TRANSACTION; DECLARE @ErrorMessage NVARCHAR(4000); DECLARE @ErrorSeverity INT; DECLARE @ErrorState INT; SELECT @ErrorMessage = ERROR_MESSAGE(), @ErrorSeverity = ERROR_SEVERITY(), @ErrorState = ERROR_STATE(); RAISERROR (@ErrorMessage, @ErrorSeverity, @ErrorState); END CATCH;"
                # Execute the SQL query with parameters
                query_update = transaction_query1 + query_update + transaction_query2
                cursor.execute(query_update, params)
                conn.commit()  # Commit the transaction

                # Get number of rows affected
                rows_affected = cursor.rowcount

                query_with_placeholders = query_update.replace("?", "{}")
                formatted_query = query_with_placeholders.format(*params)

                st.success(f"✅ Food item with ID {food_id} updated successfully — {rows_affected} row(s) affected.")
                st.success("Query executed successfully: " + formatted_query)

            except Exception as e:
                # Rollback in case the SQL transaction fails
                cursor.execute("ROLLBACK TRANSACTION;")
                st.error(f"❌ Query failed and transaction rolled back: {e}")

            finally:
                conn.close()

    with tab3:
        food_id = st.number_input("Enter Food ID to Delete", min_value=1)
        if st.button("Delete Food"):
            conn = pyodbc.connect(st.session_state.connection_string, attrs_before=st.session_state.attrs)
            cursor = conn.cursor()
            try:
                transaction_query1 = "BEGIN TRY BEGIN TRANSACTION; "
                transaction_query2 = " COMMIT TRANSACTION; END TRY BEGIN CATCH ROLLBACK TRANSACTION; DECLARE @ErrorMessage NVARCHAR(4000); DECLARE @ErrorSeverity INT; DECLARE @ErrorState INT; SELECT @ErrorMessage = ERROR_MESSAGE(), @ErrorSeverity = ERROR_SEVERITY(), @ErrorState = ERROR_STATE(); RAISERROR (@ErrorMessage, @ErrorSeverity, @ErrorState); END CATCH;"
                # SQL query to delete a food listing
                query_delete = transaction_query1 + "DELETE FROM Food_Listings WHERE Food_ID = ?;" + transaction_query2
                params = (food_id,)
                cursor.execute(query_delete, params)
                conn.commit()  # Commit the transaction

                # Get number of rows affected
                rows_affected = cursor.rowcount

                query_with_placeholders = query_delete.replace("?", "{}")
                formatted_query = query_with_placeholders.format(*params)

                st.success(f"✅ Food item with ID {food_id} deleted successfully — {rows_affected} row(s) affected.")
                st.success("Query executed successfully: " + formatted_query)

            except Exception as e:
                # Rollback in case the SQL transaction fails
                cursor.execute("ROLLBACK TRANSACTION;")
                st.error(f"❌ Query failed and transaction rolled back: {e}")

            finally:
                conn.close()

    # ...existing code...

def filter(query_string):
    # filter based on city, provider, food type, and meal type

    
    # matches = re.findall(r'FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)', query_string, re.IGNORECASE)

    # if matches:
    #     last_table = matches[-1]
        #print("Last table after FROM:", last_table)

    # if last_table == "Claims":
    #     where_string = "AND Claims.Food_ID = Food_Listings.Food_ID AND Food_Listings.Provider_ID = Providers.Provider_ID"
    # elif last_table == "Food_Listings":
    #     where_string = "AND Food_Listings.Provider_ID = Providers.Provider_ID"
    # elif last_table == "Providers":
    #     where_string = "AND Food_Listings.Provider_ID = Providers.Provider_ID"
    # elif last_table == "Receivers":
    #     where_string = "AND Claims.Receiver_ID = Receivers.Receiver_ID AND Food_Listings.Provider_ID = Providers.Provider_ID"

    query_string = query_string.format(
        #where_string  # Default condition to always be true
          ("AND Providers.City = '{}' ".format(st.session_state.city) if st.session_state.city != "All" else "")
        + ("AND Providers.Name = '{}' ".format(st.session_state.provider_choice) if st.session_state.provider_choice != "All" else "")
        + ("AND Food_Listings.Food_Type = '{}' ".format(st.session_state.food_type) if st.session_state.food_type != "All" else "")
        + ("AND Food_Listings.Meal_Type = '{}' ".format(st.session_state.meal_type) if st.session_state.meal_type != "All" else "")
    )
    return query_string
    

# after logging in
def post_login():
    # app


    st.sidebar.header("🔑 User Information")
    st.sidebar.text(f"User: {st.session_state.upn}")
    #st.sidebar.text("Role: [User Role]")

    st.sidebar.header("📂 Navigation")
    tab = st.sidebar.radio("Select a Section", [
        "Info and Login",
        "Summary",
        "Food Listings",
        "Claims Analysis",
        "Contacts",
        "Manage Food Listings"
    ])

    st.sidebar.header("🔍 Filters")
    st.session_state.city = st.sidebar.selectbox("City", ["All"] + query_to_list("SELECT DISTINCT City FROM Providers ORDER BY City"))
    st.session_state.provider_choice = st.sidebar.selectbox("Provider", ["All"] + query_to_list("SELECT DISTINCT Name FROM Providers ORDER BY Name"))
    st.session_state.food_type = st.sidebar.selectbox("Food Type", ["All"] + query_to_list("SELECT DISTINCT Food_Type FROM Food_Listings ORDER BY Food_Type"))
    st.session_state.meal_type = st.sidebar.selectbox("Meal Type", ["All"] + query_to_list("SELECT DISTINCT Meal_Type FROM Food_Listings ORDER BY Meal_Type"))




    # Layout: Left - Nav (sidebar), Right - Content
    right_col = st.columns(1)

    # Show content in right column
    if right_col:
        if tab == "Info and Login":
            st.set_page_config(page_title="Local Food Wastage System", layout="wide")
            st.title("🍽️ Local Food Wastage Management System")
            st.markdown("Connect food donors with those in need to reduce food waste.")
            
            st.subheader("User Information")
            show_data(user)
            st.subheader("Accessible Tables")
            show_data(accessible)
            st.subheader("Database Information")
            show_data(db_info)
        elif tab == "Summary":
            
            st.title("📊 Summary Dashboard")
            st.subheader("Providers and Receivers by City")
            show_data(lambda: query_db(st.session_state.queries["get_providers_receivers_by_city"]))
            st.subheader("🏆 Top Provider Types by Contributions")
            show_data(lambda: query_db(st.session_state.queries["get_top_provider_type"]))
            st.subheader("📦 Total Quantity of Food Available")
            show_data(lambda: query_db(st.session_state.queries["get_total_food_quantity"]))
            st.subheader("🏙️ Cities with Most Food Listings")
            show_data(lambda: query_db(st.session_state.queries["get_top_city_by_listings"]))
            st.subheader("🍽️ Common Food Types")
            show_data(lambda: query_db(st.session_state.queries["get_common_food_types"]))
        elif tab == "Food Listings":
            
            st.title("🍽️ Food Listings Dashboard")
            st.subheader("🍛 Claims per Food Item")
            show_data(lambda: query_db(st.session_state.queries["get_claims_per_food"]))
            st.subheader("🍽️ Most Claimed Meal Types")
            show_data(lambda: query_db(st.session_state.queries["get_top_meal_type"]))
            st.subheader("📊 Quantity Donated by Providers")
            show_data(lambda: query_db(st.session_state.queries["get_quantity_by_provider"]))
        elif tab == "Claims Analysis":
            
            st.title("📊 Claims Analysis Dashboard")
            st.subheader("✅ Top Receivers by Claims")
            show_data(lambda: query_db(st.session_state.queries["get_top_receivers"]))
            st.subheader("📈 Provider with Most Completed Claims")
            show_data(lambda: query_db(st.session_state.queries["get_top_provider_by_claims"])) # getting error here
            st.subheader("📊 Claim Status Distribution")
            show_data(lambda: query_db(st.session_state.queries["get_claim_status_distribution"]))
            st.subheader("📉 Average Claim Quantity by Receiver")
            show_data(lambda: query_db(st.session_state.queries["get_avg_claim_quantity"]))
        elif tab == "Contacts":
            st.title("📞 Contacts Dashboard")
            st.subheader("📋 Providers by City")
            show_data(lambda: query_db(st.session_state.queries["get_providers_by_city"]))
        elif tab == "Manage Food Listings":
            manage_food_listings()
            pass





st.session_state.queries = {
    "get_providers_receivers_by_city": """
        SELECT Providers.City, COUNT(DISTINCT Providers.Provider_ID) AS Providers,
        (SELECT COUNT(*) FROM Receivers WHERE Receivers.City = Providers.City) AS Receivers
        FROM Providers
        JOIN Food_Listings ON Food_Listings.Provider_ID = Providers.Provider_ID
        WHERE 1 = 1 {}
        GROUP BY Providers.City
    """,

    "get_top_provider_type": """
        SELECT Food_Listings.Provider_Type, COUNT(*) AS Total
        FROM Food_Listings
        JOIN Providers ON Food_Listings.Provider_ID = Providers.Provider_ID
        WHERE 1 = 1 {}
        GROUP BY Food_Listings.Provider_Type
        ORDER BY Total DESC
    """,

    "get_providers_by_city": """
        SELECT Providers.Name, Providers.Type, Providers.Address, Providers.City, Providers.Contact
        FROM Providers
        JOIN Food_Listings ON Food_Listings.Provider_ID = Providers.Provider_ID
        WHERE 1 = 1 {}
    """,

    "get_top_receivers": """
        SELECT Receivers.Name, COUNT(Claims.Claim_ID) AS Total_Claims
        FROM Claims
        JOIN Food_Listings ON Claims.Food_ID = Food_Listings.Food_ID
        JOIN Providers ON Food_Listings.Provider_ID = Providers.Provider_ID
        JOIN Receivers ON Claims.Receiver_ID = Receivers.Receiver_ID
        WHERE 1 = 1 {}
        GROUP BY Receivers.Name
        ORDER BY Total_Claims DESC
    """,

    "get_total_food_quantity": """
        SELECT SUM(Food_Listings.Quantity) AS Total_Quantity
        FROM Food_Listings
        JOIN Providers ON Food_Listings.Provider_ID = Providers.Provider_ID
        WHERE 1 = 1 {}
    """,

    "get_top_city_by_listings": """
        SELECT Food_Listings.Location AS City, COUNT(*) AS Listings
        FROM Food_Listings
        JOIN Providers ON Food_Listings.Provider_ID = Providers.Provider_ID
        WHERE 1 = 1 {}
        GROUP BY Food_Listings.Location
        ORDER BY Listings DESC
    """,

    "get_common_food_types": """
        SELECT Food_Listings.Food_Type, COUNT(*) AS Count
        FROM Food_Listings
        JOIN Providers ON Food_Listings.Provider_ID = Providers.Provider_ID
        WHERE 1 = 1 {}
        GROUP BY Food_Listings.Food_Type
        ORDER BY Count DESC
    """,

    "get_claims_per_food": """
        SELECT Food_Listings.Food_Name, COUNT(Claims.Claim_ID) AS Claims
        FROM Claims
        JOIN Food_Listings ON Claims.Food_ID = Food_Listings.Food_ID
        JOIN Providers ON Food_Listings.Provider_ID = Providers.Provider_ID
        JOIN Receivers ON Claims.Receiver_ID = Receivers.Receiver_ID
        WHERE 1 = 1 {}
        GROUP BY Food_Listings.Food_Name
        ORDER BY Claims DESC
    """,

    "get_top_provider_by_claims": """
        SELECT Providers.Name, COUNT(Claims.Claim_ID) AS Successful_Claims
        FROM Claims
        JOIN Food_Listings ON Claims.Food_ID = Food_Listings.Food_ID
        JOIN Providers ON Food_Listings.Provider_ID = Providers.Provider_ID
        JOIN Receivers ON Claims.Receiver_ID = Receivers.Receiver_ID
        WHERE Claims.Status = 'Completed' {}
        GROUP BY Providers.Name
        ORDER BY Successful_Claims DESC
    """,

    "get_claim_status_distribution": """
        SELECT Claims.Status, COUNT(*) AS Count
        FROM Claims
        JOIN Food_Listings ON Claims.Food_ID = Food_Listings.Food_ID
        JOIN Providers ON Food_Listings.Provider_ID = Providers.Provider_ID
        JOIN Receivers ON Claims.Receiver_ID = Receivers.Receiver_ID
        WHERE 1 = 1 {}
        GROUP BY Claims.Status
    """,

    "get_avg_claim_quantity": """
        SELECT Receivers.Name, AVG(Food_Listings.Quantity) AS Avg_Quantity
        FROM Claims
        JOIN Food_Listings ON Claims.Food_ID = Food_Listings.Food_ID
        JOIN Providers ON Food_Listings.Provider_ID = Providers.Provider_ID
        JOIN Receivers ON Claims.Receiver_ID = Receivers.Receiver_ID
        WHERE 1 = 1 {}
        GROUP BY Receivers.Name
        ORDER BY Avg_Quantity DESC
    """,

    "get_top_meal_type": """
        SELECT Meal_Type, COUNT(*) AS Total_Claims
        FROM Claims
        JOIN Food_Listings ON Claims.Food_ID = Food_Listings.Food_ID
        JOIN Providers ON Food_Listings.Provider_ID = Providers.Provider_ID
        WHERE 1 = 1 {}
        GROUP BY Meal_Type
        ORDER BY Total_Claims DESC
    """,

    "get_quantity_by_provider": """
        SELECT Providers.Name, SUM(Food_Listings.Quantity) AS Total_Quantity
        FROM Food_Listings
        JOIN Providers ON Food_Listings.Provider_ID = Providers.Provider_ID
        WHERE 1 = 1 {}
        GROUP BY Providers.Name
        ORDER BY Total_Quantity DESC
    """
}





# st.session_state.queries["get_providers_receivers_by_city"]
st.session_state.filters = ""


# pre login
def pre_login():
    st.set_page_config(page_title="Sign In", layout="wide")
    st.title("Sign In To Data Warehouse")
    st.markdown("Connect food donors with those in need to reduce food waste.")

    if st.button("🔑 Sign In to Data Warehouse"):
        sign_in()
        st.rerun()
        #st.session_state.logged_in = True

def signed_in():
    if "logged_in" in st.session_state :
        logged_in = st.session_state.logged_in
        connection_string = st.session_state.connection_string
        attrs = st.session_state.attrs
        #print(f"Logged in: {logged_in}, Connection String: {connection_string}, Attributes: {attrs}")
        post_login()
    else:
            pre_login()
            


# Main execution
if __name__ == "__main__":
    signed_in()
