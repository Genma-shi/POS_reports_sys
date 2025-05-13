import requests

def get_exchange_rates():
    url = "https://data.fx.kg/api/v1/central"
    headers = {
        "Authorization": "Bearer W5zhYJsTMYREYJd6ILGN6fo3WZekBFLpvqXAQAz0ed19cb01"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("DEBUG: Ответ от API:", data)  # можешь убрать позже
        rates = {}
        for key, value in data.items():
            if key.isalpha() and len(key) == 3:  # фильтруем валютные коды
                rates[key.upper()] = float(value)
        return rates
    else:
        print("Ошибка при получении данных", response.status_code)
        return {}
