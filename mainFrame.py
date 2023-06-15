import translator

while True:
    text = input('pseudo > ')
    result, error = translator.run(text)

    if error: print(error.as_string())
    else: print(result)