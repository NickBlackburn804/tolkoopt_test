import asyncio
from decimal import ROUND_DOWN, Decimal


async def recommend_price(fetch_offers, current_price, min_price, timeout_s=2.0):
    def hold(reason):
        return {
            "price": current_price,
            "decision": "HOLD",
            "reason": reason,
        }

    # Получение данных с ограничением времени ожидания
    try:
        result = await asyncio.wait_for(
            fetch_offers(),
            timeout=timeout_s,
        )
    except asyncio.TimeoutError:
        return hold("Истекло время ожидания источника")
    except Exception:
        return hold("Ошибка при получении предложений")

    # Проверка статуса источника
    if result["status"] != "success":
        return hold("Источник вернул неполные или ошибочные данные")

    # Отбор подходящих предложений
    offers = [
        offer["price"]
        for offer in result["offers"]
        if offer["seller"].casefold() != "myshop"
        and offer["delivery_days"] is not None
        and offer["delivery_days"] <= 6
    ]

    if not offers:
        return hold("Нет подходящих предложений конкурентов")

    # Расчёт рекомендованной цены
    competitor_price = min(offers)

    discounted_price = (competitor_price * Decimal("0.985")).quantize(
        Decimal("0.01"), rounding=ROUND_DOWN
    )

    recommended_price = max(discounted_price, min_price)

    # Проверка отклонения от текущей цены
    deviation = abs(recommended_price - current_price) / current_price

    if deviation > Decimal("0.30"):
        decision = "REVIEW"
        reason = "Изменение цены превышает 30%, требуется проверка"
    else:
        decision = "APPLY"
        reason = "Найдена подходящая цена конкурента"

    return {
        "price": recommended_price,
        "decision": decision,
        "reason": reason,
    }


async def sample_fetch_offers():
    return {
        "status": "success",
        "offers": [
            {"seller": "myshop", "price": Decimal("4300.00"), "delivery_days": 2},
            {"seller": "PARTS", "price": Decimal("4800.00"), "delivery_days": 3},
            {"seller": "SLOW", "price": Decimal("4700.00"), "delivery_days": 8},
        ],
    }


if __name__ == "__main__":
    print(
        asyncio.run(
            recommend_price(
                sample_fetch_offers,
                current_price=Decimal("4900.00"),
                min_price=Decimal("4500.00"),
            )
        )
    )
