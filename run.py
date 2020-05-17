from app import create_app
app = create_app('DEBUGGING')
app.run(debug=True,host = '127.0.0.1',port=5001)
