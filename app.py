import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(page_title="CRUD Application", layout="wide")
st.title("📊 SQLite CRUD Application")

# ============================================================================
# DATABASE SETUP AND FUNCTIONS
# ============================================================================

DATABASE_FILE = "data.db"

def init_database():
    """
    Initialize the SQLite database and create the table if it doesn't exist.
    This function is called on app startup.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Create users table with columns: id, name, email, phone, age, date_created
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            age INTEGER,
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

def get_connection():
    """
    Create and return a database connection.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

# ============================================================================
# CREATE OPERATION
# ============================================================================

def insert_user(name, email, phone, age):
    """
    Insert a new user into the database.
    
    Args:
        name (str): User's name
        email (str): User's email
        phone (str): User's phone number
        age (int): User's age
    
    Returns:
        bool: True if insertion was successful, False otherwise
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO users (name, email, phone, age)
            VALUES (?, ?, ?, ?)
        """, (name, email, phone, age))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error inserting user: {e}")
        return False

# ============================================================================
# READ OPERATION
# ============================================================================

def view_all_users():
    """
    Retrieve all users from the database.
    
    Returns:
        DataFrame: A pandas DataFrame containing all users
    """
    try:
        conn = get_connection()
        query = "SELECT id, name, email, phone, age, date_created FROM users ORDER BY id DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error retrieving users: {e}")
        return pd.DataFrame()

def get_user_by_id(user_id):
    """
    Retrieve a single user by ID.
    
    Args:
        user_id (int): The ID of the user to retrieve
    
    Returns:
        tuple: User data tuple (id, name, email, phone, age, date_created)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user
    except Exception as e:
        st.error(f"Error retrieving user: {e}")
        return None

def get_user_ids():
    """
    Retrieve all user IDs for selectbox options.
    
    Returns:
        list: List of tuples (id, name) for easy display
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM users ORDER BY id DESC")
        users = cursor.fetchall()
        conn.close()
        return [(user[0], user[1]) for user in users]
    except Exception as e:
        st.error(f"Error retrieving user list: {e}")
        return []

# ============================================================================
# UPDATE OPERATION
# ============================================================================

def update_user(user_id, name, email, phone, age):
    """
    Update an existing user's information.
    
    Args:
        user_id (int): The ID of the user to update
        name (str): Updated name
        email (str): Updated email
        phone (str): Updated phone
        age (int): Updated age
    
    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users
            SET name = ?, email = ?, phone = ?, age = ?
            WHERE id = ?
        """, (name, email, phone, age, user_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error updating user: {e}")
        return False

# ============================================================================
# DELETE OPERATION
# ============================================================================

def delete_user(user_id):
    """
    Delete a user from the database.
    
    Args:
        user_id (int): The ID of the user to delete
    
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error deleting user: {e}")
        return False

# ============================================================================
# STREAMLIT UI
# ============================================================================

# Initialize database on app startup
init_database()

# Create tabs for different operations
tab1, tab2, tab3, tab4 = st.tabs(["➕ Create", "📋 Read", "✏️ Update", "🗑️ Delete"])

# ======================== CREATE TAB ========================
with tab1:
    st.header("Add New User")
    
    with st.form("add_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", placeholder="Enter full name")
            email = st.text_input("Email", placeholder="Enter email address")
        
        with col2:
            phone = st.text_input("Phone Number", placeholder="Enter phone number")
            age = st.number_input("Age", min_value=1, max_value=120, value=25)
        
        # Submit button
        submitted = st.form_submit_button("➕ Add User", use_container_width=True)
        
        if submitted:
            # Validation
            if not name or not email or not phone:
                st.error("❌ Please fill in all fields!")
            elif "@" not in email:
                st.error("❌ Please enter a valid email address!")
            else:
                # Insert the user
                if insert_user(name, email, phone, age):
                    st.success(f"✅ User '{name}' added successfully!")
                else:
                    st.error("❌ Failed to add user!")

# ======================== READ TAB ========================
with tab2:
    st.header("View All Users")
    
    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()
    
    # Retrieve and display all users
    users_df = view_all_users()
    
    if users_df.empty:
        st.info("📭 No users found. Add one using the 'Create' tab!")
    else:
        st.subheader(f"Total Users: {len(users_df)}")
        
        # Display as dataframe with formatting
        st.dataframe(
            users_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": st.column_config.NumberColumn("ID", width="small"),
                "name": st.column_config.TextColumn("Name", width="medium"),
                "email": st.column_config.TextColumn("Email", width="medium"),
                "phone": st.column_config.TextColumn("Phone", width="small"),
                "age": st.column_config.NumberColumn("Age", width="small"),
                "date_created": st.column_config.TextColumn("Created", width="medium"),
            }
        )

# ======================== UPDATE TAB ========================
with tab3:
    st.header("Update User Information")
    
    # Get list of users
    user_list = get_user_ids()
    
    if not user_list:
        st.info("📭 No users found. Add one using the 'Create' tab!")
    else:
        # Select user to update
        selected_option = st.selectbox(
            "Select a user to update:",
            options=user_list,
            format_func=lambda x: f"{x[1]} (ID: {x[0]})"
        )
        
        selected_user_id = selected_option[0]
        user_data = get_user_by_id(selected_user_id)
        
        if user_data:
            st.info(f"Editing: **{user_data[1]}** (ID: {user_data[0]})")
            
            with st.form("update_user_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    updated_name = st.text_input("Full Name", value=user_data[1])
                    updated_email = st.text_input("Email", value=user_data[2])
                
                with col2:
                    updated_phone = st.text_input("Phone Number", value=user_data[3])
                    updated_age = st.number_input("Age", min_value=1, max_value=120, value=user_data[4])
                
                # Submit button
                submit_update = st.form_submit_button("✅ Save Changes", use_container_width=True)
                
                if submit_update:
                    # Validation
                    if not updated_name or not updated_email or not updated_phone:
                        st.error("❌ Please fill in all fields!")
                    elif "@" not in updated_email:
                        st.error("❌ Please enter a valid email address!")
                    else:
                        # Update the user
                        if update_user(selected_user_id, updated_name, updated_email, updated_phone, updated_age):
                            st.success(f"✅ User updated successfully!")
                        else:
                            st.error("❌ Failed to update user!")

# ======================== DELETE TAB ========================
with tab4:
    st.header("Delete User")
    
    # Get list of users
    user_list = get_user_ids()
    
    if not user_list:
        st.info("📭 No users found. Add one using the 'Create' tab!")
    else:
        # Select user to delete
        selected_option = st.selectbox(
            "Select a user to delete:",
            options=user_list,
            format_func=lambda x: f"{x[1]} (ID: {x[0]})",
            key="delete_select"
        )
        
        selected_user_id = selected_option[0]
        selected_user_name = selected_option[1]
        
        # Display confirmation
        st.warning(f"⚠️ You are about to delete: **{selected_user_name}** (ID: {selected_user_id})")
        st.write("This action cannot be undone!")
        
        # Delete button with confirmation
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Delete User", use_container_width=True, type="primary"):
                if delete_user(selected_user_id):
                    st.success(f"✅ User '{selected_user_name}' deleted successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to delete user!")
        
        with col2:
            st.button("❌ Cancel", use_container_width=True)

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Export to CSV", use_container_width=True):
        df = view_all_users()
        if not df.empty:
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No data to export!")

with col2:
    db_stats = view_all_users()
    st.metric("Total Records", len(db_stats))

with col3:
    st.info(f"📁 Database: `{DATABASE_FILE}`")
