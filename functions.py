from flask import Flask, flash, redirect, render_template, request, session

def login_required(id):
    if id is None:
        return redirect("/login")