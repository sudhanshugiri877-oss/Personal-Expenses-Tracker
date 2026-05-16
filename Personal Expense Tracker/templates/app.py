@app.route("/delete/<int:id>")
def delete(id):

    expense = Expense.query.get(id)

    db.session.delete(expense)

    db.session.commit()

    return redirect("/dashboard")
if __name__ == "__main__":