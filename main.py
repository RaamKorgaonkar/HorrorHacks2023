import streamlit as st
import random
import json
import qrcode
from io import BytesIO

# Define the User class
class User:
    def __init__(self, name, initial_balance=1000):
        self.name = name
        self.balance = initial_balance
        self.unique_code = self.generate_unique_code()
        self.password = self.generate_password()

    def generate_unique_code(self):
        return str(random.randint(10000000, 99999999))

    def generate_password(self):
        return str(random.randint(10000000, 99999999))

    def to_dict(self):
        return {
            "name": self.name,
            "balance": self.balance,
            "unique_code": self.unique_code,
            "password": self.password,
        }

    @classmethod
    def from_dict(cls, data):
        name = data.get("name", "User")
        user = cls(name, data.get("balance", 1000))
        user.unique_code = data["unique_code"]
        user.password = data["password"]
        return user

# Define the Bank class
class Bank:
    def __init__(self):
        self.users = {}
        self.current_user = None
        self.load_users_data()

    def load_users_data(self):
        try:
            with open("users.json", "r") as file:
                data = json.load(file)
                for user_data in data:
                    user = User.from_dict(user_data)
                    self.users[user.unique_code] = user
        except FileNotFoundError:
            pass

    def save_users_data(self):
        data = [user.to_dict() for user in self.users.values()]
        with open("users.json", "w") as file:
            json.dump(data, file)

    def create_user(self, name):
        user = User(name)
        self.users[user.unique_code] = user
        st.write(f"User {user.name} created with a unique code: {user.unique_code}")
        st.write(f"Your 8-digit password: {user.password}")
        self.save_users_data()

    def login(self, unique_code, password):
        user = self.users.get(unique_code)
        if user and user.password == password:
            self.current_user = user
            return user
        return None

    def logout(self):
        self.current_user = None

    def send_funds(self, sender_code, recipient_code, amount):
        st.toast("function begins")
        sender = self.users.get(sender_code)
        st.toast("sender confirmed")
        recipient = self.users.get(recipient_code)
        st.toast("recipient confirmed")

        if sender and recipient:
            if amount <= sender.balance:
                sender.balance -= amount
                recipient.balance += amount
                self.save_users_data()  # Save user data to update account info
                st.success("Funds sent successfully.")
                st.write(f"Your current balance: ${sender.balance:.2f}")
            else:
                st.error("Insufficient funds.")
        else:
            st.error("Sender or recipient not found.")

# Define the generate_qr_code function
def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=6,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert the QR code image to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    return img_bytes

# Main function
def main():
    bank = Bank()

    st.set_page_config(page_title="CryptoCandy", page_icon="🍬")

    if 'user' not in st.session_state:
        st.session_state.user = None

    col1, col2, col3 = st.columns(3)

    with col2:
        st.title("CryptoCandy")

    if not st.session_state.user:
        col1, col2, col3 = st.columns(3)

        with col2:
            st.text("To signup, send an e-mail to raam.korgaonkar1234@gmail.com")
            st.divider()
            unique_code = st.text_input("Unique Code:")
            password = st.text_input("Password:", type="password")

            if st.button("Log In"):
                user = bank.login(unique_code, password)
                if user:
                    st.session_state.user = user
                    st.toast(f"Logged in as {user.name}.")
                else:
                    st.toast("Invalid credentials. Log in failed")
            st.divider()

    if st.session_state.user:
        st.toast(f"Welcome, {st.session_state.user.name}!")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"Name: {st.session_state.user.name}", unsafe_allow_html=True)

        with col2:
            st.markdown(f"Unique Code: {st.session_state.user.unique_code}", unsafe_allow_html=True)

        with col3:
            st.markdown(f"Balance: ${st.session_state.user.balance:.2f}", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            # Convert the QR code image to bytes
            qr_bytes = generate_qr_code(st.session_state.user.unique_code)
            st.image(qr_bytes, caption="Your QR Code")  # Make QR code responsive

        with col2:
            st.subheader("Send Funds:")
            recipient_code = st.text_input("Recipient's Unique Code:")
            st.toast("Recipient Data Inputed")
            amount = st.number_input("Amount to Send:", 0.0, st.session_state.user.balance, 0.0)
            st.toast("Amount Inputed")
            confirm_payment = st.checkbox("Confirm Payment")
            st.toast("Payment confirmed")

            if confirm_payment:
                sender_code = st.session_state.user.unique_code  # Get sender's unique code
                bank.send_funds(sender_code, recipient_code, amount)
                st.toast("Transfer successful")

    if st.button("Log Out"):
        bank.logout()
        st.session_state.user = None
        st.success("Logged out successfully")

if __name__ == "__main__":
    main()

