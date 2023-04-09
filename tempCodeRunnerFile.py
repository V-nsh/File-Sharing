
    if request.method == 'POST':
        fi = request.files['text_f']
        data = request.files['text_f'].read()