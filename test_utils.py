from utils import get_exchange_rates

def test_get_exchange_rates():
    rates = get_exchange_rates()

    # Проверка, что результат — это словарь
    assert isinstance(rates, dict), "Ожидался словарь с курсами валют"

    # Проверка, что в словаре есть ключ 'USD'
    assert 'USD' in rates, "В курсах должен быть доллар (USD)"

    # Проверка, что все значения — числа
    for code, rate in rates.items():
        assert isinstance(rate, (float, int)), f"Курс {code} должен быть числом"

    print("✅ Тест пройден успешно.")
    print("Пример курсов:", rates)

if __name__ == "__main__":
    test_get_exchange_rates()
