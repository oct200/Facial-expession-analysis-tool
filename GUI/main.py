from random import randint
import streamlit as st
import os

from UI.GUIClass import GraphicalUI


def main():
    gui = GraphicalUI()
    gui.initVariabile()
    gui.run()



main()