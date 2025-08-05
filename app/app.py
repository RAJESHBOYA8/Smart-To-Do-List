@app.route('/add', methods=['POST'])
def add_task():
    content = request.form['content']
    priority = request.form['priority']
    due_date_str = request.form['due_date']

    due_date = None
    if due_date_str:
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()

    new_task = Task(content=content, priority=priority, due_date=due_date)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('todo_list'))