"""
Author: Karim Elkholy

Page Object classes for the LambdaTest E-Commerce Playground.
"""
from pages.account_page import AccountPage
from pages.base_page import BasePage
from pages.cart_page import CartPage
from pages.category_page import CategoryPage
from pages.change_password_page import ChangePasswordPage
from pages.contact_page import ContactPage
from pages.edit_account_page import EditAccountPage
from pages.forgotten_password_page import ForgottenPasswordPage
from pages.login_page import LoginPage
from pages.product_page import ProductPage
from pages.register_page import RegisterPage
from pages.search_page import SearchPage

__all__ = [
    "BasePage",
    "LoginPage",
    "RegisterPage",
    "AccountPage",
    "CartPage",
    "ProductPage",
    "SearchPage",
    "ContactPage",
    "CategoryPage",
    "ForgottenPasswordPage",
    "ChangePasswordPage",
    "EditAccountPage",
]
