from datetime import datetime
import streamlit as st


def app():
    st.title("Order Status")
    st.write("Enter your order details here:")
        
    # Initialize the form data in session state if it doesn't exist
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {
            'name': "",
            'order_id': 1000,
            'date': datetime.now().date(),
            'action': "Cancel Order",
            'mult_order': False,
            'order_qty': 1
        }

    # Get the form data from session state  
    user_name = st.text_input("Enter your name")
    order_id = st.number_input("Enter your order id", min_value=1000, max_value=9999, step=1)
    today_date = st.date_input("Enter today's date", format="YYYY/MM/DD", value=datetime.now().date())
    action = st.selectbox("Select an action", ["Cancel Order", "Reject Order", "Show Status"])
    mult_order= st.checkbox("Is this a multiple item order?")
    order_qty = st.slider("Enter the quantity of items in the order", min_value=1, max_value=100, step=1)


    #Add a Save button
    if st.button("Save Values"):
        # Check required fields
        required_fields = {
            'name': user_name,
            'order_id': order_id,
            'date': today_date,
        }

        missing_fields = [field for field, value in required_fields.items() 
                        if not value or (isinstance(value, str) and value.strip() == "")]
        
        if missing_fields:
            st.error(f"Please fill in all required fields: {', '.join(missing_fields)}")
        else:
            st.session_state.form_data = {
                'name': user_name,
                'order_id': order_id,
                'date': today_date,
                'action': action,
                'mult_order': mult_order,
                'order_qty': order_qty
            }
            st.success("Values saved successfully!")
            
    if user_name:
        st.markdown(
            f"""
            * User Name: {user_name}
            * Order ID: {order_id}
            * Today's Date: {today_date}
            * Action: {action}
            * Multiple Order: {mult_order}
            * Order Quantity: {order_qty}   
            """
        )
